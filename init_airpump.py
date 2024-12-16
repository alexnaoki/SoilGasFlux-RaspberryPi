import machine, time, os, json, uos
from prototypes import logging_error

class Init_AirPump:
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
        
        self.bi01 = machine.Pin(self.config['motor']['bi01'], machine.Pin.OUT)
        self.bi02 = machine.Pin(self.config['motor']['bi02'], machine.Pin.OUT)
        self.pwmb_gpio = machine.Pin(self.config['motor']['pwmb'])
        
        self.pwma = machine.PWM(self.pwma_gpio)
        self.pwma.freq(1000)
        
        self.pwmb = machine.PWM(self.pwmb_gpio)
        self.pwmb.freq(1000)
        
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
            self.ai01.value(1)
            self.ai02.value(0)
            duty = 50
            duty_16 = int((duty*65536)/100)
            self.pwma.duty_u16(duty_16)
        elif direction == 'other_motor':
            self.bi01.value(1)
            self.bi02.value(0)
            duty = 100
            duty_16 = int((duty*65536)/100)
            self.pwmb.duty_u16(duty_16)
            
        else:
            self.ai01.value(0)
            self.ai02.value(0)
            self.pwma.duty_u16(0)
            
            self.bi01.value(0)
            self.bi02.value(0)
            self.pwma.duty_u16(0)