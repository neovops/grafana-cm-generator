[![Neovops](https://neovops.io/images/logos/neovops.svg)](https://neovops.io)

# Grafana configmap generator

This tool creates ConfigMap that will be read by grafana deployed with
[kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack).

It handles two types of dashboard:
 * raw JSON
 * official dashboards from [grafana.com](https://grafana.com/grafana/dashboards).

## Requirements

 * Grafana must be deployed with a sidecar that watch ConfigMaps with label `grafana_dashboard`. It's the default with
   [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
 * Folders must be pre-configured during `kube-prometheus-stack` deployment. `values.yaml` example:

```yaml
grafana:
  enabled: true

  sidecar:
    dashboards:
      defaultFolderName: kubernetes
      provider:
        folder: Kubernetes

  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: kubernetes
        orgId: 1
        folder: Kubernetes
        type: file
        disableDeletion: false
        editable: false
        options:
          path: /tmp/dashboards/kubernetes
      - name: infra
        orgId: 1
        folder: Infrastructure
        type: file
        disableDeletion: false
        editable: false
        options:
          path: /tmp/dashboards/infra
```

## Installation

```bash
pip install -e .
```

## Usage

Please check [example](example).

Each dashboard must be in a specific directory. For raw json, just put file in this directory. For dashboards from
[grafana.com](https://grafana.com/grafana/dashboards), add a `grafana.yaml` file with, for example:
```yaml
- name: nginx-ingress-controller
  id: 9614
  revision: 1
- name: alertmanager
  id: 9578
  revision: 4
- name: loki-quick-search
  id: 12019
  revision: 2
  datasource: Loki
```

To generate and install ConfigMaps:
```bash
grafana-cm-generator --input_directory=example --output_directory=example/dist
kubectl apply -f example/dist
```

## Docker

```bash
cd example
docker run --rm -ti -v "$(pwd):/work" quay.io/neovops/grafana-cm-generator:latest
kubectl apply -f dist
```

## grafana-cm-generator --help

```
NAME
    grafana-cm-generator - Generate grafana dashboard configmaps

SYNOPSIS
    grafana-cm-generator <flags>

DESCRIPTION
    Generate grafana dashboard configmaps

FLAGS
    --input_directory=INPUT_DIRECTORY
        Input directory (default to current directory)
    --output_directory=OUTPUT_DIRECTORY
        Output directory (default to "./dist")
    --namespace=NAMESPACE
        Kubernetes namespace for configmaps (default to "monitoring")
    --configmap_prefix=CONFIGMAP_PREFIX
        Prefix name (default to "dashboard-")
    --target_prefix=TARGET_PREFIX
        Target prefix, for k8s-sidecar-target-directory annotation (default to "/tmp/dashboards/")
```
