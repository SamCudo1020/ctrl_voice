import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO MORADO ---
st.set_page_config(page_title="CASA INTELIGENTE", layout="centered")

st.markdown("""
    <style>
    /* Fondo morado profundo */
    .stApp {
        background-color: #1e0533;
        background-image: linear-gradient(180deg, #1e0533 0%, #110221 100%);
        color: white;
    }
    
    /* Títulos en tonos morado neón */
    h1, h3, p, span {
        color: #bc13fe !important;
        text-align: center;
    }

    /* Centrado del componente Bokeh */
    .stBokehEvents {
        display: flex;
        justify-content: center;
    }

    /* Estilo del botón de Bokeh */
    .bk-btn-success {
        background-color: #9d50bb !important;
        border-color: #bc13fe !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("yosoyclientequeescucha2")

def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

# --- INTERFAZ (TEXTOS ORIGINALES) ---
st.title("CASA INTELIGENTE 🏠")
st.subheader("CONTROL POR VOZ")

# Imagen centrada
col1, col2, col3 = st.columns([1,1,1])
with col2:
    try:
        image = Image.open('ger.png')
        st.image(image, width=200)
    except:
        pass

st.write("Toca el Botón y habla")

# --- BOTÓN CENTRADO ---
# Usamos columnas para centrar el botón de Bokeh manualmente
c1, c2, c3 = st.columns([1,1,1])
with col2:
    stt_button = Button(label=" Inicio ", width=200)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
    
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("yosoyclientequeescucha2", {detail: value}));
            }
        }
        recognition.start();
        """))

    result = streamlit_bokeh_events(
        stt_button,
        events="yosoyclientequeescucha2",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)

# --- PROCESAMIENTO ---
if result:
    if "yosoyclientequeescucha2" in result:
        valor_voz = result.get("yosoyclientequeescucha2")
        st.write(valor_voz)
        
        try:
            client1.on_publish = on_publish                            
            client1.connect(broker, port)  
            message = json.dumps({"Act1": valor_voz.strip()})
            ret = client1.publish("voice_ctrl", message)
        except:
            st.error("Error de conexión")

if not os.path.exists("temp"):
    os.makedirs("temp")
