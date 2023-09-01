from components import bmp280, tsl2591, sdcard, SI7021
import machine
import time, os

print('Library imports:\t OK')

class Meteo_Pico:
    def __init__(self):
        print('Initializing Meteo_Pico...')

        self.GPi = {0: {'i2c_n':0, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 0, 'spi_RX': True, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               1: {'i2c_n':0, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':True, 'spi_SCK': False, 'spi_TX': False},
               2: {'i2c_n':1, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': True, 'spi_TX': False},
               3: {'i2c_n':1, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': True},
               4: {'i2c_n':0, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 0, 'spi_RX': True, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               5: {'i2c_n':0, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':True, 'spi_SCK': False, 'spi_TX': False},
               6: {'i2c_n':1, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': True, 'spi_TX': False},
               7: {'i2c_n':1, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': True},
               8: {'i2c_n':0, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 1, 'spi_RX': True, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               9: {'i2c_n':0, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 1, 'spi_RX': False, 'spi_CSn':True, 'spi_SCK': False, 'spi_TX': False},
               10: {'i2c_n':1, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 1, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': True, 'spi_TX': False},
               11: {'i2c_n':1, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 1, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': True},
               12: {'i2c_n':0, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 1, 'spi_RX': True, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               13: {'i2c_n':0, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 1, 'spi_RX': False, 'spi_CSn':True, 'spi_SCK': False, 'spi_TX': False},
               14: {'i2c_n':1, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 1, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': True, 'spi_TX': False},
               15: {'i2c_n':1, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 1, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': True},
               16: {'i2c_n':0, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 0, 'spi_RX': True, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               17: {'i2c_n':0, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':True, 'spi_SCK': False, 'spi_TX': False},
               18: {'i2c_n':1, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': True, 'spi_TX': False},
               19: {'i2c_n':1, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': 0, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': True},
               20: {'i2c_n':0, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': None, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               21: {'i2c_n':0, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': None, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               22: {'i2c_n':None, 'i2c_SDA': False, 'i2c_SCL': False, 'spi_n': None, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               26: {'i2c_n':1, 'i2c_SDA': True, 'i2c_SCL': False, 'spi_n': None, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               27: {'i2c_n':1, 'i2c_SDA': False, 'i2c_SCL': True, 'spi_n': None, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False},
               28: {'i2c_n':None, 'i2c_SDA': False, 'i2c_SCL': False, 'spi_n': None, 'spi_RX': False, 'spi_CSn':False, 'spi_SCK': False, 'spi_TX': False}}
        
        self.inUse_Gpi = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10:False,
                     11:False, 12:False, 13:False, 14:False, 15:False, 16:False, 17:False, 18:False, 19:False, 20:False, 21:False,
                     22:False, 26:False, 27:False, 28:False}
        
    def _checkConflict(self, pin, mode, type):
        if self.inUse_Gpi[pin] == True:
            print('Pin is already in use')
            return False
        else:   
            self.inUse_Gpi[pin] = True
            return True

    
    def set_PressureSensor(self, gpio_scl, gpio_sda):
        '''
        Pressure Sensor: BMP280
        '''
        
        # check_scl = self._checkConflict(pin=gpio_scl, mode='i2c', type='SCL')
        # check_sda = self._checkConflict(pin=gpio_sda, mode='i2c', type='SDA')
        
        i2c_scl = self.GPi[gpio_scl]
        i2c_sda = self.GPi[gpio_sda]
        
        scl = machine.Pin(gpio_scl)
        sda = machine.Pin(gpio_sda)
        
        i2c_id = i2c_scl['i2c_n']
        # print(i2c_id)
        
        bus = machine.I2C(i2c_id, scl=scl, sda=sda)
        self.bmp = bmp280.BMP280(bus)
        self.bmp.use_case(bmp280.BMP280_CASE_INDOOR)
        
        print('Pressure sensor initialized')
        # return self.bmp
if __name__ == '__main__':
    a = Meteo_Pico()
    a.set_PressureSensor()