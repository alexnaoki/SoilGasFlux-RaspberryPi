from time import sleep_ms

_MAX_RETRIES = 3

class K30:
    def __init__(self, i2c_bus, addr=0x68):
        self.i2c = i2c_bus
        self.addr = addr
        
    def read_value(self):
        for attempt in range(_MAX_RETRIES):
            try:
                self.i2c.writeto(self.addr, bytes([0x22, 0x00, 0x08, 0x2A]))
                sleep_ms(30)

                response = bytearray(4)
                self.i2c.readfrom_into(self.addr, response)
                sleep_ms(20)

                checksum = sum(response[:3])
                if checksum != response[3]:
                    print(f'K30 CRC error (attempt {attempt + 1}/{_MAX_RETRIES})')
                    sleep_ms(50)
                    continue
                return (response[1] << 8) | response[2]
            except OSError as e:
                print(f'K30 I2C error (attempt {attempt + 1}/{_MAX_RETRIES}): {e}')
                sleep_ms(50)
        # All retries exhausted
        return (response[1] << 8) | response[2]
        