import machine, os, time, json
from init_sensors import Init_Sensors
from init_motor import Init_Motor
from init_sd_rtc import Init_SD_RTC
from aux.create_config import create_config_file
from aux.chamber_position import ChamberPosition
from prototypes import logging_error
import components.rtc as rtc
import components.ssd1306 as ssd1306
from aux.client import TransmitData
from machine import I2C, Pin, SoftI2C, WDT
import gc

def check_memory():
    """Check available memory and log if low"""
    free_mem = gc.mem_free()
    alloc_mem = gc.mem_alloc()
    total_mem = free_mem + alloc_mem
    
    print(f"Memory - Free: {free_mem}, Allocated: {alloc_mem}, Total: {total_mem}")
    
    # Log warning if memory is low (less than 10KB free)
    if free_mem < 10240:
        logging_error.log_exception_to_file(f"Low memory warning: {free_mem} bytes free", '/sd/error.log')
        return False
    return True

def force_gc_collection():
    """Force garbage collection and return freed memory"""
    before = gc.mem_free()
    gc.collect()
    after = gc.mem_free()
    freed = after - before
    if freed > 0:
        print(f"GC freed {freed} bytes")
    return freed




i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, i2c)
display.fill(0)
display.text("Hello Yellow!",0,0)
display.text("Hello Blue!",0,17)
display.text("Hello Blue!",0,27)
display.text("Hello Blue!",0,37)
display.text("Hello Blue!",0,47)
display.text("Hello Blue!",0,57)

display.show()

wdt = WDT(timeout=8000)
wdt.feed()



print('gc collect')
gc.collect()

### Configurations files ###
os.chdir('/')
try:
    with open('config.json', 'r') as f:
        config_file = f.read()
        config = json.loads(config_file)
except:
    print('config.json not found')
    create_config_file()
    with open('config.json', 'r') as f:
        config_file = f.read()
        config = json.loads(config_file)
###########################
print('Feed wdt')
wdt.feed()

transmit = TransmitData(ssid="name12", password="password", server_ip="192.168.4.1", server_port=80, wdt_obj=wdt)
transmit.send_simple_data(id=config['id_sensor'], datatype='Starting', data=None)

### Assigning Buttons and limit switch###
b1 = machine.Pin(config['buttons']['button01'], machine.Pin.IN, machine.Pin.PULL_DOWN)
b2 = machine.Pin(config['buttons']['button02'], machine.Pin.IN, machine.Pin.PULL_DOWN)
b3 = machine.Pin(config['buttons']['button03'], machine.Pin.IN, machine.Pin.PULL_DOWN)

relay01 = machine.Pin(config['relays']['relay01'], machine.Pin.OUT)
relay02 = machine.Pin(config['relays']['relay02'], machine.Pin.OUT)


display.fill(0)
display.text('prep2',0,0)
display.show()
# print(os.listdir('/'))
### Initialize Components ###
try:
    sd_rtc_component = Init_SD_RTC()
    sd = sd_rtc_component.set_SDCard()      #/sd mounted
except Exception as e:
    display.fill(0)
    display.text(f'{e}',0,0)
    display.show()
sd_rtc_component = Init_SD_RTC()

sd = sd_rtc_component.set_SDCard()      #/sd mounted
print('Feed wdt')
wdt.feed()
display.fill(0)
display.text('OK SD',0,0)
display.show()

clock_rtc = sd_rtc_component.set_rtc()        #clock object
wdt.feed()

# Set the RTC clock for logging
logging_error.set_rtc_clock(clock_rtc)

time.sleep(1)
display.fill(0)
display.text(f'ok set rtc',0,0)
display.show()
print('Feed wdt')
wdt.feed()
# i2c_test = I2C(1, sda=Pin(26), scl=Pin(27))
# print(i2c_test.scan())

time.sleep(1)
# display.fill(0)
# # display.text(f'date {clock_rtc.datetime}',0,0)
# display.text(f'date {clock_rtc.year}',0,0)
# display.show()
try:
    # i2c_test = I2C(1, sda=Pin(26), scl=Pin(27))
    
    time.sleep(2)
    display.fill(0)
    # display.text(f'{i2c_test.scan()}',0,0)
    display.text(f'{clock_rtc.datetime()}', 0,0)
    display.show()
    time.sleep(2)
    print(clock_rtc.datetime())
    print('Feed wdt')
    wdt.feed()
