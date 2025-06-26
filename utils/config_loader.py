"""Utility for loading YAML configuration files."""
from __future__ import annotations

import os
import yaml
from typing import Any, Dict


def load_yaml(path: str) -> Dict[str, Any]:
    """Load a YAML file from the given path."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_config(name: str) -> Dict[str, Any]:
    """Load a config file from the config directory by name without extension."""
    base = os.path.join(os.path.dirname(__file__), "..", "config")
    path = os.path.join(base, f"{name}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    return load_yaml(path)
