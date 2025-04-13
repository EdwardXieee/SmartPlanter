import math
import datetime

# Set the base timestamp
start_time = datetime.datetime(2025, 4, 8, 0, 0, 0)

# Function to generate INSERT SQL statements
def generate_insert(table_name, col_name, value_func, value_format="{:.1f}"):
    stmt = f"INSERT INTO `{table_name}` (fog_device_id, {col_name}, measured_at) VALUES\n"
    values = []
    for i in range(100):
        measured_at = start_time + datetime.timedelta(hours=i)
        value = value_func(i, measured_at)
        values.append(f"(1, {value_format.format(value)}, '{measured_at}')")
    stmt += ",\n".join(values) + ";\n"
    return stmt

# Simulated data generation functions
def calc_humidity(i, dt):
    return 55 + 15 * math.sin(2 * math.pi * i / 24)

def calc_temperature(i, dt):
    return 25 + 5 * math.sin(2 * math.pi * i / 24)

def calc_pressure(i, dt):
    return 101 + 0.5 * math.sin(2 * math.pi * i / 24)

def calc_soil_moisture(i, dt):
    return 50 + 20 * math.sin(2 * math.pi * i / 24)

def calc_light_intensity(i, dt):
    hour = dt.hour
    if 6 <= hour <= 18:
        return round(4000 * math.sin(math.pi * (hour - 6) / 12))
    else:
        return 0

# Generate all SQL insert statements
sql_statements = [
    ("-- air_humidity", generate_insert("air_humidity", "humidity_value", calc_humidity)),
    ("-- air_temperature", generate_insert("air_temperature", "temperature_value", calc_temperature)),
    ("-- air_pressure", generate_insert("air_pressure", "pressure_value", calc_pressure)),
    ("-- soil_moisture", generate_insert("soil_moisture", "moisture_value", calc_soil_moisture)),
    ("-- light_intensity", generate_insert("light_intensity", "light_value", calc_light_intensity, value_format="{}")),
]

# Print all SQL for direct copy-paste
for comment, sql in sql_statements:
    print(comment)
    print(sql)
