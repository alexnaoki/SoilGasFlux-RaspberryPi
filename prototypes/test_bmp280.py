# Source: Electrocredible.com, Language: MicroPython
from machine import Pin,I2C
from components.bmp280 import *
import time
# import components.bmp280

bus = I2C(0,scl=Pin(1),sda=Pin(0),freq=200000)
print(bus.scan())
bmp = BMP280(bus)

bmp.use_case(BMP280_CASE_INDOOR)

while True:
    pressure=bmp.pressure
    p_bar=pressure/100000
    p_mmHg=pressure/133.3224
    temperature=bmp.temperature
    print("Temperature: {} C".format(temperature))
    print("Pressure: {} Pa, {} bar, {} mmHg".format(pressure,p_bar,p_mmHg))
    time.sleep(1)