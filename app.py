import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sqlite3
import time
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Crusher Intel AI", layout="wide", initial_sidebar_state="collapsed")

# Professional Industrial CSS
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #0072f5; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOAD BRAIN & DATABASE ---
with open('crusher_model.pkl', 'rb') as f:
    model = pickle.load(f)

conn = sqlite3.connect('crusher_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS history (timestamp TEXT, temp REAL, vib REAL, risk REAL)')
conn.commit()

# --- 3. SESSION STATE (Memory) ---
if 'data_log' not in st.session_state:
    st.session_state.data_log = pd.DataFrame(columns=['Temp', 'Vib', 'Risk'])

# --- 4. SIDEBAR - BUSINESS CONTEXT ---
st.sidebar.title("🛠️ Unit Settings")
machine_id = st.sidebar.selectbox("Select Machine ID", ["CR-402 (Primary)", "CR-405 (Secondary)"])
location = st.sidebar.info("📍 Site: Thane Quarry - Sector B")
live_mode = st.sidebar.toggle("🛰️ Enable Live Simulation", value=False)

# --- 5. MAIN DASHBOARD ---
st.title(f"🏭 Crusher Monitoring System | {machine_id}")
st.divider()

# --- 6. LIVE SIMULATION vs MANUAL ---
if live_mode:
    # Auto-generate values with a bit of "noise"
    temp = 60 + np.sin(time.time()/10) * 10 + np.random.normal(0, 2)
    vib = 3.0 + np.cos(time.time()/10) * 1 + np.random.normal(0, 0.5)
    st.info("Simulation active. Values are streaming from virtual sensors...")
    time.sleep(1) # Slow down refresh
    st.rerun()
else:
    c1, c2 = st.columns(2)
    temp = c1.slider("🌡️ Sensor: Temperature (°C)", 30, 120, 65)
    vib = c2.slider("📳 Sensor: Vibration (Hz)", 0.0, 10.0, 4.2)

# --- 7. AI PREDICTION & PROBABILITY ---
features = pd.DataFrame([[temp, vib]], columns=['Temperature', 'Vibration'])
risk_prob = model.predict_proba(features)[0][1] * 100  # Probability of class 1 (Failure)
prediction = model.predict(features)[0]

# Update history buffer
new_entry = pd.DataFrame({'Temp': [temp], 'Vib': [vib], 'Risk': [risk_prob]})
st.session_state.data_log = pd.concat([st.session_state.data_log, new_entry]).iloc[-30:]

# --- 8. VISUAL DASHBOARD ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Heat Status", f"{temp:.1f}°C")
col_m2.metric("Vibration Level", f"{vib:.2f} Hz")
col_m3.metric("Failure Risk", f"{risk_prob:.1f}%", delta=f"{risk_prob-50:.1f}%", delta_color="inverse")

# --- 9. GRAPHS (The Time-Based Story) ---
st.subheader("📊 Analytics Trend (Last 30 Seconds)")
st.line_chart(st.session_state.data_log[['Temp', 'Risk']])

# --- 10. SMART ALERTS & ACTIONS ---
if risk_prob > 80:
    st.error(f"🚨 CRITICAL FAILURE RISK: {risk_prob:.1f}%")
    st.warning("🛠️ **ACTION REQUIRED:** High vibration detected. Inspect bearing housing and check lubrication levels immediately.")
    # Log critical to DB
    c.execute("INSERT INTO history VALUES (?,?,?,?)", (datetime.now().strftime("%H:%M:%S"), temp, vib, risk_prob))
    conn.commit()
elif risk_prob > 50:
    st.warning(f"⚠️ WARNING: Moderate Risk ({risk_prob:.1f}%) - Schedule inspection within 24 hours.")
else:
    st.success("✅ SYSTEM HEALTHY: All parameters within nominal range.")

st.divider()

# --- 11. HISTORY TABLE ---
st.subheader("📅 Recent Incident Logs")
logs = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp DESC LIMIT 5", conn)
if not logs.empty:
    st.table(logs)
else:
    st.write("No incidents recorded.")
