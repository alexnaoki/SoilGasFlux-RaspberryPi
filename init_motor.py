import machine, time, os, json, uos
from prototypes import logging_error

class Init_Motor:
    def __init__(self):
        print('Initialize Motor')
        
        os.chdir('/')
        
        with open('config.json', 'r') as f:
            config_file = f.read()
            self.config = json.loads(config_file)
            
        # led = machine.Pin()
        self.ai01 = machine.Pin(self.config['motor']['ai01'], machine.Pin.OUT)
        self.ai02 = machine.Pin(self.config['motor']['ai02'], machine.Pin.OUT)
        self.pwma_gpio = machine.Pin(self.config['motor']['pwma'])
        
        self.pwma = machine.PWM(self.pwma_gpio)
        self.pwma.freq(1000)
        
        # return self.ai01, self.ai02
    
    @logging_error.log_errors_to_file('error.log')
    def Rotate_ButtonControl(self, b1, b2):
        self.ai01.value(b1)
        self.ai02.value(b2)
        duty = 100
        duty_16 = int((duty*65536)/100)
        self.pwma.duty_u16(duty_16)
        
        if b1 == b2:
            self.ai01.value(0)
            self.ai02.value(0)
            self.pwma.duty_u16(0)
        else:
            self.ai01.value(b1)
            self.ai02.value(b2)
            duty = 100
            duty_16 = int((duty*65536)/100)
            self.pwma.duty_u16(duty_16)
    
    @logging_error.log_errors_to_file('error.log')
    def Rotate(self, direction):
        if direction == 'open':
            self.ai01.value(1)
            self.ai02.value(0)
            duty = 100
            duty_16 = int((duty*65536)/100)
            self.pwma.duty_u16(duty_16)
        elif direction == 'close':
            self.ai01.value(0)
            self.ai02.value(1)
            duty = 100
            duty_16 = int((duty*65536)/100)
            self.pwma.duty_u16(duty_16)
        else:
            self.ai01.value(0)
            self.ai02.value(0)
            self.pwma.duty_u16(0)