.PHONY: all run batch graph graph3d clean clean_ipc help

all: batch

batch:
	@python3 run_batch.py

run: clean_ipc
	@echo "Elaborazione cinematica e IPC in esecuzione [Terminale 1]"
	@python3 track_runner.py 42

graph:
	@echo "Esecuzione routine di purging zombie in RAM..."
	@ps aux | grep '[p]ython3 track_runner.py' | awk '{print $$2}' | xargs -r kill -9
	@ps aux | grep '[p]ython3 telemetry_emulator.py' | awk '{print $$2}' | xargs -r kill -9
	@ps aux | grep '[p]ython3 track_visualizer.py' | awk '{print $$2}' | xargs -r kill -9
	@rm -f /tmp/apex_*.ipc
	@echo "=========================================================="
	@echo "AVVISO: Questo target avvia SOLO l'interfaccia grafica."
	@echo "Devi aprire un ALTRO TERMINALE e lanciare 'make run' per avviare il motore fisico."
	@echo "Senza 'make run', l'interfaccia rimarrà congelata in ascolto su IPC."
	@echo "=========================================================="
	@python3 track_visualizer.py

graph3d: clean_ipc
	@echo "=========================================================="
	@echo "APEX 3D - simulatore + visualizzatore"
	@echo "=========================================================="
	@echo "Avvio apex_simulator.py..."
	@python3 apex_simulator.py 42 & \
	SIM_PID=$$!; \
	trap 'kill $$SIM_PID 2>/dev/null || true; wait $$SIM_PID 2>/dev/null || true' INT TERM EXIT; \
	echo "Avvio apex_viewer.py..."; \
	python3 apex_viewer.py; \
	STATUS=$$?; \
	kill $$SIM_PID 2>/dev/null || true; \
	wait $$SIM_PID 2>/dev/null || true; \
	exit $$STATUS

clean_ipc:
	@rm -f /tmp/apex_*.ipc

clean: clean_ipc
	@ps aux | grep '[p]ython3 track_runner.py' | awk '{print $$2}' | xargs -r kill -9
	@ps aux | grep '[p]ython3 telemetry_emulator.py' | awk '{print $$2}' | xargs -r kill -9
	@ps aux | grep '[p]ython3 track_visualizer.py' | awk '{print $$2}' | xargs -r kill -9
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Ambiente azzerato. Processi annientati."

help:
	@echo "make batch | make run | make graph | make graph3d | make clean"
