import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import pickle

print("🧠 Booting up the XGBoost Training Sequence...")

# 1. Load the historical data we just generated
try:
    df = pd.read_csv('historical_fire_data.csv')
except FileNotFoundError:
    print("❌ Error: Could not find 'historical_fire_data.csv'. Did you run the generator script first?")
    exit()

# 2. Separate Features (The inputs) from the Target (The answer)
# We drop Sector_ID because the AI should learn the physics (weather/terrain), not just memorize names.
X = df.drop(columns=['Sector_ID', 'Fire_Occurred']) 
y = df['Fire_Occurred']

# 3. Split the data: 80% for studying, 20% for taking the final exam
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and Train the XGBoost Classifier
print("⚙️ Training the XGBoost AI. This might take a few seconds...")
model = xgb.XGBClassifier(
    n_estimators=100,      # Number of trees to build
    learning_rate=0.1,     # How fast it updates its beliefs
    max_depth=5,           # How deep each tree can think
    random_state=42,
    eval_metric='logloss'
)

# This is where the actual "learning" happens
model.fit(X_train, y_train)

# 5. Test the AI on the 20% of data it has never seen before
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("\n📊 --- FINAL EXAM RESULTS ---")
print(f"Model Accuracy: {accuracy * 100:.2f}%\n")
print("Detailed Report:")
print(classification_report(y_test, predictions, target_names=['No Fire', 'Fire']))

# 6. Save the trained brain to your hard drive so Streamlit can use it!
model_filename = 'xgboost_fire_model.pkl'
with open(model_filename, 'wb') as file:
    pickle.dump(model, file)

print(f"✅ SUCCESS: Trained AI model saved as '{model_filename}'")