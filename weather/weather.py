import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from metar.Metar import Metar
import urllib.request

# Train and save a weather classification model
def train_weather_model(data_path='weather_data.csv', model_path='weather_model.joblib'):
    data = pd.read_csv(data_path)

    # Drop irrelevant column
    data = data.drop(columns=['Date/Time'])

    # Map text weather descriptions to numeric categories
    weather_map = {
        'Mainly Clear': 0,
        'Mostly Cloudy': 0,
        'Cloudy': 0,
        'Clear': 0,
        'Fog': 0,
        'Rain': 1,
        'Rain,Fog': 1,
        'Drizzle,Fog': 1,
        'Snow': 2,
        'Rain Showers': 2
    }
    data['Weather'] = data['Weather'].map(weather_map)
    data = data.dropna(subset=['Weather'])

    # Prepare features and labels
    X = data.drop(columns=['Weather'])
    y = data['Weather']

    # Train a Random Forest Classifier
    model = RandomForestClassifier()
    model.fit(X, y)

    # Save the trained model
    joblib.dump(model, model_path)
    print(f"Weather prediction model saved to {model_path}")

# Fetch real-time METAR weather data from Changi Airport (WSSS)
def get_meteorological_data():
    url = 'https://tgftp.nws.noaa.gov/data/observations/metar/stations/WSSS.TXT'
    raw_data = urllib.request.urlopen(url).read().decode()
    report_line = raw_data.split('\n')[1]
    metar = Metar(report_line)

    wind_speed = metar.wind_speed.value() if metar.wind_speed else -1
    visibility = metar.vis.value() if metar.vis else -1
    dew_point = metar.dewpt.value() if metar.dewpt else -1

    return wind_speed, dew_point, visibility

# Predict weather condition using local and METAR data
def predict_weather(temperature, humidity, pressure, model_path='weather/weather_model.joblib'):
    wind_speed, dew_point, visibility = get_meteorological_data()
    model = joblib.load(model_path)

    # Prepare input in correct order
    input_data = np.array([[temperature, dew_point, humidity, wind_speed, visibility, pressure]])
    prediction = model.predict(input_data)[0]
    return prediction

if __name__ == '__main__':
    # train_weather_model()
    predicted_class = predict_weather(8.2, 76, 100.69)
    print(f"Predicted weather class: {predicted_class}")

"""
Example usage:

train_weather_model()  # Train and save the model

# Predict weather condition with real-time data + local input
predicted_class = predict_weather(8.2, 76, 100.69)
print(f"Predicted weather class: {predicted_class}")
"""
