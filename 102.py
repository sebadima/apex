import time
import zmq

# Inizializzazione ZeroMQ Publisher
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("ipc:///tmp/apex_telemetry.ipc")

def read_ina219():
    # Sostituire con le letture reali dell'INA219
    return 3.74, 420.5

while True:
    v_bus, i_ma = read_ina219()
    ts = time.time()
    
    # Payload piatto in byte-array (zero overhead JSON)
    payload = f"{ts},{v_bus},{i_ma}".encode('utf-8')
    socket.send(payload)
    
    time.sleep(0.02) # 50 Hz
