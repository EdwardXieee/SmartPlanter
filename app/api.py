from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import (
    FogDevice, LightIntensity, AirTemperature,
    AirHumidity, AirPressure, SoilMoisture
)
from flask_login import login_required, current_user
from flask import abort

api = Blueprint('api', __name__)

@api.route('/light', methods=['POST'])
def record_light():
    data = request.json
    try:
        light_data = LightIntensity(
            fog_device_id=data['fog_device_id'],
            light_value=data['light_value'],
            measured_at=datetime.fromisoformat(data['measured_at'])
        )
        db.session.add(light_data)
        db.session.commit()
        return jsonify({'message': '光照数据记录成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/air_temp', methods=['POST'])
def record_temperature():
    data = request.json
    try:
        temp_data = AirTemperature(
            fog_device_id=data['fog_device_id'],
            temperature_value=data['temperature_value'],
            measured_at=datetime.fromisoformat(data['measured_at'])
        )
        db.session.add(temp_data)
        db.session.commit()
        return jsonify({'message': '温度数据记录成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/air_humidity', methods=['POST'])
def record_humidity():
    data = request.json
    try:
        humidity_data = AirHumidity(
            fog_device_id=data['fog_device_id'],
            humidity_value=data['humidity_value'],
            measured_at=datetime.fromisoformat(data['measured_at'])
        )
        db.session.add(humidity_data)
        db.session.commit()
        return jsonify({'message': '湿度数据记录成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/air_pressure', methods=['POST'])
def record_pressure():
    data = request.json
    try:
        pressure_data = AirPressure(
            fog_device_id=data['fog_device_id'],
            pressure_value=data['pressure_value'],
            measured_at=datetime.fromisoformat(data['measured_at'])
        )
        db.session.add(pressure_data)
        db.session.commit()
        return jsonify({'message': '气压数据记录成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/soil', methods=['POST'])
def record_soil_moisture():
    data = request.json
    try:
        soil_data = SoilMoisture(
            fog_device_id=data['fog_device_id'],
            moisture_value=data['moisture_value'],
            measured_at=datetime.fromisoformat(data['measured_at'])
        )
        db.session.add(soil_data)
        db.session.commit()
        return jsonify({'message': '土壤湿度数据记录成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/devices/heartbeat', methods=['POST'])
def device_heartbeat():
    data = request.json
    try:
        device_id = data['device_id']
        device = FogDevice.query.filter_by(fog_device_name=device_id).first()
        if device:
            device.status = 'online'
            device.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': '心跳包更新成功'}), 200
        return jsonify({'error': '设备不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/device/<int:device_id>/current-data')
@login_required
def get_device_current_data(device_id):
    device = FogDevice.query.get_or_404(device_id)
    
    # 确保用户只能访问自己的设备数据
    if device.user_id != current_user.user_id:
        abort(403)
    
    # 获取最新的传感器数据
    latest_soil = SoilMoisture.query.filter_by(fog_device_id=device_id).order_by(SoilMoisture.measured_at.desc()).first()
    latest_light = LightIntensity.query.filter_by(fog_device_id=device_id).order_by(LightIntensity.measured_at.desc()).first()
    latest_temp = AirTemperature.query.filter_by(fog_device_id=device_id).order_by(AirTemperature.measured_at.desc()).first()
    latest_humidity = AirHumidity.query.filter_by(fog_device_id=device_id).order_by(AirHumidity.measured_at.desc()).first()
    latest_pressure = AirPressure.query.filter_by(fog_device_id=device_id).order_by(AirPressure.measured_at.desc()).first()
    
    return jsonify({
        'soil_moisture': latest_soil.moisture_value if latest_soil else 0,
        'light': latest_light.light_value if latest_light else 0,
        'temperature': latest_temp.temperature_value if latest_temp else 0,
        'humidity': latest_humidity.humidity_value if latest_humidity else 0,
        'pressure': latest_pressure.pressure_value if latest_pressure else 0
    }) 