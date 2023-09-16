from machine import Pin, I2C
import time
from components.rtc import PCF8523

i2c_0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
print(i2c_0.scan())

# time.sleep(1)
print()
i2c_1 = I2C(1, sda=Pin(26), scl=Pin(27))
print(i2c_1.scan())

clock_rtc = PCF8523(i2c=i2c_1)

clock_rtc.datetime = (2023, 9, 16, 10,18,0,0)

print(clock_rtc.datetime)