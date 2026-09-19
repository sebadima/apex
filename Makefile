.PHONY: all run batch graph clean clean_ipc help

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
	@echo "make batch | make run | make graph | make clean"