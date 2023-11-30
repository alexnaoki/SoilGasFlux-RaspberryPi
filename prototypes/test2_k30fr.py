from components.k30fr import K30
from machine import Pin, I2C
import time

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
print(i2c.scan())

while True:
    try:
        print(i2c.scan())
        k30 = K30(i2c)
        value = k30.read_value()
        print(value)
        time.sleep_ms(1000)
    except Exception as e:
        print(e)
        print('erro')
        time.sleep_ms(1000)
# while True:
#     # try:
#     k30 = K30(i2c)
#     value = k30.read_value()
#     print(value)
#     time.sleep_ms(1000)
    # except Exception as e:
        # print(e)
        # print('erro')
        # time.sleep_ms(1000)
