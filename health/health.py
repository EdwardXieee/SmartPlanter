import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Train and save the XGBoost model
def train_health_model(data_path='plant_health_data.csv', model_path='health_model.json'):
    data = pd.read_csv(data_path)

    # Drop unused features
    data = data.drop(columns=[
        'Timestamp', 'Plant_ID', 'Soil_pH', 'Nitrogen_Level',
        'Phosphorus_Level', 'Potassium_Level',
        'Electrochemical_Signal', 'Chlorophyll_Content'
    ])

    # Encode labels: Healthy, Unhealthy, etc.
    encoder = LabelEncoder()
    data['Plant_Health_Status'] = encoder.fit_transform(data['Plant_Health_Status'])
    labels = data['Plant_Health_Status']
    features = data.drop(columns='Plant_Health_Status')

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # Train XGBoost model
    model = XGBClassifier(objective='multi:softmax', num_class=3, eval_metric='mlogloss', use_label_encoder=False)
    model.fit(X_train, y_train)

    # Save model to file
    model.save_model(model_path)
    print(f"XGBoost model saved to {model_path}")

# Predict plant health status based on sensor input
def predict_health(soil_moisture, ambient_temperature, soil_temperature, humidity, light_intensity, model_path='health/health_model.json'):
    model = XGBClassifier()
    model.load_model(model_path)

    input_data = np.array([[soil_moisture, ambient_temperature, soil_temperature, humidity, light_intensity]])
    prediction = model.predict(input_data)[0]
    return prediction

if __name__ == '__main__':
    # train_health_model()
    result = predict_health(33.5, 26.3, 23.1, 69.6, 884.7)
    print(f"Prediction label: {result}")

"""
Example usage:

train_health_model()  # Train and save the model

# Make a prediction
result = predict_health(33.5, 26.3, 23.1, 69.6, 884.7)
print(f"Prediction label: {result}")
"""
