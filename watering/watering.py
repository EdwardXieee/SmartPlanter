import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

# Train and save model directly from CSV file
def train_watering_model(file_path='watering_needs.txt', model_path='model.pkl'):
    try:
        # Load dataset and select necessary columns
        data = pd.read_csv(file_path)
        selected_columns = ['Soil_Moisture', 'Ambient_Temperature', 'Humidity', 'Light_Intensity', 'Plant_Health_Status']
        data = data[selected_columns]
    except FileNotFoundError:
        print(f"File not found at path: {file_path}")
        return

    # Label encoding: Healthy -> 1, others -> 0
    data['Plant_Health_Status'] = np.where(data['Plant_Health_Status'] == 'Healthy', 1, 0)

    # Features and target
    X = data[['Soil_Moisture', 'Ambient_Temperature', 'Humidity', 'Light_Intensity']]
    y = data['Plant_Health_Status']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)

    # Train Random Forest model
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X_train, y_train)

    # Save model
    joblib.dump(rf_classifier, model_path)
    print(f"Model saved to: {model_path}")

# Predict whether watering is needed
def predict_watering_needs(soil_moisture, light_intensity, ambient_temperature, humidity, model_path='model.pkl'):
    rf_classifier = joblib.load(model_path)
    input_data = pd.DataFrame({
        'Soil_Moisture': [soil_moisture],
        'Ambient_Temperature': [ambient_temperature],
        'Humidity': [humidity],
        'Light_Intensity': [light_intensity]
    })

    prediction = rf_classifier.predict(input_data)[0]
    probability = rf_classifier.predict_proba(input_data)[0][1]
    prediction = prediction if probability > 0.5 else 1 - prediction

    # Estimate required watering amount
    min_threshold = 29.90
    max_threshold = 39.52
    if soil_moisture < min_threshold:
        interval = min_threshold - soil_moisture
    elif soil_moisture > max_threshold:
        interval = 0
    else:
        interval = 0

    return prediction, interval

if __name__ == '__main__':
    train_watering_model()

"""
Example usage:
train_model_from_csv("your_dataset.csv")

prediction, interval = predict_watering_needs(28, 1500, 60, 50)
print(f"Prediction: {prediction}")
print(f"Result: {'No watering needed' if prediction else 'Watering needed, add {:.2f} moisture units'.format(interval)}")
"""
