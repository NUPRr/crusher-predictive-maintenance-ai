import pandas as pd
import numpy as np

# Set random seed for reproducibility (Good practice!)
np.random.seed(42)

# 1. Create a range of time
data_size = 1200  # Extended to simulate a full 50-day window
time = pd.date_range(start='1/1/2026', periods=data_size, freq='h')

# 2. Simulate realistic machinery telemetry using a Normal Distribution
# Healthy crushers average around 55°C and 2.5Hz vibration
temp = np.random.normal(loc=55.0, scale=5.0, size=data_size)
vibration = np.random.normal(loc=2.5, scale=0.4, size=data_size)

# 3. Inject realistic anomaly states (Siemens Operational Safety Hazard Simulation)
# Let's simulate hours 500 to 520 as a severe bearing lubrication breakdown
temp[500:520] = np.random.normal(loc=90.0, scale=4.0, size=20)
vibration[500:520] = np.random.normal(loc=7.2, scale=0.8, size=20)

# Simulate hours 900 to 915 as structural mounting loose bolt anomaly
temp[900:915] = np.random.normal(loc=65.0, scale=3.0, size=15)
vibration[900:915] = np.random.normal(loc=8.5, scale=0.5, size=15)

# 4. Define 'Status' logic: 0 is Healthy, 1 is Maintenance Required
status = []
for t, v in zip(temp, vibration):
    # If parameters cross critical thresholds, flag as failure risk
    if t > 80.0 or v > 5.0:
        status.append(1) # Critical Alert State
    else:
        status.append(0) # Stable State

# 5. Compile into structured dataframe & output to CSV
df = pd.DataFrame({
    'Timestamp': time, 
    'Temperature': temp, 
    'Vibration': vibration, 
    'Status': status
})

df.to_csv('crusher_sensor_data.csv', index=False)
print(f"✅ Data Generation Complete. Saved {data_size} rows of realistic telemetry to 'crusher_sensor_data.csv'")
