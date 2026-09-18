import time
import requests
import zmq

BASE_API_URL = "https://kaspian.robotdazero.it/sensor_api/{}/sensor-data/"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxODE5MjAzMjE4LCJpYXQiOjE3ODc2NjcyMTgsImp0aSI6ImJmNDgzNTAwMjI5ZTRmZTY4MzE4MDM1YjljNjkyZjNlIiwic3ViIjoiMSIsImJvYXJkX2NvZGUiOiIwMDEifQ.pRAmSkojHzkt_kZ---RVFnKEUDboQz3-cnJAC9TF0rU"
BOARD_ID = "1"

# Configurazione ZeroMQ Subscriber
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("ipc:///tmp/apex_telemetry.ipc")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

url = BASE_API_URL.format(BOARD_ID)

while True:
    raw_data = socket.recv_string()
    sensor_id, voltage, current = raw_data.split(",")
    
    # Mappatura dati verso Kaspian
    payload = {
        "sensor_id": sensor_id,
        "soil_moisture": float(voltage),
        "ec": float(current)
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=2.0)
        if response.status_code == 201 or response.status_code == 200:
            print(f"✓ Inviato {sensor_id}: V={voltage} | I={current}")
        else:
            print(f"✗ Errore HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"✗ Errore di connessione: {e}")
        