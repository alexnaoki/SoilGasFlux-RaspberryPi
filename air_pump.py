import machine, os, time, json
from init_sensors import Init_Sensors
from init_airpump import Init_AirPump
from init_sd_rtc import Init_SD_RTC
from aux.create_config import create_config_file
from aux.chamber_position import ChamberPosition
from prototypes import logging_error
import components.rtc as rtc
import components.ssd1306 as ssd1306
from machine import I2C, Pin, SoftI2C

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

fan1 = machine.Pin(config['limit_swiches']['top'], machine.Pin.OUT, machine.Pin.PULL_UP)
fan1.value(1)
fan2 = machine.Pin(config['limit_swiches']['bottom'], machine.Pin.IN, machine.Pin.PULL_DOWN)

time.sleep(1)
motor = Init_AirPump()

# while True:
#     time.sleep(0.5)
#     print(b1.value(), b2.value(), b3.value())
#     if b1.value() == 1:
#         motor.Rotate('open')
#     elif (b1.value() == 0) and (b2.value() == 0) and (b3.value() == 0):
#         motor.Rotate('stop')   
#     elif b2.value() == 1:
#         motor.Rotate('close')
#     elif b3.value() == 1:
#         motor.Rotate('other_motor')
motor_1 = 'stop'
motor_2 = 'stop'
while True:
    time.sleep(0.5)
    print(b1.value(), b2.value(), b3.value())
    if (b1.value()==1) and (motor_1 == 'stop'):
        motor.Rotate('open')
        motor_1 = 'open'
    elif (b1.value()==1) and (motor_1 == 'open'):
        motor.Rotate('stop')
        motor_1 = 'stop'
    elif (b2.value()==1) and (motor_1 == 'stop'):
        motor.Rotate('close')
        motor_1 = 'close'
    elif (b2.value()==1) and (motor_1 == 'close'):
        motor.Rotate('stop')
        motor_1 = 'stop'
    elif (b3.value()==1) and (motor_2 == 'stop'):
        motor.Rotate('other_motor')
        motor_2 = 'other_motor'
    elif (b3.value()==1) and (motor_2 == 'other_motor'):
        motor.Rotate('stop')
        motor_2 = 'stop'
