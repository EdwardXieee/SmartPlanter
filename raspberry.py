import serial
import time
from datetime import datetime
import threading
import requests
from enum import Enum
from collections import deque
import random
import board
import busio
import RPi.GPIO as GPIO
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_tcs34725

# =========================
# Configuration Parameters
# =========================

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
DEVICE_ID = "raspberry-01"

# =========================
# Define Sensor Types and Corresponding API URLs
# =========================

class SensorType(Enum):
    LIGHT = "light_intensity"
    AIR_TEMP = "air_temp"
    AIR_HUMIDITY = "air_humidity"
    AIR_PRESSURE = "air_pressure"
    SOIL_HUMIDITY = "soil_humidity"

API_BASE_URL = "http://172.20.10.4:5001/api"
SENSOR_API_URLS = {
    SensorType.LIGHT: f"{API_BASE_URL}/light",
    SensorType.AIR_TEMP: f"{API_BASE_URL}/air_temp",
    SensorType.AIR_HUMIDITY: f"{API_BASE_URL}/air_humidity",
    SensorType.AIR_PRESSURE: f"{API_BASE_URL}/air_pressure",
    SensorType.SOIL_HUMIDITY: f"{API_BASE_URL}/soil"
}

# =========================
# Initialize Serial Port
# =========================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# =========================
# Initialize I2C Sensors
# =========================

i2c = busio.I2C(board.SCL, board.SDA)

# BME280: For reading ambient temperature, pressure, and humidity
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)  # Adjust the address as needed

# Soil moisture sensor: digital output via GPIO
MOISTURE_SENSOR_DO_PIN = 17  # GPIO17 (physical pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_SENSOR_DO_PIN, GPIO.IN)

moisture_window = deque(maxlen=6)
simulated_moisture = None

# =========================
# Base Function to Send Sensor Data
# =========================

def build_payload(sensor_type: SensorType, edge_device_id: str, value):
    """Build payload data based on the sensor type"""
    base_payload = {
        "fog_device_id": 1,
        "measured_at": datetime.now().isoformat()
    }
    if sensor_type == SensorType.LIGHT:
        base_payload["light_value"] = value
    elif sensor_type == SensorType.AIR_TEMP:
        base_payload["temperature_value"] = value
    elif sensor_type == SensorType.AIR_HUMIDITY:
        base_payload["humidity_value"] = value
    elif sensor_type == SensorType.AIR_PRESSURE:
        base_payload["pressure_value"] = value
    elif sensor_type == SensorType.SOIL_HUMIDITY:
        base_payload["moisture_value"] = value
    return base_payload

def send_sensor_value(sensor_type: SensorType, edge_device_id: str, value):
    """Send sensor data to the cloud via corresponding API URL"""
    payload = build_payload(sensor_type, edge_device_id, value)
    url = SENSOR_API_URLS[sensor_type]
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Successfully sent to cloud:", payload)
        else:
            print("Failed to send to cloud, status code:", response.status_code)
    except Exception as e:
        print("HTTP error:", e)

# =========================
# Functions for Sending Each Sensor's Data
# =========================

def send_time_and_date():
    """Send current time and date to micro:bit"""
    now = datetime.now()
    time_str = now.strftime("T:%H:%M")
    date_str = now.strftime("D:%m-%d-%Y")
    ser.write((time_str + "\n").encode())
    print("Sent time:", time_str)
    time.sleep(1)
    ser.write((date_str + "\n").encode())
    print("Sent date:", date_str)

def parse_light_value(line):
    """
    Parse edge_device_id and light_value from micro:bit return string
    Example: "DID:EDGE-001;L:320"
    """
    edge_device_id = None
    light_value = None
    try:
        parts = line.split(";")
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "DID":
                    edge_device_id = value
                elif key == "L":
                    light_value = float(value)
    except Exception as e:
        print("Parse error:", e)
    return edge_device_id, light_value

def send_light_data():
    """Read light data from micro:bit and upload"""
    try:
        line = ser.readline().decode().strip()
        if line:
            print("Received from micro:bit:", line)
            edge_device_id, light_value = parse_light_value(line)
            if edge_device_id is not None and light_value is not None:
                send_sensor_value(SensorType.LIGHT, edge_device_id, light_value)
                print("Sent light value:", light_value)
            else:
                print("Missing data fields, skipping send.")
    except Exception as e:
        print("Read error:", e)

