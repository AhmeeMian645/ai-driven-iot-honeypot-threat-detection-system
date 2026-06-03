import json
import csv

EVE_FILE = "/var/log/suricata/eve.json"
OUTPUT_CSV = "iot_attacks.csv"

rows = []

with open(EVE_FILE, "r") as f:
    for line in f:
        try:
            event = json.loads(line)

            # Only process alerts
            if event.get("event_type") != "alert":
                continue

            alert = event.get("alert", {})
            flow = event.get("flow", {})

            rows.append({
                "timestamp": event.get("timestamp"),
                "protocol": event.get("proto"),
                "src_ip": event.get("src_ip"),
                "src_port": event.get("src_port", 0),
                "dest_ip": event.get("dest_ip"),
                "dest_port": event.get("dest_port", 0),
                "signature": alert.get("signature"),
                "severity": alert.get("severity", 1),
                "packets": flow.get("pkts_toserver", 0),
                "bytes": flow.get("bytes_toserver", 0),

                # ✅ CRITICAL FIX → real label (NO guessing)
                "label": alert.get("signature")
            })

        except json.JSONDecodeError:
            continue

# Write CSV safely
if rows:
    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

    print(f"[+] Dataset created successfully: {OUTPUT_CSV}")
    print(f"[+] Total samples: {len(rows)}")
else:
    print("[!] No alert data found in eve.json")
