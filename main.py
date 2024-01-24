import machine, os, time, json
# from meteo_pico import Meteo_Pico
from init_sensors import Init_Sensors
from init_motor import Init_Motor
from init_sd_rtc import Init_SD_RTC
from aux.create_config import create_config_file
from aux.chamber_position import ChamberPosition
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

### Assigning Buttons and limit switch###
b1 = machine.Pin(config['buttons']['button01'], machine.Pin.IN, machine.Pin.PULL_DOWN)
b2 = machine.Pin(config['buttons']['button02'], machine.Pin.IN, machine.Pin.PULL_DOWN)

led = machine.Pin(25, machine.Pin.OUT)


motor_current_state = None

top_ls_pressed = None
bot_ls_pressed = None

def stop_motor_TOP(pin):
    print('Motor stopped in the top', pin.value())
    global motor_current_state
    motor_current_state = 'stop'
    print('Motor current state:\t',motor_current_state)
    motor.Rotate(motor_current_state)
    global top_ls_pressed
    top_ls_pressed = True
    
def stop_motor_BOTTOM(pin):
    print('Motor stopped in the bottom', pin.value())
    global motor_current_state
    motor_current_state = 'stop'
    print('Motor current state:\t',motor_current_state)
    motor.Rotate(motor_current_state)
    global bot_ls_pressed
    bot_ls_pressed = True

ls_power01 = machine.Pin(config['relays']['relay01'], machine.Pin.OUT) ## Power relay (using to power both limit switches)
ls_power02 = machine.Pin(config['relays']['relay02'], machine.Pin.OUT) ## Power relay (using to power both limit switches)
ls_power01.value(1)
ls_power02.value(1)


ls_top = machine.Pin(config['limit_swiches']['top'], machine.Pin.IN, machine.Pin.PULL_DOWN)
ls_bot = machine.Pin(config['limit_swiches']['bottom'], machine.Pin.IN, machine.Pin.PULL_DOWN)

ls_top.irq(trigger=machine.Pin.IRQ_RISING, handler=stop_motor_TOP)
ls_bot.irq(trigger=machine.Pin.IRQ_RISING, handler=stop_motor_BOTTOM)


###########################

print(os.listdir('/'))
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
initial_chamber_position = ChamberPosition(limit_switch_bot=ls_bot, limit_switch_top=ls_top)
chamber_position = initial_chamber_position.check_limit_switches()
if chamber_position == 'bottom':
    print('Chamber is in the bottom')
    motor_next_action = 'open'
elif chamber_position == 'top':
    print('Chamber is in the top')
    motor_next_action = None
    motor_current_state = 'stop'
else:
    print('Chamber not pressing limit switch')
    motor_next_action = 'open'
motor.Rotate(motor_next_action)
print('before\t',motor_next_action)
print('current\t',motor_current_state)
# while motor_next_action == 'open':
while motor_current_state != 'stop':
    time.sleep(0.5)
    print('Waiting the top limit switch',motor_current_state)

print('\n\n######## Motor stopped ########\n\n')
# print('Motor stopped at top\t', motor_current_state)
# time.sleep(3)
# print('Entrando no loop')
time.sleep(3)

last_action = None
while True:
    if top_ls_pressed and (last_action != 'waiting'):
        motor_current_state = 'stop'
        motor.Rotate(motor_current_state)
        motor_next_action = 'close'
        
        print('#'*20)
        print('Top limit switch pressed')    
        print('#'*20)
        print('Starting waiting period')
        
        waiting_time = 0
        while waiting_time < config['timeLimits']['maxTime_chamber_OPEN']:
            print('Waiting time:\t', waiting_time)
            time.sleep(1)
            waiting_time += 1
        
        print('#'*20)
        print('Finished waiting period')
        print('#'*20)
        motor.Rotate(motor_next_action)
        top_ls_pressed = False
        last_action = 'waiting'
        
    elif bot_ls_pressed and (last_action != 'measuring'):
        motor_current_state = 'stop'
        motor.Rotate(motor_current_state)
        motor_next_action = 'open'
        
        measuring_time = 0
        print('#########################')
        print('Bot limit switch pressed')
        print('#########################')
        print('Starting measuring')
        while measuring_time < config['timeLimits']['maxTime_chamber_CLOSE']:
            print(measuring_time)
            # time.sleep(0.25)
            print('bmp280\t',pressure_sensor.pressure, pressure_sensor.temperature)
            time.sleep(0.25)
            print('si7021\t', temp_hum_sensor.temperature(), temp_hum_sensor.humidity())
            time.sleep(0.25)
            print('k30\t', co2_sensor.read_value())
            time.sleep(0.5)
            
            measuring_time += 1
        
        print('#########################')
        print('FINISHED MEASURING')
        print('#########################')
        motor.Rotate(motor_next_action)
        bot_ls_pressed = False
        last_action = 'measuring'
    
    elif bot_ls_pressed and (last_action == 'measuring'):
        time.sleep(1)
        motor_current_state = 'stop'
        motor.Rotate(motor_current_state)
        motor_next_action = 'open'
        print('Bottom Double pressed detected!!')
        print('Starting opening chamber')
        time.sleep(1)
        motor.Rotate(motor_next_action)
        bot_ls_pressed = False 
    elif top_ls_pressed and (last_action == 'waiting'):
        time.sleep(1)
        motor_current_state = 'stop'
        motor.Rotate(motor_current_state)
        motor_next_action = 'close'
        print('Top Double pressed detected!!')
        print('Starting closing chamber')
        time.sleep(1)
        motor.Rotate(motor_next_action)
        top_ls_pressed = False
    else:
        print('Waiting for the limit switch:\t', bot_ls_pressed, top_ls_pressed)
        print('Last action:\t', last_action)

    time.sleep(1)
