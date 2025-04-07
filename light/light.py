import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

# Train and save the model for predicting light intensity based on soil moisture & temperature
def train_light_model(data_path='light_train.csv', model_path='light_model.joblib'):
    data = pd.read_csv(data_path)

    # Feature columns and target
    X = data[['moisture', 'temperature']]
    y = data['light']

    # Train a Random Forest Regressor
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)

    # Save the trained model
    joblib.dump(model, model_path)
    print(f"Light prediction model saved to {model_path}")

# Predict light intensity from soil moisture and temperature
def predict_light(moisture, temperature, model_path='light/light_model.joblib'):
    model = joblib.load(model_path)
    input_data = np.array([[moisture, temperature]])
    prediction = model.predict(input_data)[0]
    return prediction

if __name__ == '__main__':
    # train_light_model()
    light_value = predict_light(51, 28.6)
    print(f"Predicted light intensity: {light_value:.2f} lux")

"""
Example usage:

train_light_model()  # Train the model

# Predict light intensity
light_value = predict_light(51, 28.6)
print(f"Predicted light intensity: {light_value:.2f} lux")
"""