except Exception as e:
    print(e)
    
    display.fill(0)
    display.text(f'error {e}',0,0)
    display.show()
    time.sleep(2)
print('Feed wdt')
wdt.feed()

time.sleep(1)
display.fill(0)
display.text('OK SD and RTC',0,0)
display.show()
# oled = sd_rtc_component.set_oled()
# oled.fill(0)
# oled.text("Hello Yellow!",0,0)
# oled.show()
time.sleep(1)
display.fill(0)
display.text('Try init Motor', 0,0)
display.show()

# print(clock_rtc.datetime())
print('ok')
time.sleep(1)
motor = Init_Motor()
display.fill(0)
display.text('Init Motor',0,0)
display.show()
print('Feed wdt')
wdt.feed()
### Initialize Sensors ###
print('SENSORS:')
scl = machine.Pin(config['i2c_sensor']['scl'])
sda = machine.Pin(config['i2c_sensor']['sda'])
sensors = Init_Sensors()
for i in range(5):
    wdt.feed()
    try:
        pressure_sensor = sensors.set_PressureSensor()
        bus = machine.I2C(0, scl=scl, sda=sda, freq=50000)
        print(bus.scan())
        if 118 in bus.scan():
            print('BMP280 ok')
            break
    except Exception as e:
        print('BMP280 error', e)
    time.sleep(1)
    
for i in range(5):
    wdt.feed()
    try:
        temp_hum_sensor = sensors.set_TempAndHumidity()
        bus = machine.I2C(0, scl=scl, sda=sda, freq=50000)
        print(bus.scan())
        if 64 in bus.scan():
            print('Si7021 ok')
            break
    except Exception as e:
        print('Si7021 error', e)
    time.sleep(1)


relay01.value(1)
for i in range(5):
    time.sleep(1)
    wdt.feed()

for i in range(5):
    wdt.feed()
    try:
        co2_sensor = sensors.set_k30()
        bus = machine.I2C(0, scl=scl, sda=sda, freq=50000)
        print(bus.scan())
        if 104 in bus.scan():
            print('K30 ok')
            break
    except Exception as e:
        print('K30 error', e)
    time.sleep(1)
        
co2_sensor = sensors.set_k30()
##########################
time.sleep(1)
display.fill(0)
display.text('Sensores OK',0,0)
display.show()
counter = 0
print('Feed wdt')
wdt.feed()
time.sleep(0.5)
display.fill(0)
display.text(f'waiting {counter}',0,0)
display.show()
counter+=1
print(b1.value(), b2.value(), b3.value())
# if b1.value() == 1:
#     motor.Rotate('open')
# elif (b1.value() == 0) and (b2.value() == 0) and (b3.value() == 0):
#     motor.Rotate('stop')   
# elif b2.value() == 1:
#     motor.Rotate('close')
# elif b3.value() == 1:
## Opening chamber
counter = 0
while counter <= 20:
    print('Feed wdt')
    wdt.feed()
    time.sleep(1)
    counter += 1
    motor.Rotate('open')
    print('opening...')
