from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import (
    FogDevice, LightIntensity, AirTemperature,
    AirHumidity, AirPressure, SoilMoisture
)
from flask_login import login_required, current_user
from flask import abort
import requests
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import plantid
from openai import OpenAI

api = Blueprint('api', __name__)

# Initialize plant identifier
plant_identifier = plantid.PlantIdentifier()

# Deepseek API configuration
client = OpenAI(api_key="sk-76016bb06a4742729b53d09f91d7b756", base_url="https://api.deepseek.com")

def get_plant_care_advice(plant_name, latin_name):
    """Use Deepseek API to get plant care advice"""
    prompt = f"""As a professional horticulturist, please provide detailed care instructions for {plant_name} (Latin name: {latin_name}).
    Please include the following aspects:
    1. Light Requirements
    2. Watering Frequency and Method
    3. Temperature and Humidity Requirements
    4. Soil Selection
    5. Fertilization Guidelines
    6. Common Issues and Solutions
    
    Please use clear and concise language, focusing on key information. Do not use markdown formatting, output plain text only, no **, #, - or other symbols, just natural paragraphs and line breaks."""
    
    try:
        response = client.chat.completions.create(model="deepseek-chat",messages=[
            {"role": "user", "content": prompt}
            ], stream=False)
        return response.choices[0].message.content
    except Exception as e:
        return f"Unable to get care advice: {str(e)}"

@api.route('/identify_plant', methods=['POST'])
@login_required
def identify_plant():
    if 'image' not in request.files:
        return jsonify({'error': 'No image found in upload'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        # Save uploaded image to temp file
        temp_path = os.path.join('/tmp', secure_filename(file.filename))
        file.save(temp_path)
        
        # Read image
        image = cv2.imread(temp_path)
        if image is None:
            return jsonify({'error': 'Unable to read image'}), 400
            
        # Call plant identification
        outputs = plant_identifier.identify(image, topk=5)
        
        # Delete temp file
        os.remove(temp_path)
        
        if outputs['status'] != 0:
            return jsonify({'error': 'Unable to identify the plant'}), 400
            
        # Get best match result
        best_match = outputs['results'][0]
        chinese_name = best_match['chinese_name']
        latin_name = best_match['latin_name']
        probability = best_match['probability']
        
        # Get care advice
        care_advice = get_plant_care_advice(chinese_name, latin_name)
        
        return jsonify({
            'chinese_name': chinese_name,
            'latin_name': latin_name,
            'confidence': probability,
            'care_advice': care_advice
        })
        
    except Exception as e:
        return jsonify({'error': f'Identification failed: {str(e)}'}), 500

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
        return jsonify({'message': 'Light data recorded successfully'}), 200
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
        return jsonify({'message': 'Temperature data recorded successfully'}), 200
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
        return jsonify({'message': 'Humidity data recorded successfully'}), 200
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
        return jsonify({'message': 'Pressure data recorded successfully'}), 200
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
        return jsonify({'message': 'Soil moisture data recorded successfully'}), 200
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
            return jsonify({'message': 'Heartbeat updated successfully'}), 200
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/device/<int:device_id>/current-data')
@login_required
def get_device_current_data(device_id):
    device = FogDevice.query.get_or_404(device_id)
    
    # Ensure user can only access their own device data
    if device.user_id != current_user.user_id:
        abort(403)
    
    # Get latest sensor data
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