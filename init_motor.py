import machine, time, os, json, uos

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
        
        self.pwma = machine.PWM(machine(self.config['motor']['pwma']))
        self.pwma.freq(1000)
        
        # return self.ai01, self.ai02
            
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
    