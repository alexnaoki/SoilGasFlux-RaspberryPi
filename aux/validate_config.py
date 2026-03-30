"""Validate config.json structure and values for RP2040 hardware."""

_VALID_GPIO_RANGE = range(0, 29)  # GP0–GP28

_REQUIRED_KEYS = {
    'relays': ['relay01', 'relay02'],
    'rtc': ['sda', 'scl'],
    'sd_card': ['cs', 'sck', 'tx', 'rx'],
    'i2c_sensor': ['sda', 'scl'],
    'buttons': ['button01', 'button02', 'button03'],
    'motor': ['ai01', 'ai02', 'pwma'],
    'timeLimits': ['maxTime_chamber_OPEN', 'maxTime_chamber_CLOSE', 'maxTime_motor_ON'],
    'start_time': ['year', 'month', 'day', 'hour', 'minute', 'second', 'sync'],
}


def validate_config(config):
    """Validate config dict. Returns list of error strings (empty = OK)."""
    errors = []

    # Check required top-level keys and sub-keys
    for section, keys in _REQUIRED_KEYS.items():
        if section not in config:
            errors.append(f'Missing section: {section}')
            continue
        for key in keys:
            if key not in config[section]:
                errors.append(f'Missing key: {section}.{key}')

    # Validate GPIO pin numbers
    gpio_sections = ['relays', 'buttons', 'motor', 'rtc', 'sd_card', 'i2c_sensor']
    for section in gpio_sections:
        if section not in config:
            continue
        for key, val in config[section].items():
            if isinstance(val, int) and val not in _VALID_GPIO_RANGE:
                errors.append(f'Invalid GPIO {section}.{key}={val} (must be 0-28)')

    # Validate timing limits are positive
    if 'timeLimits' in config:
        for key, val in config['timeLimits'].items():
            if isinstance(val, (int, float)) and val <= 0:
                errors.append(f'Invalid timing {key}={val} (must be > 0)')

    # Check id_sensor exists
    if 'id_sensor' not in config:
        errors.append('Missing key: id_sensor')

    return errors
