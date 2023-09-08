I2C_SLAVE = 0x0703
CMD_READ_REG = 0x22
REG_CO2_PPM = 0x08

import io
import fcntl

class K30Sensor:
    def __init__(self, bus, addr=0x68):
        self.fr = io.open(bus, "rb", buffering=0)
        self.fw = io.open(bus, "wb", buffering=0)
        
        fcntl.ioctl(self.fr, I2C_SLAVE, addr)
        fcntl.ioctl(self.fw, I2C_SLAVE, addr)
        
    def write(self, *data):
        if type(data) is list or type(data) is tuple:
            data = bytes(data)
        self.fw.write(data)
    
    def read(self, count):
        s = self.fr.read(count)
        l = []
        if len(s) != 0:
            for n in s:
                l.append(ord(n))
        return l
    
    def read_co2_ppm(self):
        checksum = (CMD_READ_REG + REG_CO2_PPM) & 0xFF
        self.write(CMD_READ_REG, 0, REG_CO2_PPM, checksum)

        response = self.read(4)
        return ((response[1] & 0xFF) << 8) | (response[2] & 0xFF)
    
    def close(self):
        self.fw.close()
        self.fr.close()

if __name__ == "__main__":
    """
    Demonstrate the use of the K30Sensor class by simply reading the
    concentration from the sensor, and printing it to the screen.
    """
    with K30Sensor("/dev/i2c-0") as k30:
        print("Concentration of CO2: {} ppm".format(k30.read_co2_ppm()))
