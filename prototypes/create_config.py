import json
import os

if __name__ == '__main__':
    buttons = {'button01': 6, 'button02':7, 'button03':8}
    
    motor = {'ai01': 13, 'ai02': 14, 'pwma': 15,
             'bi01': 22, 'bi02': 21, 'pwmb': 20}
    relays = {'relay01': 11, 'relay02': 12}
    limit_swiches = {'bottom': 9, 'top': 10}
    
    rtc = {'scl': 27, 'sda': 26}
    sd_card = {'rx': 16, 'cs':17, 'sck':18, 'tx':19}
    
    i2c_sensor = {'scl': 1, 'sda': 0}
    
    config_gpio = {'buttons': buttons, 'motor': motor, 'relays': relays,
                   'limit_swiches': limit_swiches, 'rtc': rtc,
                   'sd_card': sd_card, 'i2c_sensor': i2c_sensor}
    print(os.getcwd())
    os.chdir('/')
    
    
    with open('config.json', 'w') as f:
        json.dump(config_gpio, f)
    print('config.json created')