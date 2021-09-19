def create_table(db):
    cursor = db.cursor()
    cursor.execute("""
        create table readings (
            'pm1_ug_per_m3' real,
            'pm25_ug_per_m3' real,
            'pm10_ug_per_m3' real
        )
    """)

def read_sensor(sensor):
    pm_sizes = [1.0, 2.5, 10.0]
    reading = sensor.read()
    return {pm_size: reading.pm_ug_per_m3(pm_size) for pm_size in pm_sizes}

def record_reading(db, reading):
    cursor = db.cursor()
    cursor.execute("insert into readings values (?, ?, ?)", tuple(reading.values()))
