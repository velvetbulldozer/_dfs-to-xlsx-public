"""Tests for the ConfigLoader class.

This suite verifies that configuration values are correctly loaded from YAML
files, that defaults are used when no config file is provided, and that the
precedence rules (override > YAML > default) behave as expected.
"""

from src.dfs_to_xlsx.modules.config_loader import ConfigLoader


def test_loads_yaml_file(tmp_path):
    """Test that ConfigLoader correctly loads values from a YAML file."""
    # Create a temporary YAML file
    config_file = tmp_path / "config.yaml"
    config_file.write_text("batch_size: 50\nname: test_export", encoding="utf-8")

    loader = ConfigLoader(str(config_file))

    # Validate loaded values
    assert loader.get("batch_size") == 50
    assert loader.get("name") == "test_export"


def test_no_config_file_uses_empty_defaults():
    """Test that ConfigLoader behaves correctly when no config file is provided."""
    loader = ConfigLoader(None)

    # Missing key → fallback returned
    assert loader.get("missing_key", "fallback") == "fallback"

    # Raw config should be empty
    assert loader.raw == {}


def test_resolve_precedence(tmp_path):
    """Test that resolve() respects override > YAML > default precedence."""
    # Create YAML file with a value
    config_file = tmp_path / "config.yaml"
    config_file.write_text("batch_size: 100", encoding="utf-8")

    loader = ConfigLoader(str(config_file))

    # 1. Override wins
    assert loader.resolve("batch_size", override=20, default=5) == 20

    # 2. YAML value wins when override is None
    assert loader.resolve("batch_size", override=None, default=5) == 100

    # 3. Default wins when neither override nor YAML has the key
    assert loader.resolve("missing_key", override=None, default=999) == 999
