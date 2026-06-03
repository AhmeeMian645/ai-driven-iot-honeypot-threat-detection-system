import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# 1. Load CLEAN dataset
df = pd.read_csv("final_dataset.csv")

print("[+] Dataset loaded:", df.shape)

# 2. Encode protocol
protocol_encoder = LabelEncoder()
df["protocol"] = protocol_encoder.fit_transform(df["protocol"].astype(str))

# 3. Encode labels (IMPORTANT)
label_encoder = LabelEncoder()
df["label"] = label_encoder.fit_transform(df["label"])

print("[+] Labels:", list(label_encoder.classes_))

# 4. Select features
X = df[[
    "protocol",
    "src_port",
    "dest_port",
    "severity",
    "packets",
    "bytes"
]]

y = df["label"]

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y   # IMPORTANT for balanced learning
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\n=== MODEL EVALUATION ===\n")
print(classification_report(y_test, y_pred))

# 8. Save everything
joblib.dump(model, "iot_attack_model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")
joblib.dump(protocol_encoder, "protocol_encoder.pkl")

print("\n[+] Model trained and saved successfully")
