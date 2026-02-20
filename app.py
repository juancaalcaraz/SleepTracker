import streamlit as st
import time

from config import MODEL_PATH, DATA_PATH, CLASS_LABELS, HEART_RATE_RANGES
from model.predictor import SleepPredictor
from services.heart_rate import calculate_bpm, classify_heart_rate
from services.sleep_logger import save_record, load_history
import altair as alt
import pandas as pd
@st.cache_data(ttl=600) # El ttl=600 limpia la memoria cada 10 minutos.
def get_cached_history(path):
    return load_history(path)
# Inicializar modelo
predictor = SleepPredictor(MODEL_PATH)

st.title("Sleep Quality Tracker")
st.markdown(""" ### -- Diario de tus sueños. --          
            """)
st.warning(
    "⚠️ Herramienta de uso personal. No reemplaza evaluación ni diagnóstico médico profesional."
)

st.subheader("1️⃣ Medición de Pulso")
st.markdown(
"""
💡 **Instrucciones:**

Presiona en **Iniciar temporizador** y cuenta tus latidos durante 15 segundos 
(coloca los dedos en el cuello o muñeca para mayor precisión).
"""
)


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
st.divider()
st.subheader("2️⃣ Variables de sueño")
st.markdown("Ingresa la cantidad de horas que dormiste (por ejemplo 7.5).")

# Text input con placeholder
sleep_input = st.text_input("Horas dormidas", placeholder="0.0")

# Validar y convertir a float
try:
    sleep_hours = float(sleep_input) if sleep_input else None
except ValueError:
    sleep_hours = None
    st.warning("Por favor ingresa un número válido de horas (por ejemplo 7.0 o 7.5).")

# Validar rango
if sleep_hours is not None:
    if not (0.0 <= sleep_hours <= 12.0):
        st.warning("Ingresa un número entre 0 y 12 horas.")
        sleep_hours = None

# Espacio visual
st.markdown("---")

# Sección Estrés.
st.subheader("3️⃣ Nivel de Estrés")

modo_estres = st.radio(
    "¿Cómo quieres registrar tu nivel de estrés?",
    ["Ingreso rápido", "Cuestionario breve"]
)

if modo_estres == "Ingreso rápido":
    st.info("Escala: 1 Bajo; 8 Alto ")
    stress_level = st.slider("Nivel de estrés (1-8)", 1, 8, 4)
    
else:
    st.markdown("Responde las siguientes preguntas (0 = Nunca, 4 = Muy a menudo)")
    
    q1 = st.slider("¿Te has sentido nervioso o estresado?", 0, 4)
    q2 = st.slider("¿Has sentido que no podías controlar cosas importantes?", 0, 4)
    q3 = st.slider("¿Te has sentido confiado en tu capacidad para manejar problemas?", 0, 4)

    # Invertimos la pregunta positiva (q3)
    raw_score = q1 + q2 + (4 - q3)

    # Normalizamos a escala 1–8
    stress_level = round((raw_score / 12) * 7 + 1)

    st.info(f"Nivel de estrés calculado: {stress_level} (escala 1–8)")

can_predict = pulses > 0 and sleep_hours is not None
if pulses == 0:
    st.warning("Por favor medí tu pulso antes de predecir.")
# --- Agregado antes de la sección de Evaluación ---
st.divider()
st.subheader("4️⃣ Hábitos y Relato")

# Opción A: Selección de etiquetas (Más estructurado)
opciones_habitos = [
    "Ejercicio intenso","Ejercicio liviano", "Meditación", "Uso de pantallas (Celular/TV)", 
    "Cena pesada","Cena liviana", "Cafeína", "Alcohol", "Tabaco", "Mate", "Bebida energizante", "Te negro","Te verde o de hierbas",
    "Lectura", "Ducha caliente", "Ducha fría", "Otro"
]

habitos_seleccionados = st.multiselect(
    "¿Qué hiciste antes de dormir? (Máximo 3)",
    options=opciones_habitos,
    max_selections=3,
    help="Seleccioná hasta 3 hábitos que creas que influyeron en tu descanso."
)

# Convertimos la lista de hábitos en un solo string separado por comas para el CSV
habitos_str = ", ".join(habitos_seleccionados)
st.subheader("4️⃣-B Relato del sueño")
dream_text = st.text_area(
    "¿Qué recordás de tu sueño? (Opcional)",
    placeholder="Escribí acá que tipo de sueño tuviste, lo que recuerdes del sueño, sensaciones al despertar...",
    help="Este texto servirá para futuros análisis de tópicos e IA."
)
st.markdown("### 🔎 Evaluación")
if st.button("Predecir calidad del sueño", disabled=not can_predict, use_container_width=True):

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
        prediction,
        habitos_str,
        dream_text 
    )


st.subheader("📊 Historial")


history = get_cached_history(DATA_PATH)

if history is not None and not history.empty:

    history["date"] = pd.to_datetime(history["date"])
    history = history.sort_values("date")

    label_map = {
        0: "Mala",
        1: "Regular",
        2: "Buena"
    }

    history["sleep_label"] = history["prediction"].map(label_map)
    latest = history.iloc[-1]
    if latest["sleep_label"]:
        st.metric(
            label="Calidad del último sueño registrado: ",
            value=latest["sleep_label"]
        )

    # Definir colores personalizados
    color_scale = alt.Scale(
        domain=["Mala", "Regular", "Buena"],
        range=["#e74c3c", "#f1c40f", "#2ecc71"]  # rojo, amarillo, verde
    )

    chart = alt.Chart(history).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("date:T", title="Fecha"),
        y=alt.Y(
            "sleep_label:N",
            sort=["Mala", "Regular", "Buena"],
            title="Calidad del Sueño"
        ),
        color=alt.Color(
            "sleep_label:N",
            scale=color_scale,
            legend=alt.Legend(title="Nivel")
        ),
        tooltip=[
            alt.Tooltip("date:T", title="Fecha"),
            alt.Tooltip("sleep_label:N", title="Calidad")
        ]
    ).properties(
        width=700,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
