from time import sleep_ms

class K30:
    def __init__(self, i2c_bus, addr=0x68):
        self.i2c = i2c_bus
        self.addr = addr
        
    def read_value(self):
        self.i2c.writeto(self.addr, bytes([0x22, 0x00, 0x08, 0x2A]))
        sleep_ms(30)
        
        # bytearray
        #TODO use to read to buffer instead of readfrom
        response = bytearray(4)
        response_1 = self.i2c.readfrom_into(self.addr, response)
        # sleep_ms(20)
        checksum = sum(response[:3])
        if checksum != response[3]:
            # raise OSError('K30 CRC error')
            print('K30 CRC error, oserror')
        return (response[1] << 8) | response[2]
        