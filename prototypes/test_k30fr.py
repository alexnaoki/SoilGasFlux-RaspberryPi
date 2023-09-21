from machine import Pin, I2C, SoftI2C
import time

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
# i2c = SoftI2C(scl=Pin(1), sda=Pin(0), freq=100000)
print(i2c.scan())
print(0x68)
# for i in range(100):
while True:
    try:
        i2c.writeto(0x68, bytes([0x22, 0x00, 0x08, 0x2A]))
        time.sleep_ms(30)
        response = bytearray(4)
        response_1 = i2c.readfrom_into(0x68, response)
        checksum = sum(response[:3])
        print()
        print(response)
        print()
        # for i in range(4):
        #     print(response[i])
        print()
        print(checksum, response[3])
        print((response[1] << 8) | response[2])
        print()
        time.sleep_ms(1000)
    except Exception as error:
        print(error)
        print("error")
        time.sleep_ms(1000)