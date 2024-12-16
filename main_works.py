import machine, os, time, json
from init_sensors import Init_Sensors
from init_motor import Init_Motor
from init_sd_rtc import Init_SD_RTC
from aux.create_config import create_config_file
from aux.chamber_position import ChamberPosition
from prototypes import logging_error
import components.rtc as rtc
import components.ssd1306 as ssd1306
from machine import I2C, Pin, SoftI2C

# i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
# display = ssd1306.SSD1306_I2C(128, 64, i2c)
# display.fill(0)
# display.text("Hello Yellow!",0,0)
# display.text("Hello Blue!",0,17)
# display.text("Hello Blue!",0,27)
# display.text("Hello Blue!",0,37)
# display.text("Hello Blue!",0,47)
# display.text("Hello Blue!",0,57)

# display.show()

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

### Assigning Buttons and limit switch###
b1 = machine.Pin(config['buttons']['button01'], machine.Pin.IN, machine.Pin.PULL_DOWN)
b2 = machine.Pin(config['buttons']['button02'], machine.Pin.IN, machine.Pin.PULL_DOWN)
b3 = machine.Pin(config['buttons']['button03'], machine.Pin.IN, machine.Pin.PULL_DOWN)

# display.fill(0)
# display.text('prep',0,0)
# display.show()
print(os.listdir('/'))
### Initialize Components ###
sd_rtc_component = Init_SD_RTC()
sd = sd_rtc_component.set_SDCard()      #/sd mounted

# display.fill(0)
# display.text('OK SD',0,0)
# display.show()
clock_rtc = sd_rtc_component.set_rtc()        #clock object

# time.sleep(1)
# display.fill(0)
# display.text(f'ok set rtc',0,0)
# display.show()

# i2c_test = I2C(1, sda=Pin(26), scl=Pin(27))
# print(i2c_test.scan())

# time.sleep(1)
# display.fill(0)
# # display.text(f'date {clock_rtc.datetime}',0,0)
# display.text(f'date {clock_rtc.year}',0,0)
# display.show()
# try:
#     i2c_test = I2C(1, sda=Pin(26), scl=Pin(27))
    
#     time.sleep(2)
#     display.fill(0)
#     display.text(f'{i2c_test.scan()}',0,0)
#     display.show()
#     time.sleep(2)
#     print(clock_rtc.datetime)
# except Exception as e:
    
#     display.fill(0)
#     display.text(f'error {e}',0,0)
#     display.show()
#     time.sleep(2)


# time.sleep(1)
# display.fill(0)
# display.text('OK SD and RTC',0,0)
# display.show()
# oled = sd_rtc_component.set_oled()
# oled.fill(0)
# oled.text("Hello Yellow!",0,0)
# oled.show()
# time.sleep(1)
# display.fill(0)
# display.text('Try init Motor', 0,0)
# display.show()

# print(clock_rtc.datetime())
print('ok')
time.sleep(1)
motor = Init_Motor()
# display.fill(0)
# display.text('Init Motor',0,0)
# display.show()

### Initialize Sensors ###
print('SENSORS:')
sensors = Init_Sensors()
pressure_sensor = sensors.set_PressureSensor()
temp_hum_sensor = sensors.set_TempAndHumidity()
co2_sensor = sensors.set_k30()
##########################
time.sleep(1)
# display.fill(0)
# display.text('Sensores OK',0,0)
# display.show()
counter = 0
while True:
    time.sleep(0.5)
    # display.fill(0)
    # display.text(f'waiting {counter}',0,0)
    # display.show()
    counter+=1
    print(b1.value(), b2.value(), b3.value())
    if b1.value() == 1:
        motor.Rotate('open')
    elif (b1.value() == 0) and (b2.value() == 0) and (b3.value() == 0):
        motor.Rotate('stop')   
    elif b2.value() == 1:
        motor.Rotate('close')
    elif b3.value() == 1:
        print('Start measuring')
        
        measuring_time = 0
        start_measure = clock_rtc.datetime()
        start_measure_time = f'{start_measure.year}-{start_measure.month:02}-{start_measure.day:02}_{start_measure.hour:02}-{start_measure.minute:02}-{start_measure.second:02}'
        filename = f'{start_measure_time}.json'
        bmp_pressure = []
        bmp_temperature = []
        si_temperature = []
        si_humidity = []
        k30_co2 = []
        datetime = []
        datetime_utc = []
        while measuring_time < config['timeLimits']['maxTime_chamber_CLOSE']:
            # display.fill(0)
            # display.text(f"Time:{measuring_time}",0,0)
            # display.show()
            print(measuring_time)
            # time.sleep(0.25)
            clock_now_tuple = clock_rtc.datetime()
            clock_rtc_value = rtc.tuple2seconds(clock_now_tuple)
            
            bmp_pressure_value = pressure_sensor.pressure
            bmp_temperature_value = pressure_sensor.temperature
            
            si_temperature_value = temp_hum_sensor.temperature()
            si_humidity_value = temp_hum_sensor.humidity()
            
            co2_value = co2_sensor.read_value()
            
            bmp_pressure.append(bmp_pressure_value)
            bmp_temperature.append(bmp_temperature_value)
            si_humidity.append(si_humidity_value)
            si_temperature.append(si_temperature_value)
            k30_co2.append(co2_value)
            
            datetime.append(clock_rtc_value)
            datetime_utc.append(f'{clock_now_tuple.year}-{clock_now_tuple.month:02}-{clock_now_tuple.day:02} {clock_now_tuple.hour:02}:{clock_now_tuple.minute:02}:{clock_now_tuple.second:02}')
            
            print(clock_now_tuple)
            print(rtc.tuple2seconds(clock_now_tuple))
            print('bmp280\t',bmp_pressure_value, bmp_temperature_value)
            # time.sleep(0.25)
            print('si7021\t', si_temperature_value, si_humidity_value)
            # time.sleep(0.25)
            print('k30\t', co2_value)
            # time.sleep(0.5)
            time.sleep(1)
            measuring_time += 1
            # bmp_pressure.append(pressure_sensor.pressure)
        end_measure = clock_rtc.datetime()
        end_measure_time = f'{end_measure.year}-{end_measure.month:02}-{end_measure.day:02}_{end_measure.hour:02}-{end_measure.minute:02}-{end_measure.second:02}'
        
        raw_data = {'bmp_pressure': bmp_pressure, 'bmp_temperature': bmp_temperature,
                    'si_temperature': si_temperature, 'si_humidity': si_humidity,
                    'k30_co2': k30_co2, 'datetime': datetime, 'datetime_utc': datetime_utc}
        
        # metadata = {'id_sensor': config['id_sensor'], 'start_time': start_measure_time, 'end_time': end_measure_time}
        
        to_json = {
            # 'metadata': metadata, 
                   'raw_data': raw_data}
        
        with open(f'/sd/data/{filename}', 'w') as f:
            json.dump(to_json, f)
        print(f'{filename} created')
        
        print('#########################')
        print('FINISHED MEASURING')
        print('#########################')

        