.PHONY: all run batch clean help

# Target predefinito
all: batch

# Esegue la simulazione batch su 10 run stocastiche
batch:
	@python3 run_batch.py

# Esegue la simulazione singola su tracciato (default seed 42)
run:
	@python3 track_runner.py 42

# Pulizia di socket IPC e file temporanei di Python
clean:
	@rm -f /tmp/apex_*.ipc
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Ambiente di simulazione pulito."

# Guida rapida ai comandi
help:
	@echo "Comandi disponibili:"
	@echo "  make batch   - Esegue i 10 test di consumo stocastico"
	@echo "  make run     - Esegue una singola simulazione di tracciato"
	@echo "  make clean   - Rimuove socket IPC e cache Python"
