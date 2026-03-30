import machine, os, time, json
from init_sensors import Init_Sensors
from init_motor import Init_Motor
from init_sd_rtc import Init_SD_RTC
from aux.create_config import create_config_file
from prototypes import logging_error
import components.rtc as rtc
import components.ssd1306 as ssd1306
from aux.client import TransmitData
from aux.validate_config import validate_config
from machine import Pin, SoftI2C, WDT
import gc

# --------------- Helper functions ---------------

def display_msg(display, *lines):
    """Show up to 6 lines of text on the OLED (10px spacing each)."""
    display.fill(0)
    for i, line in enumerate(lines):
        display.text(str(line), 0, i * 10)
    display.show()


def display_status(display, title, components):
    """Show a boot checklist on the OLED.

    *components* is a dict of {name: status} where status is one of
    'OK', 'FAIL', '...' (pending), or any short string.
    The title is shown on the first line; components fill the rest.
    """
    display.fill(0)
    display.text(title, 0, 0)
    for i, (name, status) in enumerate(components.items()):
        if i >= 5:  # max 5 rows below the title
            break
        tag = 'x' if status == 'OK' else ('!' if status == 'FAIL' else ' ')
        display.text(f'[{tag}] {name}: {status}', 0, 12 + i * 10)
    display.show()


def wait_with_wdt(wdt, seconds, display=None, msg=None):
    """Sleep for *seconds* while feeding the watchdog every second."""
    for s in range(seconds):
        wdt.feed()
        time.sleep(1)
        if display and msg:
            display_msg(display, f'{msg} {s + 1}/{seconds}')


def fmt_dt(dt):
    """Return 'YYYY-MM-DD_HH-MM-SS' from an RTC datetime object."""
    return f'{dt.year}-{dt.month:02}-{dt.day:02}_{dt.hour:02}-{dt.minute:02}-{dt.second:02}'


def fmt_dt_utc(dt):
    """Return 'YYYY-MM-DD HH:MM:SS' from an RTC datetime object."""
    return f'{dt.year}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}'


def ensure_dir(path):
    """Create directory if it does not exist."""
    try:
        os.mkdir(path)
    except OSError:
        pass  # already exists


def _write_array(f, arr, chunk=10):
    """Write a list to an open file in chunks to avoid large allocations."""
    f.write('[')
    for i in range(0, len(arr), chunk):
        seg = json.dumps(arr[i:i + chunk])
        if i > 0:
            f.write(',')
        # strip outer brackets from segment
        f.write(seg[1:-1])
    f.write(']')


def save_measurement(filepath, data_dict, wdt=None):
    """Write {"raw_data": {key: [...], ...}} to *filepath* atomically.

    Writes to a .tmp file first, then renames. If power is lost during
    the write the .tmp file will be cleaned up on next boot.
    Each array is serialised in small chunks so the full JSON string
    is never held in RAM at once.  Arrays are freed from data_dict
    progressively to reclaim RAM during the write.
    """
    tmp_path = filepath + '.tmp'
    with open(tmp_path, 'w') as f:
        f.write('{"raw_data":{')
        first = True
        keys = list(data_dict.keys())
        for key in keys:
            if wdt:
                wdt.feed()
            if not first:
                f.write(',')
            f.write(json.dumps(key))
            f.write(':')
            _write_array(f, data_dict[key])
            first = False
            # Free this array now to reclaim RAM for the next one
            del data_dict[key]
            gc.collect()
        f.write('}}')
    os.rename(tmp_path, filepath)


def check_memory():
    """Return True if memory is healthy (>10 KB free)."""
    free = gc.mem_free()
    if free < 10240:
        logging_error.log_exception_to_file(
            f"Low memory warning: {free} bytes free", '/sd/error.log')
        return False
    return True


def force_gc():
    """Force garbage collection."""
    gc.collect()


def cleanup_tmp_files(base_dir):
    """Remove leftover .tmp files from interrupted writes."""
    try:
        for entry in os.listdir(base_dir):
            full = f'{base_dir}/{entry}'
            try:
                # Check if it's a directory
                os.listdir(full)
                cleanup_tmp_files(full)
            except OSError:
                # It's a file
                if entry.endswith('.tmp'):
                    os.remove(full)
                    print(f'Cleaned up: {full}')
    except OSError:
        pass  # base_dir doesn't exist yet


