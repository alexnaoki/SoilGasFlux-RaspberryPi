import machine, os, time, json
from meteo_pico import Meteo_Pico
from init_motor import Init_Motor
from init_sd_rtc import Init_SD_RTC

os.chdir('/')

with open('config.json', 'r') as f:
    config_file = f.read()
    config = json.loads(config_file)

led = machine.Pin(25, machine.Pin.OUT)

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

# led = machine.Pin("LED", machine.Pin.OUT)
# button01 = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)

motor = Init_Motor()
#############################
print('SENSORS:')
sensors = Init_Sensors()
pressure_sensor = sensors.set_PressureSensor()
temp_hum_sensor = sensors.set_TempAndHumidity()
co2_sensor = sensors.set_k30()





while True:
    time.sleep(0.5)
    print('nada')

    motor.Rotate_ButtonControl(b1.value(), b2.value())



