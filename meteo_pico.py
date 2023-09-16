from components import bmp280, tsl2591, sdcard, SI7021, k30fr, rtc
import machine
import time, os
import uos
 
 
print('Library imports:\t OK')

class Meteo_Pico:
    def __init__(self):
        print('Initializing Meteo_Pico...')
        
        i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)
        print(i2c.scan())

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
        
        bus = machine.I2C(i2c_id, scl=scl, sda=sda, freq=100000)
        self.bmp = bmp280.BMP280(bus)
        self.bmp.use_case(bmp280.BMP280_CASE_INDOOR)
        
        print('Pressure sensor initialized')
        # return self.bmp
        
    def set_TempAndHumidity(self, gpio_scl, gpio_sda):
        '''
        Temperature and Humidity Sensor: SI7021
        '''
        
        # check_scl = self._checkConflict(pin=gpio_scl, mode='i2c', type='SCL')
        # check_sda = self._checkConflict(pin=gpio_sda, mode='i2c', type='SDA')
        # print(check_scl, check_sda)
        
        i2c_scl = self.GPi[gpio_scl]
        i2c_sda = self.GPi[gpio_sda]
        
        scl = machine.Pin(gpio_scl)
        sda = machine.Pin(gpio_sda)
        
        i2c_id = i2c_scl['i2c_n']
        print(i2c_id)
        
        bus = machine.I2C(i2c_id, scl=scl, sda=sda, freq=100000)
        print(bus.scan())
        self.si = SI7021.SI7021(bus)
        
        print('Temperature and Humidity sensor initialized')
        humidity = self.si.humidity()
        temperature = self.si.temperature()
        humidity = self.si.humidity()
        dew_point = self.si.dew_point()
        print(humidity, temperature, dew_point)
    
    def set_LightSensor(self, gpio_scl, gpio_sda):
        scl = machine.Pin(gpio_scl)
        sda = machine.Pin(gpio_sda)
        
        i2c_id = self.GPi[gpio_scl]['i2c_n']
        
        i2c = machine.I2C(i2c_id, scl=scl, sda=sda, freq=100000)
        print(i2c.scan())
        self.tsl = tsl2591.TSL2591(i2c=i2c)
        print('Light sensor initialized')
        print(self.tsl.lux)
    
    def set_SDCard(self, gpio_cs, gpio_sck, gpio_di, gpio_do):
        cs = machine.Pin(gpio_cs, machine.Pin.OUT)
        sck = machine.Pin(gpio_sck)
        di = machine.Pin(gpio_di)
        do = machine.Pin(gpio_do)
        
        spi_id = self.GPi[gpio_cs]['spi_n']
        print(spi_id)
        
        spi = machine.SPI(spi_id, sck=sck, mosi=di, miso=do,
                          baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB)
        
        # print(spi)
        self.sd = sdcard.SDCard(spi=spi, cs=cs)

        vfs = uos.VfsFat(self.sd)
        uos.mount(vfs, "/sd")
        print('SD Card initialized')
        
    def set_k30fr(self, gpio_scl, gpio_sda):
        scl = machine.Pin(gpio_scl)
        sda = machine.Pin(gpio_sda)
        i2c_id = 0
        
        i2c = machine.I2C(i2c_id, scl=scl, sda=sda, freq=100000)
        try:
            self.k30 = k30fr.K30(i2c)
            # value = k30.read_value()
            # print()
            print('K30 initialized')
        except:
            pass
        
    def set_rtc(self, gpio_scl, gpio_sda, datetime):
        '''
        PCF8523
        datetime: (year, month, day, weekday, hour, minute, second, milisecond)
        
        To convert from int to datetime:
        import datetime
        time = <output from rtc.datetime>
        datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
        '''
        scl = machine.Pin(gpio_scl)
        sda = machine.Pin(gpio_sda)
        i2c_id = 1
        
        i2c = machine.I2C(i2c_id, scl=scl, sda=sda)
        
        self.rtc = rtc.PCF8523(i2c)
        self.rtc.datetime = datetime
        print('RTC initialized with datetime: {0} (needs to convert from int to datetime format)'.format(self.rtc.datetime))
    
    
if __name__ == '__main__':
    a = Meteo_Pico()
    a.set_PressureSensor(gpio_scl=1, gpio_sda=0)
    
    a.set_TempAndHumidity(gpio_scl=1, gpio_sda=0)
    
    a.set_LightSensor(gpio_scl=1, gpio_sda=0)
    
    a.set_SDCard(gpio_cs=17, gpio_sck=18, gpio_di=19, gpio_do=16)
    
    a.set_k30fr(gpio_scl=1, gpio_sda=0)
    
    print(os.listdir())
    time.sleep(5)
    
    counter = 0
    while True:
        
        f = open(f'/sd/{counter}.csv', 'w')
        f.write('Pressure (bmp280), Temperature (bmp280), Humidity (si7021), Temperature (si7021), Lux (tsl2591), CO2 (k30fr)\n')
        
        
        for i in range(60):
            bmp280_pressure_value = ''
            bmp280_temperature_value = ''
            
            si_humidity_value = ''
            si_temperature_value = ''
            
            tsl_lux_value = ''
            
            k30_co2_value = ''
            time.sleep(1)
            
            try:
                bmp280_pressure_value = a.bmp.pressure
                bmp280_temperature_value = a.bmp.temperature
                
                si_humidity_value = a.si.humidity()
                si_temperature_value = a.si.temperature()
                
                tsl_lux_value = a.tsl.lux
                
                k30_co2_value = a.k30.read_value()
                print('Pressure: {0} Pa'.format(bmp280_pressure_value))
                print('Temperature: {0} C'.format(bmp280_temperature_value))

                print('Humidity: {0}'.format(si_humidity_value))
                print('Temperature: {0}C'.format(si_temperature_value))
                
                print('Lux: {0}'.format(tsl_lux_value))
                
                print('CO2: {0}'.format(k30_co2_value))
                print()
            except Exception as e:
                print(e)
                print('error')
                
                pass
            
            f.write(f'{bmp280_pressure_value}, {bmp280_temperature_value}, {si_humidity_value}, {si_temperature_value}, {tsl_lux_value}, {k30_co2_value}\n')
            
        f.close()
        print('### File written ###')
        counter += 1