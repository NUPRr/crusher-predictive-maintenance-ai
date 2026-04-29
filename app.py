import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sqlite3
import time
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Crusher Intel AI", layout="wide")

# Updated CSS for Responsive Text
st.markdown("""
    <style>
    /* Laptop/Desktop par bada dikhega */
    h1 {
        font-size: 2.5rem !important;
    }
    
    /* Mobile Screen (width < 768px) par font chota ho jayega */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.5rem !important;
            text-align: center;
        }
        [data-testid="stMetric"] {
            padding: 10px;
        }
    }

    [data-testid="stMetric"] { 
        background-color: rgba(28, 131, 225, 0.1); 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #0072f5; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOAD BRAIN & DATABASE ---
with open('crusher_model.pkl', 'rb') as f:
    model = pickle.load(f)

conn = sqlite3.connect('crusher_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS history (timestamp TEXT, temp REAL, vib REAL, risk REAL)')
conn.commit()

# --- 3. SESSION STATE ---
if 'data_log' not in st.session_state:
    st.session_state.data_log = pd.DataFrame(columns=['Temp', 'Vib', 'Risk'])

# --- 4. BUSINESS CONTEXT (Top Header) ---
st.title("🏭 Crusher Monitoring System")
# Putting Location and ID front and center
head_col1, head_col2, head_col3 = st.columns(3)
head_col1.write(f"**Machine ID:** CR-402 (Primary)")
head_col2.write(f"**Location:** Thane Quarry - Site B")
head_col3.write(f"**Status:** 🛰️ Connected via IoT")
st.divider()

# --- 5. LIVE CONTROLS ---
st.sidebar.title("🛠️ System Controls")
live_mode = st.sidebar.toggle("Enable Live Simulation", value=False)

if live_mode:
    temp = 60 + np.sin(time.time()/10) * 10 + np.random.normal(0, 2)
    vib = 3.0 + np.cos(time.time()/10) * 1 + np.random.normal(0, 0.5)
    st.info("Streaming live telemetry...")
    time.sleep(1)
    st.rerun()
else:
    c1, c2 = st.columns(2)
    temp = c1.slider("🌡️ Temperature Sensor (°C)", 30, 120, 65)
    vib = c2.slider("📳 Vibration Sensor (Hz)", 0.0, 10.0, 4.2)

# --- 6. AI PREDICTION ---
features = pd.DataFrame([[temp, vib]], columns=['Temperature', 'Vibration'])
risk_prob = model.predict_proba(features)[0][1] * 100
prediction = model.predict(features)[0]

# History Log
new_entry = pd.DataFrame({'Temp': [temp], 'Vib': [vib], 'Risk': [risk_prob]})
st.session_state.data_log = pd.concat([st.session_state.data_log, new_entry]).iloc[-30:]

# --- 7. METRICS & GRAPHS ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Heat Status", f"{temp:.1f}°C")
col_m2.metric("Vibration Level", f"{vib:.2f} Hz")
col_m3.metric("Failure Risk", f"{risk_prob:.1f}%")

st.subheader("📊 Analytics Trend (Last 30 Readings)")
st.line_chart(st.session_state.data_log[['Temp', 'Risk']])

# --- 8. SMART ALERTS ---
if risk_prob > 80:
    st.error(f"🚨 CRITICAL FAILURE RISK: {risk_prob:.1f}%")
    st.warning("🛠️ **ACTION REQUIRED:** Inspect bearing housing and check lubrication levels immediately.")
    now = datetime.now().strftime("%H:%M:%S")
    c.execute("INSERT INTO history VALUES (?,?,?,?)", (now, temp, vib, risk_prob))
    conn.commit()
elif risk_prob > 50:
    st.warning(f"⚠️ WARNING: Moderate Risk ({risk_prob:.1f}%) - Schedule inspection.")
else:
    st.success("✅ SYSTEM HEALTHY")

st.divider()

# --- 9. HISTORY TABLE (Fixed Logic) ---
st.subheader("📅 Recent Incident Logs")
logs = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp DESC LIMIT 5", conn)

if not logs.empty:
    st.table(logs)
else:
    st.write("No incidents recorded.")