def check_sd_space(path='/sd', min_bytes=1048576):
    """Return True if at least *min_bytes* are free on the filesystem."""
    try:
        stat = os.statvfs(path)
        free_bytes = stat[0] * stat[3]  # f_bsize * f_bavail
        if free_bytes < min_bytes:
            logging_error.log_exception_to_file(
                f"SD card low space: {free_bytes} bytes free", '/sd/error.log')
            return False
        return True
    except OSError:
        return False


def write_heartbeat(clock_rtc, cycle, co2_first=None, co2_last=None,
                    path='/sd/heartbeat.log'):
    """Append a heartbeat entry with timestamp, memory, and CO2 range."""
    try:
        free = gc.mem_free()
        if clock_rtc is not None:
            dt = clock_rtc.datetime()
            ts = f'{dt.year}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}'
        else:
            t = time.localtime()
            ts = f'{t[0]}-{t[1]:02}-{t[2]:02} {t[3]:02}:{t[4]:02}:{t[5]:02}'
        with open(path, 'a') as f:
            f.write(f'[{ts}] cycle={cycle} mem_free={free} CO2={co2_first}-{co2_last}\n')
    except Exception as e:
        print(f'Heartbeat write failed: {e}')


def write_boot_entry(clock_rtc, path='/sd/heartbeat.log'):
    """Append a BOOT entry with reset cause."""
    try:
        cause = machine.reset_cause()
        causes = {0: 'PWRON', 1: 'HARD', 2: 'WDT', 3: 'DEEPSLEEP', 4: 'SOFT'}
        cause_str = causes.get(cause, f'UNKNOWN({cause})')
        free = gc.mem_free()
        if clock_rtc is not None:
            dt = clock_rtc.datetime()
            ts = f'{dt.year}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}'
        else:
            t = time.localtime()
            ts = f'{t[0]}-{t[1]:02}-{t[2]:02} {t[3]:02}:{t[4]:02}:{t[5]:02}'
        with open(path, 'a') as f:
            f.write(f'[{ts}] BOOT reset_cause={cause_str} mem_free={free}\n')
    except Exception as e:
        print(f'Boot entry write failed: {e}')


def read_boot_count(path='/sd/boot_count.txt'):
    """Read and increment the boot counter. Returns new count."""
    count = 0
    try:
        with open(path, 'r') as f:
            count = int(f.read().strip())
    except Exception:
        pass
    count += 1
    try:
        with open(path, 'w') as f:
            f.write(str(count))
    except Exception:
        pass
    return count


def init_sensor_with_retry(wdt, init_fn, i2c_addr, bus, name,
                          retries=5, display=None, status_dict=None):
    """Try to initialise a sensor up to *retries* times, verifying via I2C scan."""
    sensor = None
    for attempt in range(1, retries + 1):
        wdt.feed()
        if status_dict is not None:
            status_dict[name] = f'{attempt}/{retries}'
            if display:
                display_status(display, '== SENSORS ==', status_dict)
        try:
            sensor = init_fn()
            if i2c_addr in bus.scan():
                print(f'{name} ok')
                return sensor
        except Exception as e:
            print(f'{name} error (attempt {attempt})', e)
        time.sleep(1)
    return sensor


# --------------- Boot ---------------

wdt = WDT(timeout=8000)
wdt.feed()

i2c_display = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, i2c_display)

# Component status tracker – displayed on OLED throughout boot
status = {
    'Config': '...',
    'SD':     '...',
    'RTC':    '...',
    'Motor':  '...',
    'Sensor': '...',
}

display_status(display, '== BOOT ==', status)
gc.collect()

# --- Load config ---
os.chdir('/')
try:
    with open('config.json', 'r') as f:
        config = json.loads(f.read())
    status['Config'] = 'OK'
except Exception:
    print('config.json not found, creating default')
    create_config_file()
    try:
        with open('config.json', 'r') as f:
            config = json.loads(f.read())
        status['Config'] = 'NEW'
    except Exception as e:
        status['Config'] = 'FAIL'
        print('Config error', e)

display_status(display, '== BOOT ==', status)
wdt.feed()

