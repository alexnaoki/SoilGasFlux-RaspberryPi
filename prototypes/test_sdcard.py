import machine, os
from components.sdcard import SDCard
import uos


# SD Card Pins
chipselect_sdcard = machine.Pin(17, machine.Pin.OUT)
spiClock_sdcard = machine.Pin(18)
dataIn_sdcard = machine.Pin(19)
dataOut_sdcard = machine.Pin(16)

# Initialiaze SPI peripheral (start with 1MHz)
spi_sdcard = machine.SPI(0,
                         baudrate=1000000,
                         polarity=0,
                         phase=0,
                         bits=8,
                         firstbit=machine.SPI.MSB,
                         sck=spiClock_sdcard,
                         mosi=dataIn_sdcard,
                         miso=dataOut_sdcard)

# Initialize SD card
sd = SDCard(spi=spi_sdcard, cs=chipselect_sdcard)

# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

# Create a file and write something
with open('/sd/text01.txt', 'w') as file:
    file.write('Hello, SD World!\r\n')
    file.write('This is a test\r\n')
    
# Read file just created
with open('/sd/text01.txt', 'r') as file:
    data = file.read()
    print(data)