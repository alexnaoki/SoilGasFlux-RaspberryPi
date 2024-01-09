import machine, os, time, json
# from meteo_pico import Meteo_Pico
from init_sensors import Init_Sensors
from init_motor import Init_Motor
from init_sd_rtc import Init_SD_RTC
from aux.create_config import create_config_file
from aux.chamber_position import Chamber_Position
from prototypes import logging_error


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

### Assigning Buttons ###
b1 = machine.Pin(config['buttons']['button01'], machine.Pin.IN, machine.Pin.PULL_DOWN)
b2 = machine.Pin(config['buttons']['button02'], machine.Pin.IN, machine.Pin.PULL_DOWN)

led = machine.Pin(25, machine.Pin.OUT)
###########################

### Initialize Components ###
sd_rtc_component = Init_SD_RTC()
sd = sd_rtc_component.set_SDCard()      #/sd mounted
rtc = sd_rtc_component.set_rtc()        #clock object

print(rtc.datetime())
print('ok')
motor = Init_Motor()
#############################

### Initialize Sensors ###
print('SENSORS:')
sensors = Init_Sensors()
pressure_sensor = sensors.set_PressureSensor()
temp_hum_sensor = sensors.set_TempAndHumidity()
co2_sensor = sensors.set_k30()
##########################


### Initialize Chamber ###
initial_chamber_position = Chamber_Position(config=config)
chamber_position = initial_chamber_position.check_chamber_position()
if chamber_position == 'bottom':
    print('Chamber is in the bottom')
elif chamber_position == 'top':
    print('Chamber is in the top')
else:
    print('Chamber not pressing limit switch')



while True:
    time.sleep(0.5)
    print('nada')

    # motor.Rotate_ButtonControl(b1.value(), b2.value())



