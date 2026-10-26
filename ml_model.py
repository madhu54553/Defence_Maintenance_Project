
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Sample training dataset
data = {
    "temperature": [
        35, 40, 45, 50, 55, 60, 65, 70,
        38, 42, 48, 52, 58, 62, 68, 75,
        30, 44, 47, 57, 63, 72, 78, 80
    ],
    "vibration": [
        1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0,
        1.1, 1.4, 1.8, 2.2, 2.8, 3.2, 3.8, 4.2,
        0.8, 1.3, 1.7, 2.6, 3.1, 3.7, 4.3, 4.5
    ],
    "operating_hours": [
        100, 150, 200, 250, 300, 400, 500, 600,
        120, 180, 220, 280, 350, 450, 550, 650,
        80, 170, 210, 320, 420, 520, 620, 700
    ],
    "maintenance": [
        0, 0, 0, 0, 1, 1, 1, 1,
        0, 0, 0, 1, 1, 1, 1, 1,
        0, 0, 0, 1, 1, 1, 1, 1
    ]
}

df = pd.DataFrame(data)

# Input features and target
X = df[["temperature", "vibration", "operating_hours"]]
y = df["maintenance"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# Train model
model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

# Test model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print("Model Accuracy:", round(accuracy * 100, 2), "%")

print("Model trained successfully!")
print("Model accuracy:", round(accuracy * 100, 2), "%")

# Test prediction
sample = pd.DataFrame(
    [[65, 3.5, 500]],
    columns=["temperature", "vibration", "operating_hours"]
)

result = model.predict(sample)[0]

if result == 1:
    print("Prediction: Maintenance Required")
else:
    print("Prediction: Normal")
