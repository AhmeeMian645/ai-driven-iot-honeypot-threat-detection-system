import pandas as pd

INPUT_FILE = "iot_attacks.csv"
OUTPUT_FILE = "final_dataset.csv"

print("[+] Loading dataset...")
df = pd.read_csv(INPUT_FILE)

# -----------------------------
# 1. Remove null / empty labels
# -----------------------------
df = df.dropna(subset=["label"])

# -----------------------------
# 2. Keep only important attacks
# -----------------------------
valid_labels = [
    "PORT_SCAN",
    "SSH_BRUTE_FORCE",
    "MQTT_ABUSE"
]

df = df[df["label"].isin(valid_labels)]

# -----------------------------
# 3. Fill missing numeric values
# -----------------------------
df["src_port"] = df["src_port"].fillna(0)
df["dest_port"] = df["dest_port"].fillna(0)
df["packets"] = df["packets"].fillna(0)
df["bytes"] = df["bytes"].fillna(0)
df["severity"] = df["severity"].fillna(1)

# -----------------------------
# 4. Convert data types
# -----------------------------
df["src_port"] = df["src_port"].astype(int)
df["dest_port"] = df["dest_port"].astype(int)
df["packets"] = df["packets"].astype(int)
df["bytes"] = df["bytes"].astype(int)
df["severity"] = df["severity"].astype(int)

# -----------------------------
# 5. Save clean dataset
# -----------------------------
df.to_csv(OUTPUT_FILE, index=False)

print(f"[+] Clean dataset saved: {OUTPUT_FILE}")
print(f"[+] Total samples: {len(df)}")

# -----------------------------
# 6. Show class distribution
# -----------------------------
print("\n[+] Attack Distribution:")
print(df["label"].value_counts())
