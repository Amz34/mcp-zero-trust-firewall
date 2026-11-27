.PHONY: all test benchmark run clean

all: test benchmark

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

benchmark:
	PYTHONPATH=src python3 benchmarks/run_benchmarks.py

run:
	PYTHONPATH=src python3 -m mcp_firewall.cli --help

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info .pytest_cache
