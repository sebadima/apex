import sys
import zmq

# Soglie operative per la batteria LiPo 2S
VOLTAGE_WARN = 7.0      # V: Soglia pre-allarme (Modalità ECO)
VOLTAGE_CUTOFF = 6.6    # V: Cut-off critico (Arresto di emergenza)
CURRENT_LIMIT_A = 3.0  # A: Soglia sovracorrente

context = zmq.Context()
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("ipc:///tmp/apex_telemetry.ipc")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("Apex Control Node attivo [Modulo Decisionale 50 Hz]")

system_state = "NOMINAL"

try:
    while True:
        raw_msg = sub_socket.recv_string()
        parts = raw_msg.split(",")

        if len(parts) >= 4:
            v_bat = float(parts[2])
            i_bat = float(parts[3])

            # ----------------------------------------------------
            # LOGICA DECISIONALE
            # ----------------------------------------------------

            # 1. CUT-OFF CRITICO
            if v_bat <= VOLTAGE_CUTOFF:
                if system_state != "EMERGENCY_STOP":
                    system_state = "EMERGENCY_STOP"
                    print(f"[DECISIONE APEX] 🚨 CUT-OFF TENSIONE ({v_bat}V) -> AZIONE: ARRESTO MOTORI")

            # 2. PROTEZIONE SOVRACORRENTE
            elif i_bat >= CURRENT_LIMIT_A:
                if system_state != "OVERCURRENT":
                    system_state = "OVERCURRENT"
                    print(f"[DECISIONE APEX] ⚠️ SOVRACORRENTE ({i_bat}A) -> AZIONE: TAGLIO POTENZA 50%")

            # 3. BATTERIA SCARICA
            elif v_bat <= VOLTAGE_WARN:
                if system_state != "LOW_BATTERY":
                    system_state = "LOW_BATTERY"
                    print(f"[DECISIONE APEX] 🟡 TENSIONE BASSA ({v_bat}V) -> AZIONE: MODALITÀ ECO")

            # 4. STATO REPO/NOMINALE
            elif v_bat > VOLTAGE_WARN and i_bat < CURRENT_LIMIT_A and system_state != "NOMINAL":
                system_state = "NOMINAL"
                print(f"[DECISIONE APEX] ✅ STATO NOMINALE ({v_bat}V, {i_bat}A) -> AZIONE: RIPRISTINO POTENZA")

except KeyboardInterrupt:
    print("\nNodo decisionale arrestato.")
    sys.exit(0)
