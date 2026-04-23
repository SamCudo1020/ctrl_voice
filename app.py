import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Casa Inteligente - Voz", layout="centered")

# Estilo para que se vea moderno
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .stHeader { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
# El ID del cliente debe ser único para que no se desconecte
client_id = "user_interactivo_2026_voice" 
client1 = paho.Client(client_id)

def on_publish(client, userdata, result):
    print("Dato publicado con éxito")

st.title("CASA INTELIGENTE 🏠")
st.subheader("Control por Voz")

# Manejo de la imagen (evita error si no existe)
try:
    image = Image.open('ger.png')
    st.image(image, width=200)
except:
    st.info("💡 (Aquí iría tu logo 'ger.png')")

st.write("Haz clic en el botón y di un comando (ej: 'prender', 'apagar')")

# --- BOTÓN DE VOZ (BOKEH) ---
stt_button = Button(label="🎙️ HABLAR AHORA", width=200, button_type="success")

# Nombre del evento que conectará JS con Streamlit
EVENT_NAME = "event_voz"

stt_button.js_on_event("button_click", CustomJS(code=f"""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';
 
    recognition.onresult = function (e) {{
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {{
            if (e.results[i].isFinal) {{
                value += e.results[i][0].transcript;
            }}
        }}
        if (value != "") {{
            document.dispatchEvent(new CustomEvent("{EVENT_NAME}", {{detail: value}}));
        }}
    }}
    recognition.start();
    """))

# Capturar el evento de voz
result = streamlit_bokeh_events(
    stt_button,
    events=EVENT_NAME,
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# --- PROCESAMIENTO Y ENVÍO ---
if result and EVENT_NAME in result:
    texto_escuchado = result.get(EVENT_NAME).strip()
    st.write(f"**Escuché:** _{texto_escuchado}_")
    
    # Lógica de filtrado simple
    accion = "DESCONOCIDO"
    if "prender" in texto_escuchado.lower() or "on" in texto_escuchado.lower():
        accion = "ON"
    elif "apagar" in texto_escuchado.lower() or "off" in texto_escuchado.lower():
        accion = "OFF"
    else:
        accion = texto_escuchado

    # Enviar a MQTT
    try:
        client1.on_publish = on_publish
        client1.connect(broker, port)
        # Enviamos un JSON que tu Wokwi pueda leer fácilmente
        payload = json.dumps({"Act1": accion})
        client1.publish("control_casa", payload)
        st.success(f"Comando '{accion}' enviado a Wokwi")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# Crear carpeta temporal si es necesario
if not os.path.exists("temp"):
    os.makedirs("temp")
