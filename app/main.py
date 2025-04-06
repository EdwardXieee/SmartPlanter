from flask import Blueprint, render_template, url_for, redirect, abort
from flask_login import login_required, current_user
from app.models import (
    FogDevice, LightIntensity, AirTemperature,
    AirHumidity, AirPressure, SoilMoisture
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
    
    # 确保用户只能访问自己的设备数据
    if device.user_id != current_user.user_id:
        abort(403)
    
    # 获取最新的传感器数据
    current_data = {
        'soil_moisture': SoilMoisture.query.filter_by(fog_device_id=device_id).order_by(SoilMoisture.measured_at.desc()).first(),
        'light': LightIntensity.query.filter_by(fog_device_id=device_id).order_by(LightIntensity.measured_at.desc()).first(),
        'temperature': AirTemperature.query.filter_by(fog_device_id=device_id).order_by(AirTemperature.measured_at.desc()).first(),
        'humidity': AirHumidity.query.filter_by(fog_device_id=device_id).order_by(AirHumidity.measured_at.desc()).first()
    }
    
    # 获取过去24小时的历史数据
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # 获取历史数据
    soil_history = SoilMoisture.query.filter(
        SoilMoisture.fog_device_id == device_id,
        SoilMoisture.measured_at.between(start_time, end_time)
    ).order_by(SoilMoisture.measured_at.asc()).all()
    
    temp_history = AirTemperature.query.filter(
        AirTemperature.fog_device_id == device_id,
        AirTemperature.measured_at.between(start_time, end_time)
    ).order_by(AirTemperature.measured_at.asc()).all()
    
    # 准备图表数据
    history_labels = [data.measured_at.strftime('%H:%M') for data in soil_history]
    history_moisture = [data.moisture_value for data in soil_history]
    history_temp = [data.temperature_value for data in temp_history]
    
    return render_template('main/dashboard.html',
                         device=device,
                         current_data=current_data,
                         history_labels=history_labels,
                         history_temp=history_temp,
                         history_moisture=history_moisture) 