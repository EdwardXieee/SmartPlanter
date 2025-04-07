from datetime import datetime, timedelta
from app import db
from app.models import FogDevice
from threading import Thread
import time
from health.health import predict_health
from light.light import predict_light
from watering.watering import predict_watering_needs
from weather.weather import predict_weather

def check_device_status():
    """
    检查设备状态的定时任务
    如果设备在60秒内没有发送心跳包，则将其状态设置为离线
    """
    timeout = datetime.utcnow() - timedelta(seconds=60)
    offline_devices = FogDevice.query.filter(
        FogDevice.status == 'online',
        FogDevice.updated_at < timeout
    ).all()
    
    for device in offline_devices:
        device.status = 'offline'
    
    if offline_devices:
        db.session.commit()
        print(f"已将 {len(offline_devices)} 个设备标记为离线状态")

class PredictionTask:
    def __init__(self, interval=300):  # Default interval: 5 minutes
        self.interval = interval
        self.thread = None
        self.running = False

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.thread = Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        while self.running:
            try:
                self._predict_all_devices()
            except Exception as e:
                print(f"Error in prediction task: {str(e)}")
            time.sleep(self.interval)

    def _predict_all_devices(self):
        # Get all online devices
        devices = FogDevice.query.filter_by(status='online').all()
        
        for device in devices:
            try:
                # Get latest sensor data
                latest_soil = SoilMoisture.query.filter_by(fog_device_id=device.fog_device_id)\
                    .order_by(SoilMoisture.measured_at.desc()).first()
                latest_light = LightIntensity.query.filter_by(fog_device_id=device.fog_device_id)\
                    .order_by(LightIntensity.measured_at.desc()).first()
                latest_temp = AirTemperature.query.filter_by(fog_device_id=device.fog_device_id)\
                    .order_by(AirTemperature.measured_at.desc()).first()
                latest_humidity = AirHumidity.query.filter_by(fog_device_id=device.fog_device_id)\
                    .order_by(AirHumidity.measured_at.desc()).first()
                latest_pressure = AirPressure.query.filter_by(fog_device_id=device.fog_device_id)\
                    .order_by(AirPressure.measured_at.desc()).first()

                if not all([latest_soil, latest_light, latest_temp, latest_humidity, latest_pressure]):
                    continue

                # 1. Predict plant health
                health_status = predict_health(
                    latest_soil.moisture_value,
                    latest_temp.temperature_value,
                    latest_temp.temperature_value,
                    latest_humidity.humidity_value,
                    latest_light.light_value
                )
                health_record = PlantHealth(
                    fog_device_id=device.fog_device_id,
                    status='healthy' if health_status == 1 else 'unhealthy',
                    created_at=datetime.utcnow()
                )
                db.session.add(health_record)

                # 2. Predict light needs
                light_needed = predict_light(
                    latest_soil.moisture_value,
                    latest_temp.temperature_value
                )
                light_record = PlantLightNeeded(
                    fog_device_id=device.fog_device_id,
                    light_needed=light_needed,
                    created_at=datetime.utcnow()
                )
                db.session.add(light_record)

                # 3. Predict watering needs
                watering_needed, water_amount = predict_watering_needs(
                    latest_soil.moisture_value,
                    latest_light.light_value,
                    latest_temp.temperature_value,
                    latest_humidity.humidity_value
                )
                watering_record = PlantWateringNeeded(
                    fog_device_id=device.fog_device_id,
                    status=0 if watering_needed else 1,
                    water_needed=water_amount,
                    created_at=datetime.utcnow()
                )
                db.session.add(watering_record)

                # 4. Predict weather
                weather_status = predict_weather(
                    latest_temp.temperature_value,
                    latest_humidity.humidity_value,
                    latest_pressure.pressure_value
                )
                weather_record = WeatherForecast(
                    fog_device_id=device.fog_device_id,
                    status=weather_status,
                    created_at=datetime.utcnow()
                )
                db.session.add(weather_record)

                # Commit all changes
                db.session.commit()

            except Exception as e:
                print(f"Error predicting for device {device.fog_device_id}: {str(e)}")
                db.session.rollback()

# Create a global instance
prediction_task = PredictionTask() 