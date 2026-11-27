PYTHON ?= $(shell for p in /home/ubuntu/.hermes/installs/*/environments/*/venv/bin/python /usr/bin/python3 python3 python; do if $$p -c "import pydantic" >/dev/null 2>&1; then echo $$p; break; fi; done)

.PHONY: all test benchmark run clean

all: test benchmark

test:
	PYTHONPATH=src $(PYTHON) tests/run_all_tests.py

benchmark:
	PYTHONPATH=src $(PYTHON) benchmarks/run_benchmarks.py

run:
	PYTHONPATH=src $(PYTHON) -m mcp_firewall.cli --help

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info .pytest_cache
