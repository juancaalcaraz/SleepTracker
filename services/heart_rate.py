# services/heart_rate.py

def calculate_bpm(pulses_15s: int) -> int:
    return pulses_15s * 4


def classify_heart_rate(bpm: int, low: int, high: int) -> str:
    if bpm < low:
        return "Bajo"
    elif bpm > high:
        return "Elevado"
    return "Normal"
