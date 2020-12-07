FROM quay.io/bitnami/python:3.9

WORKDIR /src

COPY pyproject.toml setup.cfg setup.py ./
RUN pip install -e .
COPY grafana_cm_generator.py ./

WORKDIR /work
CMD grafana-cm-generator
