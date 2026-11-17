import json
import time
import joblib
import pandas as pd

EVE_FILE = "/var/log/suricata/eve.json"

model = joblib.load("iot_attack_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
protocol_encoder = joblib.load("protocol_encoder.pkl")

# Reverse label lookup
label_map = dict(enumerate(label_encoder.classes_))


def encode_protocol(proto):
    try:
        return protocol_encoder.transform([proto])[0]
    except Exception:
        return 0   # fallback


def extract_features(event):
    flow = event.get("flow", {})
    proto = event.get("proto", "tcp")

    # Define the exact 6 column names expected by your trained model
    feature_cols = ["protocol", "src_port", "dest_port", "severity", "packets", "bytes"]

    # Store the raw values in a variable
    raw_values = [[
        encode_protocol(proto),
        event.get("src_port", 0) or 0,
        event.get("dest_port", 0) or 0,
        event.get("alert", {}).get("severity", 1),
        flow.get("pkts_toserver", 0),
        flow.get("bytes_toserver", 0)
    ]]

    # Return them wrapped in a Pandas DataFrame to suppress scikit-learn warnings
    return pd.DataFrame(raw_values, columns=feature_cols)


print("[+] Live AI Detector Started...")
print("[+] Waiting for Suricata alerts...\n")

with open(EVE_FILE, "r") as f:
    f.seek(0, 2)

    while True:
        line = f.readline()

        if not line:
            time.sleep(0.5)
            continue

        try:
            event = json.loads(line)

            if event.get("event_type") == "alert":
                features = extract_features(event)

                prediction = model.predict(features)[0]
                attack_type = label_map[prediction]

                # AI confidence score
                confidence = max(model.predict_proba(features)[0]) * 100

                # Create a structured JSON event
                ai_event = {
                    "event_type": "ai_classification",
                    "predicted_attack": str(attack_type),
                    "confidence": round(float(confidence), 1),
                    "source_ip": event.get("src_ip"),
                    "destination_ip": event.get("dest_ip"),
                    "destination_port": event.get("dest_port")
                }

                # Convert the dictionary into a JSON string
                json_log = json.dumps(ai_event)

                # 1. Display readable output on terminal
                print(
                    f"🚨 AI DETECTOR: ATTACK={attack_type} | "
                    f"CONFIDENCE={confidence:.1f}% | "
                    f"SRC={event.get('src_ip')} | "
                    f"DEST={event.get('dest_ip')} | "
                    f"PORT={event.get('dest_port')}"
                )

                # 2. Export JSON event to Wazuh log file
                with open("/var/log/ai_honeypot.log", "a", encoding="utf-8") as log_file:
                    log_file.write(json_log + "\n")

        except Exception as e:
            continue
