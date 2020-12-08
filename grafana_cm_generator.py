#!/usr/bin/env python

from dataclasses import dataclass
from itertools import chain
import json
from pathlib import Path
import re
from typing import Iterator

import fire  # type: ignore
import requests
import yaml


def replace_datasource(content: str) -> str:
    return re.sub(r'"datasource": *"\$[^,]*', '"datasource": "Prometheus"', content)


@dataclass
class GrafanaConfigmap:
    content: str
    directory_name: str
    name: str

    def write(
        self,
        output_path: Path,
        namespace: str,
        configmap_prefix: str,
        target_prefix: str,
    ) -> None:
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{configmap_prefix}{self.name}",
                "namespace": namespace,
                "annotations": {
                    "k8s-sidecar-target-directory": f"{target_prefix}{self.directory_name}"
                },
                "labels": {"grafana_dashboard": "1"},
            },
            "data": {f"{self.name}.json": replace_datasource(self.content)},
        }
        with (output_path / f"{self.name}.yaml").open("w") as fd:
            fd.write(yaml.dump(configmap))


def _generate_from_json(directory: Path) -> Iterator[GrafanaConfigmap]:
    for f in directory.glob("*.json"):
        name = f"{directory.name}-{f.stem}"
        with f.open("r") as fd:
            content = fd.read()
        yield GrafanaConfigmap(
            name=name, directory_name=directory.name, content=content
        )


def _generate_from_config(directory: Path) -> Iterator[GrafanaConfigmap]:
    if not (directory / "grafana.yaml").is_file():
        return

    with (directory / "grafana.yaml").open("r") as fd:
        dashboards = yaml.load(fd, Loader=yaml.SafeLoader)
    for dashboard in dashboards:
        r = requests.get(
            f"https://grafana.com/api/dashboards/{dashboard['id']}/revisions/{dashboard['revision']}/download"
        )
        r.encoding = "utf8"
        yield GrafanaConfigmap(
            name=f"{directory.name}-{dashboard['name']}",
            directory_name=directory.name,
            content=json.dumps(r.json()),
        )


def build(
    input_directory: str = ".",
    output_directory: str = "./dist",
    namespace: str = "monitoring",
    configmap_prefix: str = "dashboard-",
    target_prefix: str = "/tmp/dashboards/",
) -> None:
    """Generate grafana dashboard configmaps
    :param input_directory: Input directory (default to current directory)
    :param output_directory: Output directory (default to "./dist")
    :param namespace: Kubernetes namespace for configmaps (default to "monitoring")
    :param configmap_prefix: Prefix name (default to "dashboard-")
    :param target_prefix: Target prefix, for k8s-sidecar-target-directory annotation (default to "/tmp/dashboards/")
    """
    output_path = Path(output_directory)
    output_path.mkdir(exist_ok=True)
    for directory in filter(lambda x: x.is_dir(), Path(input_directory).iterdir()):
        for configmap in chain(
            _generate_from_json(directory), _generate_from_config(directory)
        ):
            configmap.write(output_path, namespace, configmap_prefix, target_prefix)


def main() -> None:
    fire.Fire(build)


if __name__ == "__main__":
    main()
