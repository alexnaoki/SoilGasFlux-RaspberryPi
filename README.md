# SoilGasFlux-RaspberryPi
Soil gas flux (CO2) code for sampling in-situ using low-cost sensors (Raspberry Pi Pico W)


---------------
## Usage
### Sequence of events
#### Before initialization
1. Open /aux/create_config.py and make the necessary changes in the 'USER INPUT' section
2. Then, run file.

#### Sequence
After a restart or an initialization, the main.py runs
    1. Reads config.json file created on the previous step
    2. Initialize components (SD card and RTC)
    3. Initialize Motor
    4. Initialize Sensors
    5. Check chamber position and opens till it hits the top limit switch
        - While the limit switch is not pressed, the code stays in a loop waiting the motor_next_action
    6.
