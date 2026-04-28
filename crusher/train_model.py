import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# 1. Load the data you just generated
df = pd.read_csv('crusher_sensor_data.csv')

# 2. Pick the 'Features' (Inputs) and the 'Target' (What we want to predict)
X = df[['Temperature', 'Vibration']] # The sensors
y = df['Status']                     # The result (Healthy or Fail)

# 3. Split data: 80% for learning, 20% for testing the AI's "exam"
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize the AI (Random Forest is like a team of decision-makers)
model = RandomForestClassifier(n_estimators=100)

# 5. Train the AI
print("Training the AI brain... please wait.")
model.fit(X_train, y_train)

# 6. Check how smart it is
predictions = model.predict(X_test)
score = accuracy_score(y_test, predictions)
print(f"AI Training Complete! Accuracy: {score * 100:.2f}%")

# 7. Save the brain to a file so we can use it in our Dashboard later
with open('crusher_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model saved as 'crusher_model.pkl'")