from machine import Pin
from utime import sleep

limit_switch_1 = Pin(11, Pin.OUT)
limit_switch_2 = Pin(12, Pin.OUT)

limit_switch_1.value(1)
limit_switch_2.value(1)
def irq_callback(pin):
    print('callback')
    # relay_1.on()
# limit_switch_2 = Pin(14, Pin.IN, pull=Pin.PULL_DOWN)
limit_switch_3 = Pin(9, Pin.IN, pull=Pin.PULL_DOWN)
limit_switch_3.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, 
                   handler=irq_callback)

# relay_1 = Pin(12, Pin.OUT)


    

while True:
    sleep(0.5)
    print(limit_switch_3.value())