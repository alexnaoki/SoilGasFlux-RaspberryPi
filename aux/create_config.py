import json
import os
from prototypes import logging_error

@logging_error.log_errors_to_file('error.log')
def create_config_file():
    ##### GPIOs ########
    buttons = {'button01': 6, 'button02': 7, 'button03':8}
    
    motor = {'ai01': 13, 'ai02': 14, 'pwma': 15,
             'bi01': 22, 'bi02': 21, 'pwmb': 20}
    relays = {'relay01': 2, 'relay02': 3}
    limit_swiches = {'bottom': 9, 'top': 10}
    
    rtc = {'scl': 27, 'sda': 26}
    sd_card = {'rx': 16, 'cs':17, 'sck':18, 'tx':19}
    
    i2c_sensor = {'scl': 1, 'sda': 0}
    
    ####################
    
    ##### USER INPUTS #######
    limits = {'maxTime_motor_ON': 1*60, 
              'maxTime_chamber_CLOSE': 150, 
              'maxTime_chamber_OPEN': 20*60,
              'measurement_repeat': 3,
              'measurement_wait_inbetween': 120,
              }
    
    start_time = {'year': 2025, 'month':6, 'day':23, 'weekday':4, 
                  'hour':15, 'minute':39, 'second':0, 'millisecond':None, 'sync':False}
    
    id_sensor = 'sensor01'
    ####################
    
    
    config = {'buttons': buttons, 'motor': motor, 'relays': relays,
              'limit_swiches': limit_swiches, 'rtc': rtc,
              'sd_card': sd_card, 'i2c_sensor': i2c_sensor,
              'start_time': start_time, 'timeLimits': limits,
              'id_sensor': id_sensor}
    print(os.getcwd())
    os.chdir('/')
    
    
    with open('config.json', 'w') as f:
        json.dump(config, f)
    print('config.json created')
    
# def create_folder(path, folder_name):
#     os.

if __name__ == '__main__':
    create_config_file()