import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Samuel's Smart Hub", layout="centered")

# --- ESTILO "CYBER-PURPLE" GLASSMORPHISM ---
st.markdown("""
    <style>
    /* Fondo con gradiente animado en tonos morados */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #5b247a, #1e0533);
        background-size: 400% 400%;
        animation: gradient 10s ease infinite;
        color: white;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Tarjeta central traslúcida */
    .main-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }

    /* Botón con brillo neón morado */
    .bk-btn-success {
        background-color: #bc13fe !important;
        border-color: #bc13fe !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.6) !important;
        transition: 0.3s !important;
    }
    
    /* Títulos con degradado neón */
    h1, h3 {
        text-align: center;
        background: -webkit-linear-gradient(#bc13fe, #ff00de);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
client_id = "samuel_voice_hub_2026"
client1 = paho.Client(client_id)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.title("SAMUEL'S CORE")
st.subheader("Voice Command Interface")

# Imagen o Icono central
col1, col2, col3 = st.columns([1,2,1])
with col2:
    try:
        image = Image.open('ger.png')
        st.image(image, use_container_width=True)
    except:
        st.markdown("<h2 style='text-align:center; font-size: 60px;'>🧬</h2>", unsafe_allow_html=True)

st.write("---")
st.markdown("<p style='text-align:center; opacity: 0.8;'>SISTEMA LISTO. ESPERANDO FRECUENCIA DE VOZ.</p>", unsafe_allow_html=True)

# --- BOTÓN DE VOZ ---
EVENT_NAME = "samuel_voice_event"
stt_button = Button(label="🎙️ INICIAR ESCUCHA", width=250, button_type="success")

stt_button.js_on_event("button_click", CustomJS(code=f"""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'es-ES';
    recognition.onresult = function (e) {{
        var value = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("{EVENT_NAME}", {{detail: value}}));
    }}
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events=EVENT_NAME,
    key="listen",
    refresh_on_update=False,
    override_height=80,
    debounce_time=0)

st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESAMIENTO ---
if result and EVENT_NAME in result:
    comando = result.get(EVENT_NAME).strip()
    
    st.markdown(f"""
        <div style="background: rgba(188, 19, 254, 0.15); padding: 20px; border-radius: 15px; border-left: 5px solid #bc13fe; margin-top: 20px;">
            <b style="color: #bc13fe;">Voz detectada:</b> "{comando}"
        </div>
    """, unsafe_allow_html=True)
    
    # Lógica de envío
    accion = "ON" if any(word in comando.lower() for word in ["prender", "encender", "activar"]) else "OFF" if any(word in comando.lower() for word in ["apagar", "desactivar"]) else comando
    
    try:
        client1.connect(broker, port)
        payload = json.dumps({"Act1": accion})
        client1.publish("control_casa", payload)
        st.toast(f"Señal {accion} transmitida", icon="💜")
    except:
        st.error("Error en el enlace MQTT")

if not os.path.exists("temp"):
    os.makedirs("temp")
