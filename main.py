import machine, os, time
from meteo_pico import Meteo_Pico

# LED = machine.Pin(25, machine.Pin.OUT)

# RESET_CAUSE = {
#     'PWRON_RESET': 1,
#     'HARD_RESET': 2,
#     'WDT_RESET': 3,
#     'DEEPSLEEP_RESET': 4,
#     'SOFT_RESET': 5,
# }
# import machine
# led = machine.Pin("LED", machine.Pin.OUT)
# led.off()
# led.on()
# relay = machine.Pin(15, machine.Pin.OUT)

led = machine.Pin("LED", machine.Pin.OUT)
button01 = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)


print('start')
while True:
    if button01.value() == 1:
        led.on()
    elif button01.value() == 0:
        led.off()
    # led.on()
    time.sleep(0.1)

# for _ in range(5):
#     try:
#         a = Meteo_Pico()
#         a.set_SDCard(gpio_cs=17, gpio_sck=18, gpio_di=19, gpio_do=16)
#         time.sleep(1)
#         break

#     except Exception as error:
#         print(error)
#         led.on()
#         time.sleep(1)
#         machine.reset()

# print('FINISH')