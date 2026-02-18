# services/sleep_logger.py

import pandas as pd
from datetime import datetime
import os


def save_record(path, sleep_hours, stress, hr, prediction):

    # Crear carpeta si no existe
    os.makedirs(os.path.dirname(path), exist_ok=True)

    record = {
        "date": datetime.now(),
        "sleep_hours": sleep_hours,
        "stress_level": stress,
        "heart_rate": hr,
        "prediction": prediction
    }

    df = pd.DataFrame([record])

    file_exists = os.path.isfile(path)

    df.to_csv(
        path,
        mode="a",
        header=not file_exists,
        index=False
    )


def load_history(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None
