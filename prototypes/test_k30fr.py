
from machine import Pin, I2C, SoftI2C
import time

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
# i2c = SoftI2C(scl=Pin(1), sda=Pin(0), freq=100000)
print(i2c.scan())
# for i in range(100):
while True:
    try:
        i2c.writeto(0x68, bytes([0x22, 0x00, 0x08, 0x2A]))
        time.sleep_ms(30)
        response = i2c.readfrom(0x68, 4)
        checksum = sum(response[:3])
        for i in range(4):
            print(response[i])
        print(checksum)
        print((response[1] << 8) | response[2])
        print()
        time.sleep_ms(2000)
    except:
        print("error")
        time.sleep_ms(2000)