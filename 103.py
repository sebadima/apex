import zmq
import psycopg

# Connessione a PostgreSQL
conn = psycopg.connect("dbname=apex_db user=postgres password=secret host=localhost")
cursor = conn.cursor()

# Inizializzazione ZeroMQ Subscriber
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("ipc:///tmp/apex_telemetry.ipc")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("Apex Core avviato. In ascolto sulla telemetria...")

buffer = []

try:
    while True:
        raw_data = socket.recv().decode('utf-8')
        ts, v_bus, i_ma = map(float, raw_data.split(','))
        
        buffer.append((ts, v_bus, i_ma))
        
        # Scrittura a blocchi (batching) per non bloccare il loop
        if len(buffer) >= 50:
            cursor.executemany(
                "INSERT INTO telemetry (ts, voltage, current) VALUES (%s, %s, %s)",
                buffer
            )
            conn.commit()
            buffer.clear()
            
except KeyboardInterrupt:
    conn.close()
