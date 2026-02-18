# config.py

MODEL_PATH = "model/sleep_model.pkl"
DATA_PATH = "data/sleep_log.csv"

CLASS_LABELS = {
    0: "Mala calidad",
    1: "Calidad media",
    2: "Buena calidad"
}

HEART_RATE_RANGES = {
    "low": 60,
    "high": 100
}
