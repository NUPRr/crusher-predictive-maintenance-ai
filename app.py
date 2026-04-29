import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sqlite3
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE & MODEL SETUP ---
conn = sqlite3.connect('crusher_logs.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, temp REAL, vib REAL, status TEXT)')
conn.commit()

# Load the AI model
with open('crusher_model.pkl', 'rb') as f:
    model = pickle.load(f)

# --- 2. "REAL-TIME" HISTORY TRACKING ---
# This creates a 'memory' for the graph so it doesn't disappear
if 'temp_history' not in st.session_state:
    st.session_state.temp_history = [50] * 20
if 'vib_history' not in st.session_state:
    st.session_state.vib_history = [2.5] * 20

# --- 3. UI CONFIG & DESIGN ---
st.set_page_config(page_title="Crusher Command Center", page_icon="🏗️", layout="wide")

# Theme-aware CSS (Works for Light & Dark mode)
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px; border-radius: 12px; border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stHeader { font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BUSINESS CONTEXT (The Identity) ---
st.title("🏗️ Crusher Command Center: Unit #402")
st.caption("📍 Location: Thane Quarry Site B | 🟢 System: Connected via IoT")

# --- 5. TELEMETRY CONTROLS (The Input) ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        temp = st.slider("🌡️ Live Temperature (°C)", 30, 120, 50)
    with col2:
        vib = st.slider("📳 Live Vibration (Hz)", 0.0, 10.0, 2.5)

# Update the history memory
st.session_state.temp_history.append(temp)
st.session_state.vib_history.append(vib)
st.session_state.temp_history = st.session_state.temp_history[-20:]
st.session_state.vib_history = st.session_state.vib_history[-20:]

# --- 6. DATA STORY (The Visual Graphs) ---
st.subheader("📈 Real-Time Sensor Analytics")
chart_data = pd.DataFrame({
    "Temperature Trend": st.session_state.temp_history,
    "Vibration Trend": st.session_state.vib_history
})
st.line_chart(chart_data)

st.divider()

# --- 7. AI DIAGNOSIS & ALARM ---
input_df = pd.DataFrame([[temp, vib]], columns=['Temperature', 'Vibration'])
prediction = model.predict(input_df)[0]

m_col1, m_col2, m_col3 = st.columns([1,1,2])

with m_col1:
    st.metric("Current Heat", f"{temp}°C")
with m_col2:
    st.metric("Current Vib", f"{vib}Hz")

with m_col3:
    if prediction == 0:
        st.success("✅ SYSTEM OPERATIONAL: Parameters within safety limits.")
    else:
        st.error("🚨 CRITICAL: PREDICTIVE FAILURE DETECTED!")
        # Vibrate/Sound Trigger
        components.html("<script>if(window.navigator.vibrate)window.navigator.vibrate([500,100,500]);</script>", height=0)
        
        # Log to Database
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (now, temp, vib, "CRITICAL"))
        conn.commit()

st.divider()

# --- 8. HISTORICAL LOGBOOK ---
st.subheader("📅 Automated Maintenance Log")
history_df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 5", conn)
if not history_df.empty:
    st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.info("No critical incidents logged in this session.")

st.caption("Proprietary Industrial AI System | Version 3.0")
