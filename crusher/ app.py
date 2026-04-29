import streamlit as st
import pandas as pd
import pickle
import sqlite3
from datetime import datetime

# --- 1. DATABASE SETUP ---
# We use the full names 'temperature' and 'vibration' to match your data
conn = sqlite3.connect('crusher_logs.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs 
             (timestamp TEXT, temperature REAL, vibration REAL, status TEXT)''')
conn.commit()

# --- 2. LOAD AI BRAIN ---
with open('crusher_model.pkl', 'rb') as f:
    model = pickle.load(f)

# --- 3. MOBILE-FRIENDLY UI SETUP ---
st.set_page_config(page_title="Crusher AI Health", page_icon="🏗️", layout="centered")

# Custom CSS for that "Aesthetic" touch
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; }
    .stAlert { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Crusher AI Health")
st.write("Real-time predictive monitoring for industrial units.")

# --- 4. SENSOR INPUT SECTION ---
with st.expander("🎮 Manual Sensor Simulation", expanded=True):
    temp = st.slider("Temperature (°C)", 30, 120, 50)
    vib = st.slider("Vibration (Hz)", 0.0, 10.0, 2.5)

# --- 5. PREDICTION LOGIC ---
input_df = pd.DataFrame([[temp, vib]], columns=['Temperature', 'Vibration'])
prediction = model.predict(input_df)[0]

# --- 6. LIVE STATUS DISPLAY ---
st.subheader("Current Status")
if prediction == 0:
    st.success("✅ SYSTEM OPERATIONAL: Parameters Normal")
else:
    st.error("🚨 ALERT: PREDICTIVE FAILURE DETECTED!")
    st.toast("Emergency Alert Logged!", icon="⚠️")
    # Log the failure to the database
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (now, temp, vib, "CRITICAL"))
    conn.commit()

# Metrics Row
m1, m2 = st.columns(2)
m1.metric("Heat", f"{temp}°C")
m2.metric("Vibration", f"{vib}Hz")

st.divider()

# --- 7. THE AUTOMATED MAINTENANCE LOGBOOK ---
st.subheader("📅 Automated Maintenance Logbook")
st.write("Recent critical incidents recorded by AI:")

# Pulling data from the SQL Database
history_df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10", conn)

if not history_df.empty:
    # This makes the table look clean and professional
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    if st.button("🗑️ Clear Logbook History"):
        c.execute("DELETE FROM logs")
        conn.commit()
        st.rerun()
else:
    st.info("No incidents recorded. The machine is running smoothly!")

st.caption("Industrial Monitoring System v2.1")