def send_air_temp_data():
    """Read BME280 temperature data and upload"""
    temperature = bme280.temperature
    send_sensor_value(SensorType.AIR_TEMP, "env-01", temperature)
    print(f"Sent BME280 temperature: {temperature}")

def send_air_humidity_data():
    """Read BME280 humidity data and upload"""
    humidity = bme280.humidity
    send_sensor_value(SensorType.AIR_HUMIDITY, "env-01", humidity)
    print(f"Sent BME280 humidity: {humidity}")

def send_air_pressure_data():
    """Read BME280 pressure data and upload"""
    pressure = bme280.pressure
    send_sensor_value(SensorType.AIR_PRESSURE, "env-01", pressure)
    print(f"Sent BME280 pressure: {pressure}")

def update_simulated_moisture_from_window(window):
    """Generate simulated soil moisture value based on recent readings"""
    wet_count = window.count('wet')
    if wet_count >= 5:
        return random.randint(80, 95)
    elif wet_count >= 4:
        return random.randint(65, 80)
    elif wet_count >= 3:
        return random.randint(50, 65)
    elif wet_count >= 2:
        return random.randint(35, 50)
    elif wet_count >= 1:
        return random.randint(20, 35)
    else:
        return random.randint(5, 20)

def send_soil_humidity_data():
    """Read and simulate soil moisture data and upload"""
    moisture_status = GPIO.input(MOISTURE_SENSOR_DO_PIN)
    if moisture_status == GPIO.HIGH:
        moisture_window.append('dry')
    else:
        moisture_window.append('wet')

    if len(moisture_window) == 6:
        simulated_moisture = update_simulated_moisture_from_window(moisture_window)
        send_sensor_value(SensorType.SOIL_HUMIDITY, "env-01", simulated_moisture)
        print(f"Sent Soil Humidity: {simulated_moisture}")
    else:
        print(f"Soil Moisture = Estimating... ({len(moisture_window)}/6 readings collected)")

def get_health_status():
    """
    Call the API endpoint to get the current plant health status.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health_status/1")
        if response.status_code == 200:
            data = response.json()
            return data.get('plant_health_status', 'unknown')
        else:
            print("Failed to get health status, status code:", response.status_code)
            return None
    except Exception as e:
        print("Error getting health status:", e)
        return None

def send_health_status():
    """
    Get health status and send it to micro:bit via serial.
    """
    status = get_health_status()
    if status is not None:
        message = f"H:{status}\n"
        ser.write(message.encode())
        print("Sent health status to micro:bit:", message)
    else:
        print("Health status not available.")

# =========================
# Multithreading Functions
# =========================

def microbit_light_thread():
    """Thread: Continuously read and send light data from micro:bit"""
    while True:
        send_light_data()
        time.sleep(1)

def environment_data_thread():
    """Thread: Periodically read environmental sensor data and send them"""
    while True:
        send_air_temp_data()
        send_air_humidity_data()
        send_air_pressure_data()
        send_soil_humidity_data()
        time.sleep(5)

def health_status_thread():
    """
    Background thread: periodically get plant health status and send it.
    """
    while True:
        send_health_status()
        time.sleep(60)

def time_sender_thread():
    """Thread: Monitor minute or date change and send time/date"""
    last_minute = None
    last_date = None
    while True:
        now = datetime.now()
        current_minute = now.minute
        current_date = now.date()
        if current_minute != last_minute or current_date != last_date:
            send_time_and_date()
            last_minute = current_minute
            last_date = current_date
        time.sleep(1)

def send_heartbeat():
    """Send heartbeat packet to server"""
    while True:
        try:
            response = requests.post(f"{API_BASE_URL}/devices/heartbeat", json={
                "device_id": DEVICE_ID
            })
            if response.status_code == 200:
                print("Heartbeat sent successfully")
            else:
                print("Heartbeat failed, status code:", response.status_code)
        except Exception as e:
            print("Heartbeat error:", e)
        time.sleep(30)

# =========================
# Main Program Entry Point
# =========================

if __name__ == "__main__":
    try:
        # Start multiple background threads, each responsible for specific data acquisition and transmission tasks
        light_thread = threading.Thread(target=microbit_light_thread, daemon=True)
        env_thread = threading.Thread(target=environment_data_thread, daemon=True)
        time_thread = threading.Thread(target=time_sender_thread, daemon=True)
        heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
        health_thread = threading.Thread(target=health_status_thread, daemon=True)

        light_thread.start()
        env_thread.start()
        time_thread.start()
        health_thread.start()
        heartbeat_thread.start()

        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()
        GPIO.cleanup()
