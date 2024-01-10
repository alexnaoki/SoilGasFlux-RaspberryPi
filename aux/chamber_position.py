import machine

'''

'''
class ChamberPosition:
    def __init__(self, limit_switch_bot, limit_switch_top):
        # limit_swiches_CONFIG = config['limit_swiches']
        # relays_CONFIG = config['relays']
        
        # self.limit_switch_BOTTOM = machine.Pin(limit_swiches_CONFIG['bottom'], machine.Pin.IN)
        # self.limit_switch_TOP = machine.Pin(limit_swiches_CONFIG['top'], machine.Pin.IN)
        self.limit_switch_BOTTOM = limit_switch_bot
        self.limit_switch_TOP = limit_switch_top
        

    def check_limit_switches(self):
        if self.limit_switch_BOTTOM.value() == 1:
            return 'bottom'
        elif self.limit_switch_TOP.value() == 1:
            return 'top'
        else:
            return None

    # def from_restart(self):
    #     limit_switch_STATE = self.check_limit_switches()
        
    #     if limit_switch_STATE != None:
    #         return limit_switch_STATE
    #     else:
    #         pass
        
        