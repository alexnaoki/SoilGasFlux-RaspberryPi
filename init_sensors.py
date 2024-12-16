from components import bmp280, tsl2591, SI7021, k30fr
import machine, time, os, json, uos
from prototypes import logging_error

class Init_Sensors:
    def __init__(self):
        print('Initialize Sensors')
        
        with open('config.json', 'r') as f:
            config_file = f.read()
            self.config = json.loads(config_file)
            
        self.i2c = machine.I2C(0, scl=machine.Pin(self.config['i2c_sensor']['scl']), 
                               sda=machine.Pin(self.config['i2c_sensor']['sda']), freq=50000)
        print(self.i2c.scan())
        
    @logging_error.log_errors_to_file('/sd/error.log')
    def set_PressureSensor(self):
        '''
        Pressure sensor BMP280
        '''
        # try:
        scl = machine.Pin(self.config['i2c_sensor']['scl'])
        sda = machine.Pin(self.config['i2c_sensor']['sda'])
        
        bus = machine.I2C(0, scl=scl, sda=sda, freq=50000, timeout=5000)
        time.sleep_ms(100)
        
        self.bmp = bmp280.BMP280(bus)
        time.sleep_ms(100)
        self.bmp.use_case(bmp280.BMP280_CASE_INDOOR)
        time.sleep_ms(100)
        print('Pressure Sensor initialized')
        
        return self.bmp
        # except Exception as e:
        #     print('Pressure Sensor error:/t', e)
            # logging_error.log_errors_and_reset('error.log', e)
    
    @logging_error.log_errors_to_file('/sd/error.log')
    def set_TempAndHumidity(self):
        '''
        Temperature and Humidity sensor SI7021
        '''
        # try:
        scl = machine.Pin(self.config['i2c_sensor']['scl'])
        sda = machine.Pin(self.config['i2c_sensor']['sda'])
        
        bus = machine.I2C(0, scl=scl, sda=sda, freq=50000, timeout=5000)
        
        time.sleep_ms(100)
        self.si = SI7021.SI7021(bus)
        print('Temperature and Humidity Sensor initialized')
        time.sleep_ms(100)
        return self.si
        # except Exception as e:
        #     print('Temperature and Humidity Sensor error:/t', e)
        #     # logging_error.log_errors_and_reset('error.log', e)
            
    @logging_error.log_errors_to_file('/sd/error.log')
    def set_k30(self):
        '''
        CO2 sensor K30FR
        '''
        # try:
        scl = machine.Pin(self.config['i2c_sensor']['scl'])
        sda = machine.Pin(self.config['i2c_sensor']['sda'])
        
        bus = machine.I2C(0, scl=scl, sda=sda, freq=10000, timeout=100000)
        
        self.k30 = k30fr.K30(bus)
        print('CO2 Sensor initialized')
        
        return self.k30
        # except Exception as e:
        #     print('CO2 Sensor error:/t', e)
        #     # logging_error.log_errors_and_reset('error.log', e)