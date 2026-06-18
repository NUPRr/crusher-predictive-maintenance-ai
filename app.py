import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sqlite3
import time
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Crusher Intel AI", layout="wide")

# CSS: Responsive Title, Metric Cards, and Bottom Padding
st.markdown("""
    <style>
    @media (max-width: 768px) { h1 { font-size: 1.6rem !important; } }
    [data-testid="stMetric"] { background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #0072f5; }
    .main { padding-bottom: 100px; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & BRAIN ---
with open('crusher_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Database Setup (Aligned with actual schema)
conn = sqlite3.connect('crusher_pro.db', check_same_thread=False)
c = conn.cursor()
# Ensure table exists using the correct name and columns
c.execute('CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, temperature REAL, vibration REAL, status TEXT)')
conn.commit()

# --- 3. SESSION STATE (The Memory Fix) ---
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame({
        'Time': [datetime.now() for _ in range(20)],
        'Temp': [50.0] * 20,
        'Vib': [2.5] * 20,
        'Risk': [10.0] * 20
    })

# --- 4. HEADER ---
st.title("🏭 Crusher Monitoring System")
head_c1, head_c2, head_c3 = st.columns(3)
head_c1.write("**ID:** CR-402 (Primary)")
head_c2.write("**Site:** Thane Quarry - Site B")
head_c3.write("**Status:** 🛰️ IoT Connected")
st.divider()

# --- 5. CONTROLS (Sidebar & Main) ---
st.sidebar.title("🛠️ System Controls")
live_mode = st.sidebar.toggle("🛰️ Live Simulation", value=False)

if live_mode:
    # Generate live data and store it in session state
    st.session_state.temp = 60 + np.sin(time.time()/5) * 15 + np.random.normal(0, 1)
    st.session_state.vib = 3.0 + np.cos(time.time()/5) * 2 + np.random.normal(0, 0.2)
    
    temp = st.session_state.temp
    vib = st.session_state.vib
    
    # A short pause for the live ticker feel, then rerun to pull the next stream data
    time.sleep(0.5)
    st.rerun()
else:
    # Manual Slider Logic with unique keys to prevent duplicate element errors
    sc1, sc2 = st.columns(2)
    temp = sc1.slider("🌡️ Temp (°C)", 30, 120, 65, key="manual_temp_slider")
    vib = sc2.slider("📳 Vib (Hz)", 0.0, 10.0, 4.2, key="manual_vib_slider")

# Clear Logs Button (Sidebar)
if st.sidebar.button("Clear Maintenance Logs"):
    c.execute("DELETE FROM logs")
    conn.commit()
    st.sidebar.success("Logs cleared!")
    time.sleep(1)
    st.rerun()

# --- 6. PREDICTION & MEMORY ---
features = pd.DataFrame([[temp, vib]], columns=['Temperature', 'Vibration'])
risk_prob = model.predict_proba(features)[0][1] * 100

# Update Trend Memory
new_row = pd.DataFrame({'Time': [datetime.now()], 'Temp': [temp], 'Vib': [vib], 'Risk': [risk_prob]})
st.session_state.history_df = pd.concat([st.session_state.history_df, new_row]).iloc[-20:]

# --- 7. DASHBOARD METRICS ---
m1, m2, m3 = st.columns(3)
m1.metric("Heat", f"{temp:.1f}°C")
m2.metric("Vibration", f"{vib:.2f}Hz")
m3.metric("Failure Risk", f"{risk_prob:.1f}%")

# --- 8. TREND GRAPHS (Split Scales) ---
st.subheader("📈 Real-Time Analytics Trend")
g_col1, g_col2 = st.columns(2)

with g_col1:
    st.write("**Temperature History**")
    st.line_chart(st.session_state.history_df.set_index('Time')['Temp'])

with g_col2:
    st.write("**Risk Probability (%)**")
    st.line_chart(st.session_state.history_df.set_index('Time')['Risk'], color="#FF4B4B")

# --- 9. SMART ALERTS ---
if risk_prob > 80:
    st.error(f"🚨 ALERT: CRITICAL RISK DETECTED ({risk_prob:.1f}%)")
    st.info("🛠️ **Action:** Inspect bearing housing and cooling fan immediately.")
    
    # Corrected SQL Insert Query
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs VALUES (?,?,?,?)", (now, temp, vib, "CRITICAL"))
    conn.commit()

# --- 10. MAINTENANCE LOGBOOK ---
st.subheader("📅 Automated Maintenance Logbook")

# Corrected to pull from 'logs' table
logs = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 5", conn)

if not logs.empty:
    st.table(logs)
    st.caption("Showing last 5 critical incidents.")
else:
    st.info("Logbook is currently empty. No active maintenance alerts.")