# --- Validate config ---
if status['Config'] != 'FAIL':
    config_errors = validate_config(config)
    if config_errors:
        for err in config_errors:
            print(f'Config: {err}')
        display_msg(display, 'CONFIG ERROR', *config_errors[:4])
        status['Config'] = 'INVALID'
    else:
        print('Config validated OK')
display_status(display, '== BOOT ==', status)
wdt.feed()

print(config)

# --- WiFi / transmit ---
transmit = TransmitData(
    ssid="name12", password="password",
    server_ip="192.168.4.1", server_port=80, wdt_obj=wdt)
transmit.send_simple_data(id=config['id_sensor'], datatype='Starting', data=None)

# --- GPIO ---
b1 = Pin(config['buttons']['button01'], Pin.IN, Pin.PULL_DOWN)
b2 = Pin(config['buttons']['button02'], Pin.IN, Pin.PULL_DOWN)
b3 = Pin(config['buttons']['button03'], Pin.IN, Pin.PULL_DOWN)

relay01 = Pin(config['relays']['relay01'], Pin.OUT)
relay02 = Pin(config['relays']['relay02'], Pin.OUT)

# --- SD card (up to 5 retries) ---
SD_RETRIES = 5
sd_rtc_component = Init_SD_RTC()
sd = None
for attempt in range(1, SD_RETRIES + 1):
    wdt.feed()
    status['SD'] = f'{attempt}/{SD_RETRIES}'
    display_status(display, '== BOOT ==', status)
    try:
        sd = sd_rtc_component.set_SDCard()
        status['SD'] = 'OK'
        break
    except Exception as e:
        print(f'SD error (attempt {attempt})', e)
        if attempt == SD_RETRIES:
            status['SD'] = 'FAIL'
        time.sleep(1)

display_status(display, '== BOOT ==', status)
wdt.feed()

# Clean up incomplete writes from previous power loss
cleanup_tmp_files('/sd/data')

# --- RTC (up to 5 retries) ---
RTC_RETRIES = 5
clock_rtc = None
for attempt in range(1, RTC_RETRIES + 1):
    wdt.feed()
    status['RTC'] = f'{attempt}/{RTC_RETRIES}'
    display_status(display, '== BOOT ==', status)
    try:
        clock_rtc = sd_rtc_component.set_rtc()
        logging_error.set_rtc_clock(clock_rtc)

        # Sync DS1307 from config time (first boot via laptop), then disable sync
        if config['start_time']['sync']:
            sd_rtc_component.sync_rtc(clock_rtc)
            # Reload config since sync_rtc disabled the sync flag
            with open('/config.json', 'r') as f:
                config = json.loads(f.read())
            status['RTC'] = 'SYNCED'
        else:
            dt = clock_rtc.datetime()
            print('RTC time:', dt)
            status['RTC'] = fmt_dt_utc(dt)[11:]  # show HH:MM:SS
        break
    except Exception as e:
        print(f'RTC error (attempt {attempt})', e)
        if attempt == RTC_RETRIES:
            # Still assign clock_rtc so logging can attempt to work
            try:
                clock_rtc = sd_rtc_component.set_rtc()
                logging_error.set_rtc_clock(clock_rtc)
            except Exception:
                pass
            status['RTC'] = 'FAIL'
        time.sleep(1)

display_status(display, '== BOOT ==', status)
wdt.feed()
time.sleep(1)

# --- Boot tracking ---
boot_count = read_boot_count()
write_boot_entry(clock_rtc)
print(f'Boot #{boot_count}')

# --- Motor (up to 3 retries) ---
MOTOR_RETRIES = 3
motor = None
for attempt in range(1, MOTOR_RETRIES + 1):
    wdt.feed()
    status['Motor'] = f'{attempt}/{MOTOR_RETRIES}'
    display_status(display, '== BOOT ==', status)
    try:
        motor = Init_Motor()
        status['Motor'] = 'OK'
        break
    except Exception as e:
        print(f'Motor error (attempt {attempt})', e)
        if attempt == MOTOR_RETRIES:
            status['Motor'] = 'FAIL'
        time.sleep(1)

display_status(display, '== BOOT ==', status)
wdt.feed()

