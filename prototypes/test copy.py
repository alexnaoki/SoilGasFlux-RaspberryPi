from machine import Pin , PWM
from utime import sleep

led = Pin(25,Pin.OUT)
ina1 = Pin(13,Pin.OUT)
ina2 = Pin(14, Pin.OUT)
pwma = PWM(Pin(15))

pwma.freq(1000)

led.toggle()


def RotateCW(duty):
    ina1.value(1)
    ina2.value(0)
    duty_16 = int((duty*65536)/100)
    pwma.duty_u16(duty_16)

def RotateCCW(duty):
    ina1.value(0)
    ina2.value(1)
    duty_16 = int((duty*65536)/100)
    pwma.duty_u16(duty_16)
    
def StopMotor():
    ina1.value(0)
    ina2.value(0)
    pwma.duty_u16(0)
    

while True:
    # duty_cycle=float(input("Enter pwm duty cycle"))
    duty_cycle = 100
    print (duty_cycle)
    RotateCW(duty_cycle)
    print('here')
    sleep(10)
    print('here2')
    RotateCCW(duty_cycle)
    sleep(10)
    # StopMotor()