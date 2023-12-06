import machine
import time


led = machine.Pin('LED', machine.Pin.OUT)
button01 = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)

led.value(1)
print(led.value())
time.sleep(3)
print('toggling')
# led.toggle()

while True:
    print(led.value())
    if button01.value() == 1:
        led.on()
    elif button01.value() == 0:
        led.off()
    # led.on()
    time.sleep(1)
    # led.off()
    # time.sleep(1)
    


# limit_switch_1 = machine.Pin(0, machine.Pin.OUT)
# limit_switch_1.value(1)
# limit_switch_2 = machine.Pin(1, machine.Pin.IN,pull=machine.Pin.PULL_DOWN)

# relay = machine.Pin(2, machine.Pin.OUT)


# while True:
#     time.sleep(1)
#     print(limit_switch_1.value())
#     print(limit_switch_2.value())
#     print()
    # if limit_switch_2.value() == 0:
    #     relay.on()
    # elif limit_switch_2.value() == 1:
    #     relay.off()
    # relay.toggle()

# while True:
#     relay.on()
#     time.sleep(1)
#     relay.off()
#     time.sleep(1)