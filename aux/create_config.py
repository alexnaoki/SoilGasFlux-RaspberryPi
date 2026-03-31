import json
import os
import time
import machine
from prototypes import logging_error

def _get_system_time(utc_now):
    """Set the Pico's internal RTC to the given UTC time and return a start_time dict.

    Args:
        utc_now: tuple (year, month, day, hour, minute, second) in UTC.
    """
    machine.RTC().datetime((utc_now[0], utc_now[1], utc_now[2], 0,
                            utc_now[3], utc_now[4], utc_now[5], 0))
    t = time.gmtime()
    print('UTC time:', t)
    return {
        'year': t[0], 'month': t[1], 'day': t[2],
        'weekday': t[6], 'hour': t[3], 'minute': t[4],
        'second': t[5], 'millisecond': None, 'sync': True
    }

@logging_error.log_errors_to_file('error.log')
def create_config_file(utc_now):
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
              'maxTime_chamber_CLOSE': 60, 
              'maxTime_chamber_OPEN': 20*60,
              'measurement_repeat': 20,
              'measurement_wait_inbetween': 30,
              }
    
    # Set Pico RTC to the provided UTC time
    start_time = _get_system_time(utc_now)
    
    id_sensor = 'gals-1.2'
    # WIFI_SSID = "CO2Monitor"
# WIFI_PASSWORD = "co2monitor123"
    wifi = {'ssid': 'gals_1-2', 'password': 'co2monitor123',
            'server_ip': '192.168.4.1', 'server_port': 80, 'tcp_port': 8080}
    ####################
    
    
    config = {'buttons': buttons, 'motor': motor, 'relays': relays,
              'limit_swiches': limit_swiches, 'rtc': rtc,
              'sd_card': sd_card, 'i2c_sensor': i2c_sensor,
              'start_time': start_time, 'timeLimits': limits,
              'id_sensor': id_sensor, 'wifi': wifi}
    print(os.getcwd())
    os.chdir('/')
    
    
    with open('config.json', 'w') as f:
        json.dump(config, f)
    print('config.json created')
    
# def create_folder(path, folder_name):
#     os.

if __name__ == '__main__':
    # Pass current UTC time: (year, month, day, hour, minute, second)
    create_config_file(utc_now=(2026, 3, 25, 19, 29, 0))