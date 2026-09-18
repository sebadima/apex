import time
import zmq
from board import SCL, SDA
import busio
import adafruit_ina219

# Configurazione I2C per INA219
i2c = busio.I2C(SCL, SDA)
ina219 = adafruit_ina219.INA219(i2c)

# Configurazione ZeroMQ Publisher
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("ipc:///tmp/apex_telemetry.ipc")

SENSOR_ID = "EC-001"  # O l'ID sensore che preferisci usare

while True:
    voltage = round(ina219.bus_voltage, 2)
    current = round(ina219.current, 2)
    
    # Formato stringa semplice: SENSOR_ID,VOLTAGE,CURRENT
    payload = f"{SENSOR_ID},{voltage},{current}"
    socket.send_string(payload)
    
    time.sleep(0.1)  # Lettura a 10 Hz