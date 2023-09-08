import math

class RH_to_WaterVaporMoleFraction:
    #from chatgpt
    def __init__(self, rh, total_pressure, air_temperature)
        # self.rh = rh    # Relative humidity (-) between 0 and 1
        # self.total_pressure = total_pressure    # Total pressure (kPa)
        # self.air_temperature = air_temperature  # Air temperature (°C)
        
        sat_vaporpressure = self._calculate_SaturatedVaporPressureOfWater(air_temperature=air_temperature)
        air_vaporpressure = rh*sat_vaporpressure
        
        water_vapor_mole_fraction = rh * air_vaporpressure/total_pressure
        
        return water_vapor_mole_fraction
    
    def _calculate_SaturatedVaporPressureOfWater(self, air_temperature):
        # Tetens equation (kPa)
        P_Tetens = 0.61078*math.e**((17.27*air_temperature)/(air_temperature+237.3))
        
        #Buck equation (kPa)
        P_Buck = 0.61121*math.e**((18.678-air_temperature/234.5)*(air_temperature/(257.14+air_temperature)))
        
        return P_Buck
    
    