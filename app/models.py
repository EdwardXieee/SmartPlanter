from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fog_devices = db.relationship('FogDevice', backref='user', lazy=True)
    
    def get_id(self):
        return str(self.user_id)

class FogDevice(db.Model):
    __tablename__ = 'fog_devices'
    
    fog_device_id = db.Column(db.Integer, primary_key=True)
    fog_device_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='offline')
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LightIntensity(db.Model):
    __tablename__ = 'light_intensity'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.String(50), nullable=False)
    light_value = db.Column(db.Float, nullable=False)
    measured_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AirTemperature(db.Model):
    __tablename__ = 'air_temperature'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.String(50), nullable=False)
    temperature_value = db.Column(db.Float, nullable=False)
    measured_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AirHumidity(db.Model):
    __tablename__ = 'air_humidity'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.String(50), nullable=False)
    humidity_value = db.Column(db.Float, nullable=False)
    measured_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AirPressure(db.Model):
    __tablename__ = 'air_pressure'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.String(50), nullable=False)
    pressure_value = db.Column(db.Float, nullable=False)
    measured_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SoilMoisture(db.Model):
    __tablename__ = 'soil_moisture'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.String(50), nullable=False)
    moisture_value = db.Column(db.Float, nullable=False)
    measured_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlantHealth(db.Model):
    __tablename__ = 'plant_health'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='healthy')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlantLightNeeded(db.Model):
    __tablename__ = 'plant_light_needed'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.Integer, nullable=False)
    light_needed = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlantWateringNeeded(db.Model):
    __tablename__ = 'plant_watering_needed'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0)  # 0: need watering, 1: no need
    water_needed = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherForecast(db.Model):
    __tablename__ = 'weather_forcast'
    
    id = db.Column(db.Integer, primary_key=True)
    fog_device_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0)  # 0, 1, 2: bigger number, worse weather
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 