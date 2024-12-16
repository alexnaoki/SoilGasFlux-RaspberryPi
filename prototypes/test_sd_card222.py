from init_sd_rtc import Init_SD_RTC
import machine, time, json, os
from aux.create_config import create_config_file
import components.rtc as rtc
from machine import I2C, Pin, SoftI2C, WDT
import gc


print('ok')


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
        
time.sleep(1)
try:
    sd_rtc_component = Init_SD_RTC()
    sd = sd_rtc_component.set_SDCard()      #/sd mounted
except Exception as e:
    pass
    # display.fill(0)
    # display.text(f'{e}',0,0)
    # display.show()

time.sleep(1)
sd_rtc_component = Init_SD_RTC()
time.sleep(1)
sd = sd_rtc_component.set_SDCard()      #/sd mounted
time.sleep(1)
clock_rtc = sd_rtc_component.set_rtc()        #clock object
time.sleep(1)
print(os.listdir('/sd'))
last_hour = 0
last_minute = 0
while True:
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    print(free, alloc)
    gc.collect()
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    print(free, alloc)
    # time.sleep(1)
    start_measure = clock_rtc.datetime()
    start_measure_time = f'{start_measure.year}-{start_measure.month:02}-{start_measure.day:02}_{start_measure.hour:02}-{start_measure.minute:02}-{start_measure.second:02}'
    print('start_measure_time',start_measure_time)

    # print(gc.mem_free())
    # print(gc.mem_alloc())
    filename = f'{start_measure_time}.json'

    data = {'data': [(free, alloc) for i in range(500)]}
    hour = start_measure.hour
    minute = start_measure.minute
    if (hour != last_hour) or (minute != last_minute):
        print('created folder')
        os.mkdir(f'/sd/data/{start_measure.year}-{start_measure.month:02}-{start_measure.day:02}_{start_measure.hour:02}-{start_measure.minute:02}')
    else:
        pass
    with open(f'/sd/data/{start_measure.year}-{start_measure.month:02}-{start_measure.day:02}_{start_measure.hour:02}-{start_measure.minute:02}/{filename}', 'w') as f:
        json.dump(data, f)
        
    after = clock_rtc.datetime()
    after_time = f'{after.year}-{after.month:02}-{after.day:02}_{after.hour:02}-{after.minute:02}-{after.second:02}'
    
    print('after_time',after_time)
    print()
    last_hour = start_measure.hour
    last_minute = start_measure.minute
