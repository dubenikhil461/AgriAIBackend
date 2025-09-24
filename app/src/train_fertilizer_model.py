import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("datasets/Fertilizer-data.csv")

# Clean column names
data.columns = data.columns.str.strip()

# Features and target
X = data[['Nitrogen', 'Potassium', 'Phosphorous', 'Temparature', 'Humidity']]  # Use appropriate features
y = data['Fertilizer Name']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save trained model
joblib.dump(model, "models/fertilizer_model.pkl")

print("✅ Fertilizer model trained and saved!")
