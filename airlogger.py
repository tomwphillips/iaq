def read_sensor(sensor):
    pm_sizes = [1.0, 2.5, 10.0]
    reading = sensor.read()
    return {pm_size: reading.pm_ug_per_m3(pm_size) for pm_size in pm_sizes}
