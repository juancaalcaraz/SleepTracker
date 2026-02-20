# model/predictor.py

import joblib
import pandas as pd
     
class SleepPredictor:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        # Opcional: podés guardar los nombres de las columnas aquí
        self.feature_names = ["Sleep Duration", "Stress Level", "Heart Rate",] 

    def predict(self, sleep_hours, stress_level, heart_rate):
        # Creamos el DF con los nombres correctos
        X = pd.DataFrame([[sleep_hours, stress_level, heart_rate]], columns=self.feature_names)
        return self.model.predict(X)[0]
