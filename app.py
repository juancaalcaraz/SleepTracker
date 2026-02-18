import streamlit as st
import time

from config import MODEL_PATH, DATA_PATH, CLASS_LABELS, HEART_RATE_RANGES
from model.predictor import SleepPredictor
from services.heart_rate import calculate_bpm, classify_heart_rate
from services.sleep_logger import save_record, load_history


# Inicializar modelo
predictor = SleepPredictor(MODEL_PATH)

st.title("Sleep Quality Tracker")

st.subheader("1️⃣ Medición de Heart Rate")

if st.button("Iniciar temporizador (15 segundos)"):

    timer_placeholder = st.empty()

    for i in range(15, 0, -1):
        timer_placeholder.write(f"Cuenta tus pulsaciones... {i}")
        time.sleep(1)

    timer_placeholder.write("Tiempo terminado. Ingresa tus pulsaciones.")


pulses = st.number_input("Pulsaciones en 15 segundos", min_value=0)

heart_rate = calculate_bpm(pulses)

if pulses > 0:
    hr_status = classify_heart_rate(
        heart_rate,
        HEART_RATE_RANGES["low"],
        HEART_RATE_RANGES["high"]
    )
    st.info(f"Heart Rate estimado: {heart_rate} BPM ({hr_status})")


st.subheader("2️⃣ Variables de sueño")

sleep_hours = st.number_input("Horas dormidas", min_value=0.0, max_value=12.0)
stress_level = st.slider("Nivel de estrés (1-10)", 1, 10)


if st.button("Predecir calidad del sueño"):

    prediction = predictor.predict(
        sleep_hours,
        stress_level,
        heart_rate
    )

    label = CLASS_LABELS[prediction]

    st.success(f"Resultado: {label}")

    save_record(
        DATA_PATH,
        sleep_hours,
        stress_level,
        heart_rate,
        prediction
    )


st.subheader("📊 Historial")

history = load_history(DATA_PATH)

if history is not None:
    st.dataframe(history)
    st.line_chart(history["prediction"])
