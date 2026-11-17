#!/bin/bash
# IoT Honeypot lab setup (run from the repo folder)
docker network create vlan10_net
docker network create vlan20_net


docker run -d --name attacker --network vlan10_net kalilinux/kali-rolling tail -f /dev/null
docker network connect vlan10_net attacker
docker network connect vlan20_net attacker
docker run -d --name mqtt_broker --network vlan10_net -p 1883:1883 eclipse-mosquitto
docker network connect vlan10_net  mqtt_broker
docker run -d --name iot-simulator --network vlan10_net \
  -v $(pwd)/device_simulator.py:/device_simulator.py \
  python:3-slim \
  sh -c "pip install --no-cache-dir paho-mqtt numpy && python /device_simulator.py"
docker network connect vlan10_net  iot-simulator
docker run -d --name honeypot-cowrie --network vlan20_net cowrie/cowrie
docker network connect vlan20_net  honeypot-cowrie