# --- Sensors ---
# Switch to detailed sensor view
sensor_status = {
    'BMP280': '...',
    'Si7021': '...',
    'K30':    '...',
}
display_status(display, '== SENSORS ==', sensor_status)

scl = Pin(config['i2c_sensor']['scl'])
sda = Pin(config['i2c_sensor']['sda'])
sensors = Init_Sensors()
bus = machine.I2C(0, scl=scl, sda=sda, freq=50000)

pressure_sensor = init_sensor_with_retry(
    wdt, sensors.set_PressureSensor, 118, bus, 'BMP280',
    display=display, status_dict=sensor_status)
sensor_status['BMP280'] = 'OK' if pressure_sensor else 'FAIL'
display_status(display, '== SENSORS ==', sensor_status)

temp_hum_sensor = init_sensor_with_retry(
    wdt, sensors.set_TempAndHumidity, 64, bus, 'Si7021',
    display=display, status_dict=sensor_status)
sensor_status['Si7021'] = 'OK' if temp_hum_sensor else 'FAIL'
display_status(display, '== SENSORS ==', sensor_status)

# K30 needs relay powered on + warm-up
relay01.value(1)
sensor_status['K30'] = 'warm'
display_status(display, '== SENSORS ==', sensor_status)
wait_with_wdt(wdt, 5)

co2_sensor = init_sensor_with_retry(
    wdt, sensors.set_k30, 104, bus, 'K30',
    display=display, status_dict=sensor_status)
sensor_status['K30'] = 'OK' if co2_sensor else 'FAIL'
display_status(display, '== SENSORS ==', sensor_status)
wdt.feed()

# Update top-level status
all_ok = all(v == 'OK' for v in sensor_status.values())
status['Sensor'] = 'OK' if all_ok else 'PARTIAL'

# --- Final boot summary ---
# Show combined summary for 3 seconds
display_status(display, '== READY ==', status)
time.sleep(3)
wdt.feed()

# Log any failures
_all_status = {}
_all_status.update(status)
_all_status.update(sensor_status)
boot_failures = [k for k, v in _all_status.items()
                 if v in ('FAIL', 'PARTIAL')]
if boot_failures:
    msg = f"Boot failures: {', '.join(boot_failures)}"
    print(msg)
    try:
        logging_error.log_exception_to_file(msg, '/sd/error.log')
    except Exception:
        pass

# --- Initial chamber opening ---
display_msg(display, 'Opening chamber...')
for _ in range(21):
    wdt.feed()
    motor.Rotate('open')
    time.sleep(1)
motor.Rotate('stop')
print('Finish initial opening')

# --------------- Main loop ---------------
max_close = config['timeLimits']['maxTime_chamber_CLOSE']
measurement_repeat = config['timeLimits']['measurement_repeat']
max_open = config['timeLimits']['maxTime_chamber_OPEN']
sensor_id = config['id_sensor']

