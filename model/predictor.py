# model/predictor.py

import joblib


class SleepPredictor:

    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict(self, sleep_hours, stress_level, heart_rate):
        input_data = [[sleep_hours, stress_level, heart_rate]]
        return self.model.predict(input_data)[0]
