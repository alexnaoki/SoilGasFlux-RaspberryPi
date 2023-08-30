from machine import Pin
from utime import sleep
import random
import ds18x20


pin = Pin("LED", Pin.OUT)
relay01 = Pin(16, Pin.OUT)
relay02 = Pin(18, Pin.OUT)
relay03 = Pin(19, Pin.OUT)
relay04 = Pin(20, Pin.OUT)

print("LED starts flashing...")
while True:
    #print(random.randint(1, 100))
    # rnd = random.randint(1, 100)
    pin.toggle()
    relay01.value(0)
    relay02.value(0)
    relay03.value(0)
    relay04.value(0)
    sleep(0.2) # sleep 1sec
    relay01.value(1)
    sleep(0.2) # sleep 1sec
    relay02.value(1)
    sleep(0.2) # sleep 1sec
    relay03.value(1)
    sleep(0.2) # sleep 1sec
    relay04.value(1)
    sleep(1)
print('Finish')