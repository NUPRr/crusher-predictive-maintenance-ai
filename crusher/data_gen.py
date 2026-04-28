import pandas as pd
import numpy as np

# 1. Create a range of time
data_size = 1000
time = pd.date_range(start='1/1/2026', periods=data_size, freq='h')

# 2. Simulate random Temperature (Normal: 40-70°C) and Vibration (Normal: 1-4)
temp = np.random.uniform(40, 70, size=data_size)
vibration = np.random.uniform(1, 4, size=data_size)

# 3. Create a "Failure" logic: If Temp > 85 and Vibration > 6, it likely fails
# Let's inject some "Anomalies" (Danger zones)
temp[500:510] = np.random.uniform(85, 100, size=10)
vibration[500:510] = np.random.uniform(6, 9, size=10)

# 4. Define 'Status': 0 is Healthy, 1 is Needs Repair
status = []
for t, v in zip(temp, vibration):
    if t > 80 and v > 5:
        status.append(1) # Fail
    else:
        status.append(0) # Healthy

# 5. Save to CSV
df = pd.DataFrame({'Timestamp': time, 'Temperature': temp, 'Vibration': vibration, 'Status': status})
df.to_csv('crusher_sensor_data.csv', index=False)

print("Success! 'crusher_sensor_data.csv' has been created.")