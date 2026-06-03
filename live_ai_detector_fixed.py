import json
import time
import joblib

EVE_FILE = "/var/log/suricata/eve.json"

model = joblib.load("iot_attack_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
protocol_encoder = joblib.load("protocol_encoder.pkl")

# Reverse label lookup
label_map = dict(enumerate(label_encoder.classes_))

def encode_protocol(proto):
    try:
        return protocol_encoder.transform([proto])[0]
    except:
        return 0   # fallback

def extract_features(event):
    flow = event.get("flow", {})

    proto = event.get("proto", "tcp")

    return [[
        encode_protocol(proto),
        event.get("src_port", 0) or 0,
        event.get("dest_port", 0) or 0,
        event.get("alert", {}).get("severity", 1),
        flow.get("pkts_toserver", 0),
        flow.get("bytes_toserver", 0)
    ]]

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

                print(
                    f"🚨 ATTACK: {attack_type} | "
                    f"Confidence: {confidence:.1f}% | "
                    f"{event.get('src_ip')} → {event.get('dest_ip')} "
                    f"| Port: {event.get('dest_port')}"
                )

        except Exception as e:
            continue
