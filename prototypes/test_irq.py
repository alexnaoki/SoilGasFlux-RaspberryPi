from machine import Pin
from utime import sleep

limit_switch_1 = Pin(15, Pin.OUT)
limit_switch_1.value(1)

limit_switch_2 = Pin(14, Pin.IN, pull=Pin.PULL_DOWN)
limit_switch_3 = Pin(13, Pin.IN, pull=Pin.PULL_DOWN)
limit_switch_3.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, 
                   handler=irq_callback)

relay_1 = Pin(12, Pin.OUT)

def irq_callback(pin=relay_1):
    print('callback')
    relay_1.on()
    

while True:
    sleep(0.5)
    print(limit_switch_1.value(),limit_switch_2.value(), limit_switch_3.value())