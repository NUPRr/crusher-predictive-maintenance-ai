import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# 1. Pipeline Verification Guard
if not os.path.exists('crusher_sensor_data.csv'):
    print("❌ Error: 'crusher_sensor_data.csv' not found! Please run data_gen.py first.")
    exit()

# Load the generated asset data
df = pd.read_csv('crusher_sensor_data.csv')

# 2. Separate Features (Telemetry Inputs) and Target (Machine State)
X = df[['Temperature', 'Vibration']] 
y = df['Status']                     

# 3. Train/Test Data Partitioning (80/20 Validation Split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 4. Initialize Predictive Model 
# Using a balanced Random Forest Classifier 
model = RandomForestClassifier(n_estimators=100, random_state=42)

# 5. Train the Machine Learning Brain
print("🧠 Training Core AI Failure Engine... Please wait.")
model.fit(X_train, y_train)

# 6. Evaluation Framework (Deloitte Data Analytics Validation)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("\n📊 --- MODEL EVALUATION MATRIX ---")
print(f"Overall Model Accuracy: {accuracy * 100:.2f}%")
print("\nDetailed Performance Breakdown:")
print(classification_report(y_test, predictions, target_names=['Healthy (0)', 'Critical (1)']))

# 7. Serialize Brain to Deployment File
with open('crusher_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("💾 Model successfully serialized and exported as 'crusher_model.pkl'. Ready for live UI integration!")
