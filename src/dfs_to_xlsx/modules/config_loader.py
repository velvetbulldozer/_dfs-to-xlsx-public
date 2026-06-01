# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
from pathlib import Path  # Import Path for file path handling
from typing import Any  # Import Any and Optional for type annotations

# Third-party imports
import yaml  # Import PyYAML for YAML parsing


class ConfigLoader:
    """Loads and resolves configuration values from a YAML file.

    This class encapsulates all logic related to reading configuration
    from disk and applying precedence rules. It is designed to be used
    by components such as `XlsxDataFrameWriter` that accept both YAML
    configuration and constructor overrides.

    Attributes:
        config_path (Optional[str]): Path to the YAML configuration file.
        _config (dict[str, Any]): Parsed YAML configuration dictionary.

    """

    def __init__(self, config_path: str | None) -> None:
        """Initialize the ConfigLoader.

        Args:
            config_path (Optional[str]): Path to a YAML configuration file.
                If None, an empty configuration is used.

        """
        self.config_path = config_path
        self._config = self._load()
        self.data = {}

        if config_path:
            with open(config_path, encoding="utf-8") as f:
                self.data = yaml.safe_load(f) or {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def _load(self) -> dict[str, Any]:
        """Load configuration from the YAML file.

        Returns:
            dict[str, Any]: Parsed configuration dictionary. Empty if no file
            is provided.

        Raises:
            FileNotFoundError: If the provided config path does not exist.
            yaml.YAMLError: If the YAML file contains invalid syntax.

        """
        if self.config_path is None:
            return {}

        path = Path(self.config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(path, encoding="utf-8") as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError as exc:
                raise yaml.YAMLError(
                    f"Invalid YAML in config file: {self.config_path}"
                ) from exc

    def resolve(self, field: str, override: Any, default: Any) -> Any:
        """Resolve a configuration value using precedence rules.

        Precedence:
            1. Constructor override
            2. YAML configuration
            3. Default value

        Args:
            field (str): Name of the configuration field.
            override (Any): Value provided via constructor.
            default (Any): Fallback default value.

        Returns:
            Any: The resolved configuration value.

        """
        if override is not None:
            return override
        return self._config.get(field, default)

    # Expose raw configuration as a property for direct access if needed
    @property
    def raw(self) -> dict[str, Any]:
        """Return the raw YAML configuration.

        Returns:
            dict[str, Any]: Parsed YAML configuration.

        """
        return self._config
