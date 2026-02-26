import streamlit as st
import time
import pandas as pd
import altair as alt
from datetime import datetime

# Tus módulos internos
from config import MODEL_PATH, DATA_PATH, CLASS_LABELS, HEART_RATE_RANGES
from model.predictor import SleepPredictor
from services.heart_rate import calculate_bpm, classify_heart_rate
from services.sleep_logger import save_record, load_history

# --- CONFIGURACIÓN DE CACHÉ ---
@st.cache_data(ttl=600)
def get_cached_history(path):
    return load_history(path)

# --- INICIALIZACIÓN ---
if "ultima_label" not in st.session_state:
    st.session_state.ultima_label = None

predictor = SleepPredictor(MODEL_PATH)

st.title("Sleep Quality Tracker")
st.markdown("### -- Diario Onírico. --")

# Definición de Pestañas (Optimiza RAM en gama baja)
tab_diario, tab_stats = st.tabs(["📝 Registrar Sueño", "📊 Mi Historial"])

with tab_diario:
    st.warning("⚠️ Herramienta de uso personal. No reemplaza evaluación médica.")

    st.subheader("1️⃣ Medición de Pulso")
    st.markdown("💡 **Instrucciones:** Presiona el botón y cuenta tus latidos por 15 segundos.")

    if st.button("Iniciar temporizador (15 segundos)"):
        timer_placeholder = st.empty()
        for i in range(15, 0, -1):
            timer_placeholder.write(f"Cuenta tus pulsaciones... {i}")
            time.sleep(1)
        timer_placeholder.write("✅ ¡Tiempo terminado! Ingresa el número abajo.")

    pulses = st.number_input("Pulsaciones en 15 segundos", min_value=0, step=1)
    heart_rate = calculate_bpm(pulses)

    if pulses > 0:
        hr_status = classify_heart_rate(heart_rate, HEART_RATE_RANGES["low"], HEART_RATE_RANGES["high"])
        st.info(f"Heart Rate estimado: {heart_rate} BPM ({hr_status})")

    st.divider()
    st.subheader("2️⃣ Variables de sueño")
    sleep_input = st.text_input("Horas dormidas (ej: 7.5)", placeholder="0.0")

    try:
        sleep_hours = float(sleep_input) if sleep_input else None
    except ValueError:
        sleep_hours = None
        st.warning("Ingresa un número válido.")

    if sleep_hours is not None and not (0.0 <= sleep_hours <= 12.0):
        st.error("El rango debe ser entre 0 y 12 horas.")
        sleep_hours = None

    st.divider()
    st.subheader("3️⃣ Nivel de Estrés")
    modo_estres = st.radio("Método de registro:", ["Ingreso rápido", "Cuestionario PSS-4"])

    if modo_estres == "Ingreso rápido":
        st.info("Escala: 1 Bajo; 8 Alto")
        stress_level = st.slider("Estrés detectado", 1, 8, 4)
    else:
        st.markdown("0 = Nunca, 4 = Muy a menudo")
        q1 = st.slider("¿Te has sentido nervioso o estresado?", 0, 4)
        q2 = st.slider("¿Incapaz de controlar cosas importantes?", 0, 4)
        q3 = st.slider("¿Confiado en tu capacidad de manejo?", 0, 4)
        raw_score = q1 + q2 + (4 - q3)
        stress_level = round((raw_score / 12) * 7 + 1)
        st.info(f"Nivel calculado: {stress_level} (escala 1-8)")

    st.divider()
    st.subheader("4️⃣ Hábitos y Relato")
    opciones_habitos = [
    "Ejercicio intenso", "Ejercicio liviano", "Meditación", "Lectura",
    "Uso de pantallas", "Luz brillante", "Trabajar en la cama",
    "Cena pesada", "Cena liviana", "Acostarse con hambre",
    "Cafeína", "Mate", "Té negro", "Té de hierbas", "Alcohol", "Tabaco", "Energizante",
    "Ducha caliente", "Ducha fría",
    "Charlar", "Discutir", "Planificar el siguiente día", "Música/Podcast",
    "Siesta tarde", "Ambiente ruidoso", "Padecer Mucho calor/frío", "Otros"
    ]

    habitos_sel = st.multiselect("¿Qué hiciste antes de dormir? (Máx 3)", options=opciones_habitos, max_selections=3)
    habitos_str = ", ".join(habitos_sel)

    dream_text = st.text_area("Registra la narrativa de tu experiencia onírica (Opcional)", 
                              placeholder="Registrá: ¿Qué tipo de sueño tuviste? ¿Qué recordás del sueño? ¿Qué sensaciones experimentaste? junto a lo que sientas relevante de tu sueño.",
                              help="Este texto servirá para verificar sueños/temas recurrentes mediante técnicas de IA.")

    if dream_text:
        # 1. Quitamos espacios en blanco al inicio y al final
        dream_text_clean = dream_text.strip()
    
        # 2. Reemplazamos múltiples espacios internos por uno solo
        # Esto limpia si el usuario apretó la barra espaciadora por error
        dream_text_clean = " ".join(dream_text_clean.split())
    
        # 3. Mantenemos las mayúsculas para la lectura del usuario, 
    else:
        dream_text_clean = ""

    st.markdown("### 🔎 Evaluación")
    can_predict = pulses > 0 and sleep_hours is not None
    
    if st.button("Predecir calidad del sueño", disabled=not can_predict, use_container_width=True):
        prediction = predictor.predict(sleep_hours, stress_level, heart_rate)
        st.session_state.ultima_label = CLASS_LABELS[prediction]
        
        save_record(DATA_PATH, sleep_hours, stress_level, heart_rate, prediction, habitos_str, dream_text_clean)
        
        st.cache_data.clear() # Limpiamos caché para actualizar la pestaña de stats
        st.success(f"¡Resultado guardado! Calidad: {st.session_state.ultima_label}")

    elif st.session_state.ultima_label:
        st.info(f"Último resultado: {st.session_state.ultima_label}")

with tab_stats:
    st.subheader("📊 Historial de Descanso")
    history = get_cached_history(DATA_PATH)

    if history is not None and not history.empty:
        history["date"] = pd.to_datetime(history["date"])
        history = history.sort_values("date")

        label_map = {0: "Mala", 1: "Regular", 2: "Buena"}
        history["sleep_label"] = history["prediction"].map(label_map)
        
        latest = history.iloc[-1]
        st.metric(label="Último registro", value=latest["sleep_label"])

        color_scale = alt.Scale(domain=["Mala", "Regular", "Buena"], range=["#e74c3c", "#f1c40f", "#2ecc71"])

        chart = alt.Chart(history).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("date:T", title="Fecha"),
            y=alt.Y("sleep_label:N", sort=["Mala", "Regular", "Buena"], title="Calidad"),
            color=alt.Color("sleep_label:N", scale=color_scale, legend=None),
            tooltip=["date", "sleep_label", "sleep_hours", "stress_level"]
        ).properties(height=400).interactive()

        st.altair_chart(chart, use_container_width=True)
        
        with st.expander("Ver tabla de datos completa"):
            st.dataframe(history[["date", "sleep_label", "sleep_hours", "habits", "dream_journal"]].sort_index(ascending=False))
    else:
        st.info("Aún no hay datos. Registra tu primer sueño para ver el gráfico.")
