import paho.mqtt.client as paho
import time
import streamlit as st
import json
import platform

# --- CONFIGURACIÓN DE ESTILO PARA SAMUEL ---
st.set_page_config(page_title="MQTT Terminal - Samuel", layout="centered")

# Estilo CSS con estética de estación de trabajo / Motor de juegos
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    /* Estilo de botones tipo 'Action' */
    .stButton>button {
        background-color: #262730;
        color: #ff4b4b; /* Un rojo/naranja tipo alerta/acción */
        border: 1px solid #464646;
        border-radius: 4px;
        font-family: 'Courier New', Courier, monospace;
        width: 100%;
        transition: 0.2s;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: white;
        background-color: #ff4b4b;
        box-shadow: 0px 0px 10px rgba(255, 75, 75, 0.4);
    }
    /* Títulos con fuente monoespaciada */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    /* Estilo para el slider */
    .stSlider label {
        color: #ff4b4b !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Información de entorno
st.caption(f"ENV: Python {platform.python_version()} | DEVICE: {platform.system()}")

values = 0.0
act1="OFF"

# --- LÓGICA MQTT ---
def on_publish(client,userdata,result):
    pass

broker="157.230.214.127"
port=1883

st.title("📟 Hardware Control")
st.markdown("---")

# Layout de consola
col1, col2 = st.columns(2)

with col1:
    if st.button('SET_STATE: ON'):
        act1="ON"
        client1= paho.Client("GIT-HUB")                           
        client1.on_publish = on_publish                          
        client1.connect(broker,port)  
        message = json.dumps({"Act1":act1})
        client1.publish("cmqtt_s", message)
        st.info("Log: Command 'ON' sent to broker.")

with col2:
    if st.button('SET_STATE: OFF'):
        act1="OFF"
        client1= paho.Client("GIT-HUB")                           
        client1.on_publish = on_publish                          
        client1.connect(broker,port)  
        message = json.dumps({"Act1":act1})
        client1.publish("cmqtt_s", message)
        st.warning("Log: Command 'OFF' sent to broker.")

st.write("")
st.markdown("### Analog Input Simulation")

values = st.slider('Input Value (0-100)', 0.0, 100.0, 0.0)

if st.button('Push Data to Wokwi'):
    client1= paho.Client("GIT-HUB")                           
    client1.on_publish = on_publish                          
    client1.connect(broker,port)   
    message = json.dumps({"Analog": float(values)})
    client1.publish("cmqtt_a", message)
    st.success(f"Dato analógico {values} enviado.")
