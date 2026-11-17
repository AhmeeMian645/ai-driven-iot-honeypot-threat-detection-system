# Changelog

## v2.0 (November 2026): Wazuh integration
- Added: Wazuh now reads Suricata's eve.json and the AI detector's log (wazuh/ossec-localfile-snippet.xml)
- Added: custom Wazuh rules with severity levels and MITRE ATT&CK tags for the three Suricata alerts (wazuh/local_rules.xml)
- Added: a Wazuh rule that shows each AI classification in the dashboard
- Changed: the Port Scan rule now excludes port 1883, so an MQTT flood no longer also triggers it (suricata/local.rules)
- Changed: live_ai_detector_fixed.py now also writes each verdict as JSON to /var/log/ai_honeypot.log, for Wazuh
- Added: Suricata rules file, Docker setup script, and screenshots

## v1.0: original final-year project
- Docker IoT lab (MQTT broker, device simulator, Cowrie honeypot, Kali attacker)
- Custom Suricata rules for port scan, SSH brute force, and MQTT abuse
- Random Forest classifier and a live detector that prints verdicts to the terminal
