import time
from init_motor import Init_Motor

# Duration in seconds for each movement
CLOSE_TIME = 20
OPEN_TIME = 20

motor = Init_Motor()

print(f'Closing chamber for {CLOSE_TIME}s...')
motor.Rotate('close')
time.sleep(CLOSE_TIME)
motor.Rotate('stop')
print('Chamber closed.')

time.sleep(2)

print(f'Opening chamber for {OPEN_TIME}s...')
motor.Rotate('open')
time.sleep(OPEN_TIME)
motor.Rotate('stop')
print('Chamber opened.')

print('Test complete.')
