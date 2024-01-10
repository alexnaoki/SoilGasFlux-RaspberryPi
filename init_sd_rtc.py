from components import sdcard, rtc
import machine, time, os, json, uos
from prototypes import logging_error

class Init_SD_RTC:
    def __init__(self):
        print('Initialize SD Card and RTC')
        
        os.chdir('/')
        
        with open('config.json', 'r') as f:
            config_file = f.read()
            self.config = json.loads(config_file)
        
        self.set_SDCard()
        
        self.clock = self.set_rtc()
        
        if self.config['start_time']['sync']:
            self.sync_rtc(self.clock)
        else:
            print('No RTC sync applied')
            print(self.clock.datetime())
        
    
    @logging_error.log_errors_to_file('error.log') 
    def set_SDCard(self):
        gpio_cs = self.config['sd_card']['cs']
        gpio_sck = self.config['sd_card']['sck']
        gpio_di = self.config['sd_card']['tx']
        gpio_do = self.config['sd_card']['rx']
        
        cs = machine.Pin(gpio_cs, machine.Pin.OUT)
        sck = machine.Pin(gpio_sck)
        di = machine.Pin(gpio_di)
        do = machine.Pin(gpio_do)
        
        # spi_id = self.GPi[gpio_cs]['spi_n']
        spi_id = 0
        print(spi_id)
        
        # try:
        spi = machine.SPI(spi_id, sck=sck, mosi=di, miso=do,
                        baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB)
        
        # print(spi)
        self.sd = sdcard.SDCard(spi=spi, cs=cs)

        try:
            uos.umount("/sd")
        except:
            pass
        vfs = uos.VfsFat(self.sd)
        uos.mount(vfs, "/sd")
        print('SD Card initialized')
            # return 0
        # except Exception as e:
        #     print('ERRO')
        #     print(e)
            # logging_error.log_errors_and_reset('error.log', e)
            
            # print('SD card error:/t', e)
            # machine.reset()
            
    @logging_error.log_errors_to_file('error.log')
    def set_rtc(self):
        gpio_sda = self.config['rtc']['sda']
        gpio_scl = self.config['rtc']['scl']
        
        sda = machine.Pin(gpio_sda)
        scl = machine.Pin(gpio_scl)
        
        id = 1
        # print(gpio_scl, gpio_sda)
        i2c_1 = machine.I2C(id, sda=sda, scl=scl)
        clock = rtc.DS1307(i2c=i2c_1)
        
        return clock
    
    @logging_error.log_errors_to_file('error.log')
    def sync_rtc(self, clock):
        print('sync_time #####')
    
        start_time = self.config['start_time']
        
        start_datetime = rtc.datetime_tuple(year=start_time['year'], month=start_time['month'], day=start_time['day'], weekday=None, 
                                            hour=start_time['hour'], minute=start_time['minute'], second=start_time['second'], millisecond=start_time['millisecond'])
        
        clock.datetime(start_datetime)
        
        clock_datetime = clock.datetime()
        
        print('syncing....')
        machine.RTC().datetime((clock_datetime.year, clock_datetime.month, clock_datetime.day, clock_datetime.weekday, clock_datetime.hour, clock_datetime.minute, clock_datetime.second, clock_datetime.millisecond))
        print(time.localtime())
        print(self.clock.datetime())
        time.sleep(5)
        print(time.localtime())
        print(self.clock.datetime())
        print('synced')

    
if __name__ == '__main__':
    Init_SD_RTC()