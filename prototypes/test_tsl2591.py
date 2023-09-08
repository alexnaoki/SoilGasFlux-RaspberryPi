from machine import Pin, I2C
from components.tsl2591 import TSL2591
import time

tsl2591_sda = Pin(2)
tsl2591_scl = Pin(3)

i2c = I2C(1, scl=tsl2591_scl, sda=tsl2591_sda)
print(i2c.scan())

tsl = TSL2591(i2c=i2c)

while True:
    print(tsl.lux)
    time.sleep(1)