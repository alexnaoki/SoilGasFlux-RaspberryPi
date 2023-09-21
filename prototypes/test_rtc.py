from machine import Pin, I2C
import time
import components.rtc as rtc

i2c_0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
print(i2c_0.scan())

# time.sleep(1)
print()
i2c_1 = I2C(1, sda=Pin(26), scl=Pin(27))
print(i2c_1.scan())

clock_rtc = rtc.PCF8523(i2c=i2c_1)

# clock_rtc.datetime = (2023, 9, 16, 10,18,0,0)

date = rtc.datetime_tuple(year=2023, month=9, day=19, weekday=None, hour=11, minute=13, second=0, millisecond=0)
clock_rtc.datetime(date)
print(clock_rtc.datetime())

# print(clock_rtc.datetime)
while True:
    time.sleep(1)
    timenow = rtc.tuple2seconds(clock_rtc.datetime())
    # print(clock_rtc.datetime())
    # print(rtc.tuple2seconds(timenow))
    print(timenow)
    # print(type(timenow))
    # print(clock_rtc.alarm_time())