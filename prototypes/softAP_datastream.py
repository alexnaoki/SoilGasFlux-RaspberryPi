from softAP import SoftAP
from meteo_pico import Meteo_Pico


sensors = Meteo_Pico()
ap = SoftAP(ssid='test_name', password='PASSWORD')

sensors.set_PressureSensor(gpio_scl=1, gpio_sda=0)

ap.run(sensor=sensors)