print('Starting main loop')
cycle_count = 0
while True:
    wdt.feed()
    cycle_count += 1

    # Power on K30 relay
    relay01.value(1)
    for _ in range(5):
        wdt.feed()

    for n in range(1, measurement_repeat + 1):
        # --- Close chamber ---
        motor.Rotate('close')
        relay02.value(1)
        wait_with_wdt(wdt, 20, display, 'Closing')
        motor.Rotate('stop')

        gc.collect()

        # --- Prepare measurement ---
        if not check_memory():
            force_gc()

        start_dt = clock_rtc.datetime()
        if start_dt is not None:
            start_str = fmt_dt(start_dt)
            filename = f'{start_str}.json'
            folder_path = f'/sd/data/{start_dt.year}-{start_dt.month:02}-{start_dt.day:02}'
        else:
            start_str = 'RTC_ERROR'
            filename = f'{start_str}.json'
            folder_path = '/sd/data/ERROR'

        bmp_pres = []
        bmp_temp = []
        si_temp = []
        si_hum = []
        co2 = []
        dt_sec = []
        dt_utc = []

        max_samples = min(max_close, 1000)
        wdt.feed()

        # --- Sampling loop ---
        for sample in range(max_samples):
            wdt.feed()

            # Periodic memory check
            if sample % 10 == 0 and not check_memory():
                force_gc()
                if gc.mem_free() < 5120:
                    print('Critical memory — stopping early')
                    break

            # Read sensors with individual error handling
            clock_now = None
            try:
                clock_now = clock_rtc.datetime()
            except Exception as e:
                logging_error.log_exception_to_file(f"RTC: {e}", '/sd/error.log')

            pres_val = temp_bmp_val = None
            try:
                pres_val = pressure_sensor.pressure
                temp_bmp_val = pressure_sensor.temperature
            except Exception as e:
                logging_error.log_exception_to_file(f"BMP280: {e}", '/sd/error.log')

            si_t_val = si_h_val = None
            try:
                si_t_val = temp_hum_sensor.temperature()
                si_h_val = temp_hum_sensor.humidity()
            except Exception as e:
                logging_error.log_exception_to_file(f"Si7021: {e}", '/sd/error.log')

            co2_val = None
            try:
                co2_val = co2_sensor.read_value()
            except Exception as e:
                logging_error.log_exception_to_file(f"K30: {e}", '/sd/error.log')

            # Update display
            display.fill(0)
            display.text(f"T{n}:{sample}", 0, 0)
            display.text(f'CO2:{co2_val}', 0, 10)
            _p = f'{pres_val:.0f}' if pres_val is not None else '?'
            _bt = f'{temp_bmp_val:.1f}' if temp_bmp_val is not None else '?'
            display.text(f'P:{_p} BT:{_bt}', 0, 20)
            _st = f'{si_t_val:.1f}' if si_t_val is not None else '?'
            _sh = f'{si_h_val:.1f}' if si_h_val is not None else '?'
            display.text(f'ST:{_st} H:{_sh}', 0, 30)
            if clock_now is not None:
                display.text(f'{clock_now.year}-{clock_now.month:02}-{clock_now.day:02}', 0, 42)
                display.text(f'{clock_now.hour:02}:{clock_now.minute:02}:{clock_now.second:02}', 0, 52)
            else:
                display.text('RTC Error', 0, 42)
            display.show()

            # Append readings
            bmp_pres.append(pres_val)
            bmp_temp.append(temp_bmp_val)
            si_temp.append(si_t_val)
            si_hum.append(si_h_val)
            co2.append(co2_val)

            if clock_now is not None:
                dt_sec.append(rtc.tuple2seconds(clock_now))
                dt_utc.append(fmt_dt_utc(clock_now))
            else:
                dt_sec.append(0)
                dt_utc.append(f'RTC_ERROR_{sample}')

            time.sleep(1)

        # --- Save data ---
        wdt.feed()
        force_gc()

        # Grab CO2 range before save_measurement frees the arrays
        co2_first = co2[0] if co2 else None
        co2_last = co2[-1] if co2 else None

        data_dict = {
            'bmp_pressure': bmp_pres, 'bmp_temperature': bmp_temp,
            'si_temperature': si_temp, 'si_humidity': si_hum,
            'k30_co2': co2, 'datetime': dt_sec, 'datetime_utc': dt_utc,
        }
        # Drop local refs so save_measurement's del actually frees memory
        del bmp_pres, bmp_temp, si_temp, si_hum, co2, dt_sec, dt_utc

        ensure_dir('/sd/data')
        ensure_dir(folder_path)
        if not check_sd_space():
            print('SD card low space — skipping save')
        else:
            try:
                save_measurement(f'{folder_path}/{filename}', data_dict, wdt=wdt)
                print(f'{filename} saved')
                wdt.feed()
                transmit.send_simple_data(
                    id=sensor_id, datatype='Measurement',
                    data=f'CO2={co2_first}-{co2_last}')
            except Exception as e:
                print('File save error', e)
                logging_error.log_exception_to_file(
                    f"Failed to save {filename}: {e}", '/sd/error.log')

        del data_dict
        gc.collect()

        # Heartbeat
        write_heartbeat(clock_rtc, cycle_count, co2_first, co2_last)

        print('=== FINISHED MEASURING ===')

        # --- Open chamber ---
        motor.Rotate('open')
        wait_with_wdt(wdt, 20, display, 'Opening')
        motor.Rotate('stop')

        relay02.value(0)
        wait_with_wdt(wdt, 120, display, 'Wait inter')

    # --- Long open period between cycles ---
    relay01.value(0)
    wait_with_wdt(wdt, max_open, display, 'Full wait')
