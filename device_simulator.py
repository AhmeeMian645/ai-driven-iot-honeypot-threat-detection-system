import paho.mqtt.client as mqtt
import time
import json
import numpy as np
import datetime
import socket
import threading

client = mqtt.Client()

# Load config
with open("config.json") as f:
    config = json.load(f)

# Create devices
device_config = []
for devices in config['devices']:
    for n in range(devices['device_count']):
        dev = {}
        dev['device_id'] = devices['type'] + "_" + str(n)
        dev['device_type'] = devices['type']
        dev['publish_frequency'] = devices['publish_frequency']
        dev['std_val'] = devices['std_val']
        dev['publish_topic'] = devices['publish_topic']
        device_config.append(dev)

# 🔥 PORT MAPPING (VERY IMPORTANT)
DEVICE_PORTS = {
    "temperature": 5001,
    "humidity": 5002,
    "bulb": 5003,
    "camera": 5004
}

# 🔥 SOCKET SERVER FOR EACH DEVICE
def start_device_server(device_type, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(5)
    print(f"[PORT ACTIVE] {device_type} running on port {port}")

    while True:
        conn, addr = s.accept()
        print(f"[{device_type.upper()} ATTACK] Connection from {addr}")
        conn.send(f"{device_type} device response\n".encode())
        conn.close()

# Start servers in threads
for dtype, port in DEVICE_PORTS.items():
    t = threading.Thread(target=start_device_server, args=(dtype, port))
    t.daemon = True
    t.start()

# MQTT connect
client.connect(config["broker_host"], config["broker_port"], 60)
client.loop_start()

clock = 0

while True:
    time.sleep(1)
    clock += 1

    for devices in device_config:
        if clock % devices['publish_frequency'] == 0:
            message = {}
            message["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message["device_id"] = devices["device_id"]
            message["device_type"] = devices["device_type"]

            if devices["device_type"] == "bulb":
                message["status"] = np.random.choice(["ON", "OFF"])
                message["brightness"] = int(np.random.randint(0, 100))

            elif devices["device_type"] == "camera":
                message["motion"] = bool(np.random.choice([0, 1]))
                message["status"] = "active"

            else:
                message["value"] = round(np.random.normal(devices["std_val"], 2), 2)

            client.publish(devices["publish_topic"], json.dumps(message))
            print("[MQTT SENT]:", message)
