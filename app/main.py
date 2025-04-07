from flask import Blueprint, render_template, url_for, redirect, abort
from flask_login import login_required, current_user
from app.models import (
    FogDevice, LightIntensity, AirTemperature,
    AirHumidity, AirPressure, SoilMoisture,
    PlantHealth, PlantLightNeeded, PlantWateringNeeded, WeatherForecast
)
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    fog_devices = FogDevice.query.filter_by(user_id=current_user.user_id).all()
    return render_template('main/index.html', fog_devices=fog_devices)

@main.route('/device/<int:device_id>')
@login_required
def device_dashboard(device_id):
    device = FogDevice.query.get_or_404(device_id)
    
    # Ensure user can only access their own device data
    if device.user_id != current_user.user_id:
        abort(403)
    
    # Get latest sensor data
    current_data = {
        'soil_moisture': SoilMoisture.query.filter_by(fog_device_id=device_id).order_by(SoilMoisture.measured_at.desc()).first(),
        'light': LightIntensity.query.filter_by(fog_device_id=device_id).order_by(LightIntensity.measured_at.desc()).first(),
        'temperature': AirTemperature.query.filter_by(fog_device_id=device_id).order_by(AirTemperature.measured_at.desc()).first(),
        'humidity': AirHumidity.query.filter_by(fog_device_id=device_id).order_by(AirHumidity.measured_at.desc()).first(),
        'pressure': AirPressure.query.filter_by(fog_device_id=device_id).order_by(AirPressure.measured_at.desc()).first()
    }
    
    # Get historical data for the past 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # Get historical data for each sensor
    soil_history = SoilMoisture.query.filter(
        SoilMoisture.fog_device_id == device_id,
        SoilMoisture.measured_at.between(start_time, end_time)
    ).order_by(SoilMoisture.measured_at.asc()).all()
    
    temp_history = AirTemperature.query.filter(
        AirTemperature.fog_device_id == device_id,
        AirTemperature.measured_at.between(start_time, end_time)
    ).order_by(AirTemperature.measured_at.asc()).all()
    
    humidity_history = AirHumidity.query.filter(
        AirHumidity.fog_device_id == device_id,
        AirHumidity.measured_at.between(start_time, end_time)
    ).order_by(AirHumidity.measured_at.asc()).all()
    
    pressure_history = AirPressure.query.filter(
        AirPressure.fog_device_id == device_id,
        AirPressure.measured_at.between(start_time, end_time)
    ).order_by(AirPressure.measured_at.asc()).all()
    
    light_history = LightIntensity.query.filter(
        LightIntensity.fog_device_id == device_id,
        LightIntensity.measured_at.between(start_time, end_time)
    ).order_by(LightIntensity.measured_at.asc()).all()
    
    # Prepare chart data - use soil_history for the time labels
    history_labels = [data.measured_at.strftime('%H:%M') for data in soil_history] if soil_history else []
    
    # Prepare data for each sensor
    history_moisture = [data.moisture_value for data in soil_history]
    history_temp = [data.temperature_value for data in temp_history]
    history_humidity = [data.humidity_value for data in humidity_history]
    history_pressure = [data.pressure_value for data in pressure_history]
    history_light = [data.light_value for data in light_history]
    
    return render_template('main/dashboard.html',
                         device=device,
                         current_data=current_data,
                         history_labels=history_labels,
                         history_temp=history_temp,
                         history_moisture=history_moisture,
                         history_humidity=history_humidity,
                         history_pressure=history_pressure,
                         history_light=history_light) 