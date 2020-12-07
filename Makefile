test:
	black --check grafana_cm_generator.py
	flake8 grafana_cm_generator.py
	mypy --strict grafana_cm_generator.py
