import components.ssd1306 as ssd1306
from machine import I2C, Pin, SoftI2C  

print('Teste')
i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)

print(i2c.scan())

display = ssd1306.SSD1306_I2C(128, 64, i2c)
display.fill(0)
display.text('Hello Yellow!',0,0)
display.show()