print('Finish initial opening') 
print('Feed wdt')
wdt.feed()
print('Starting main loop')
while True:
    print('Feed wdt')
    wdt.feed()

    print('Turning on the relay for the K30 sensor')
    for i in range(5):
        wdt.feed()

        relay01.value(1)

    n = 0
    while n < config['timeLimits']['measurement_repeat']:
        n += 1

        motor.Rotate('close')
        print('closing...')
        # relay01.value(1)
        relay02.value(1)
        wait_time_inter = 0
        while wait_time_inter < 20:
            time.sleep(1)
            wait_time_inter += 1
            print(f'waiting...{wait_time_inter}')
            print('Feed wdt')
            wdt.feed()

        # time.sleep(20)
        print('closed')
        motor.Rotate('stop')

        print('collect gc')
        gc.collect()
        print('gc done')

        # while True:
        counter = 0
        print('Start measuring')
        
        # Check memory before starting measurement
        if not check_memory():
            print("Low memory warning before measurement!")
            force_gc_collection()
        
        measuring_time = 0
        start_measure = clock_rtc.datetime()
        if start_measure is not None:
            start_measure_time = f'{start_measure.year}-{start_measure.month:02}-{start_measure.day:02}_{start_measure.hour:02}-{start_measure.minute:02}-{start_measure.second:02}'
            filename = f'{start_measure_time}.json'
            folder_path = f'/sd/data/{start_measure.year}-{start_measure.month:02}-{start_measure.day:02}'
        else:
            start_measure_time = f'RTC_ERROR_{measuring_time}'
            filename = f'{start_measure_time}.json'
            folder_path = f'/sd/data/ERROR'
        bmp_pressure = []
        bmp_temperature = []
        si_temperature = []
        si_humidity = []
        k30_co2 = []
        datetime = []
        datetime_utc = []
        
        # Limit maximum samples to prevent memory overflow
        max_samples = min(config['timeLimits']['maxTime_chamber_CLOSE'], 1000)  # Cap at 1000 samples
        sample_count = 0
        print('Feed wdt')
        wdt.feed()
        while measuring_time < config['timeLimits']['maxTime_chamber_CLOSE'] and sample_count < max_samples:
            print('Feed wdt')
            wdt.feed()
            
            # Check memory every 10 samples
            if sample_count % 10 == 0:
                if not check_memory():
                    print(f"Low memory at sample {sample_count}, forcing GC")
                    force_gc_collection()
                    # If still low memory, break early
                    if gc.mem_free() < 5120:  # Less than 5KB
                        print("Critical memory - stopping measurement early")
                        break
            
            print(measuring_time)
            # Initialize variables with default values
            clock_now_tuple = None
            clock_rtc_value = 0
            bmp_pressure_value = None
            bmp_temperature_value = None
            si_temperature_value = None
            si_humidity_value = None
            co2_value = None
            
            # time.sleep(0.25)
            try:
                clock_now_tuple = clock_rtc.datetime()
                clock_rtc_value = rtc.tuple2seconds(clock_now_tuple)
            except Exception as e:
                logging_error.log_exception_to_file(f"RTC read error: {e}", '/sd/error.log')
            
            try:
                bmp_pressure_value = pressure_sensor.pressure
                bmp_temperature_value = pressure_sensor.temperature
            except Exception as e:
                logging_error.log_exception_to_file(f"BMP280 sensor error: {e}", '/sd/error.log')

            try:
                si_temperature_value = temp_hum_sensor.temperature()
                si_humidity_value = temp_hum_sensor.humidity()
            except Exception as e:
                logging_error.log_exception_to_file(f"Si7021 sensor error: {e}", '/sd/error.log')
            
            try:
                co2_value = co2_sensor.read_value()
            except Exception as e:
                logging_error.log_exception_to_file(f"K30 CO2 sensor error: {e}", '/sd/error.log')
            
            # Only update display if we have valid RTC data
            if clock_now_tuple is not None:
                display.fill(0)
                display.text(f'{clock_now_tuple.year}-{clock_now_tuple.month:02}-{clock_now_tuple.day:02}',0, 40)
                display.text(f'{clock_now_tuple.hour:02}:{clock_now_tuple.minute:02}:{clock_now_tuple.second:02}',0, 50)
                display.text(f"Time{n}:{measuring_time}",0,0)
                display.text(f'CO2: {co2_value}',0, 25)
                display.show()
            else:
                display.fill(0)
                display.text(f"Time{n}:{measuring_time}",0,0)
                display.text(f'CO2: {co2_value}',0, 25)
                display.text("RTC Error", 0, 40)
                display.show()
            
            # Append sensor values (None if failed)
            bmp_pressure.append(bmp_pressure_value)
            bmp_temperature.append(bmp_temperature_value)
            si_humidity.append(si_humidity_value)
            si_temperature.append(si_temperature_value)
            k30_co2.append(co2_value)
            
            datetime.append(clock_rtc_value)
            if clock_now_tuple is not None:
                datetime_utc.append(f'{clock_now_tuple.year}-{clock_now_tuple.month:02}-{clock_now_tuple.day:02} {clock_now_tuple.hour:02}:{clock_now_tuple.minute:02}:{clock_now_tuple.second:02}')
                print(clock_now_tuple)
                print(rtc.tuple2seconds(clock_now_tuple))
            else:
                datetime_utc.append(f'RTC_ERROR_{measuring_time}')
                print("RTC read failed")
            
            print('bmp280\t',bmp_pressure_value, bmp_temperature_value)
            # time.sleep(0.25)
            print('si7021\t', si_temperature_value, si_humidity_value)
            # time.sleep(0.25)
            print('k30\t', co2_value)
            # time.sleep(0.5)
            time.sleep(1)
            measuring_time += 1
            sample_count += 1
            # bmp_pressure.append(pressure_sensor.pressure)
        end_measure = clock_rtc.datetime()
        if end_measure is not None:
            end_measure_time = f'{end_measure.year}-{end_measure.month:02}-{end_measure.day:02}_{end_measure.hour:02}-{end_measure.minute:02}-{end_measure.second:02}'
        else:
            end_measure_time = f'RTC_ERROR_{measuring_time}'
        
        raw_data = {'bmp_pressure': bmp_pressure, 'bmp_temperature': bmp_temperature,
                    'si_temperature': si_temperature, 'si_humidity': si_humidity,
                    'k30_co2': k30_co2, 'datetime': datetime, 'datetime_utc': datetime_utc}
        
        # metadata = {'id_sensor': config['id_sensor'], 'start_time': start_measure_time, 'end_time': end_measure_time}
        print('Feed wdt')
        wdt.feed()
        to_json = {
            # 'metadata': metadata, 
                'raw_data': raw_data}
        
        # Feed watchdog before file operations
        wdt.feed()
        
        # Use folder_path from earlier (already handles None case)
        # if not os.path.exists(folder_path):
        #     os.mkdir(folder_path)
        # else:
        #     pass
        
        # if os.path.exists()
        try:
            with open(f'{folder_path}/{filename}', 'w') as f:
                json.dump(to_json, f)
            print(f'{filename} created')
            wdt.feed()
            transmit.send_simple_data(id=config['id_sensor'], datatype='Measurement',
                                      data=f'CO2={k30_co2[0]}-{k30_co2[-1]}')
            # transmit.send_simple_data(id=config['id_sensor'], datatype='Starting', data=None)
        except Exception as e:
            print('Error',e)
            try:
                os.mkdir(folder_path)
                print('Folder created!\t', folder_path)
                with open(f'{folder_path}/{filename}', 'w') as f:
                    json.dump(to_json, f)
                print(f'{filename} created')
                wdt.feed()
                transmit.send_simple_data(id=config['id_sensor'], datatype='Measurement', 
                                      data=f'co2 data')            

            except Exception as e2:
                print('Error creating file', e2)
                logging_error.log_exception_to_file(f"Failed to create file {filename}: {e2}", '/sd/error.log')

        # Clear data from memory after successful write
        del raw_data, to_json
        del bmp_pressure, bmp_temperature, si_temperature, si_humidity
        del k30_co2, datetime, datetime_utc
        force_gc_collection()

        # last_measure = end_measure
        
        print('#########################')
        print('FINISHED MEASURING')
        print('#########################')
        print('Feed wdt')
        wdt.feed()
        print('opening...')
        motor.Rotate('open')
        # relay01.value(0)

        print('running gc')
        gc.collect()
        print('gc done')
        wait_time_inter = 0
        while wait_time_inter < 20:
            print('Feed wdt')
            wdt.feed()
            time.sleep(1)
            wait_time_inter += 1
            print(f'waiting...{wait_time_inter}')
            display.fill(0)
            display.text(f'Opening {wait_time_inter}',0,0)
            display.show()
            
        motor.Rotate('stop')
        print('waiting...')
        # time.sleep(20)
        
        wait_time_inter = 0
        relay02.value(0)
        while wait_time_inter < 120:
            print('Feed wdt')
            wdt.feed()
            time.sleep(1)
            wait_time_inter += 1
            print(f'waiting...{wait_time_inter}')
            display.fill(0)
            display.text(f'Wait inter {wait_time_inter}',0,0)
            display.show()
            

    relay01.value(0) #Turns off relay that controls the K30 sensor
    wait_time = 0
    while wait_time < config['timeLimits']['maxTime_chamber_OPEN']:
        print('Feed wdt')
        wdt.feed()
        time.sleep(1)
        wait_time += 1
        print(f'Full waiting...{wait_time}')
        display.fill(0)
        display.text(f'Full waiting {wait_time}',0,0)
        display.show()