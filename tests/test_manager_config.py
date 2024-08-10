# -*- coding: utf-8 -*-

import pytest
import os
from src.managers.configManager import ConfigManager
from src.enums.configPaths import ConfigPaths as CfgPaths


# General mocks, builders and fixtures


DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "files", "default_config.yaml"
)
CUSTOM_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "files", "custom_config.yaml"
)
OTHER_CUSTOM_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "files", "other_custom_config.yaml"
)
NON_EXISTING_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "files", "non_existing_config.yaml"
)


@pytest.fixture
def config_manager() -> ConfigManager:
    cfg_mngr = ConfigManager()
    # Rewrite config paths to the test default_config file
    cfg_mngr.default_config_path = DEFAULT_CONFIG_PATH
    cfg_mngr.selected_config_path = DEFAULT_CONFIG_PATH
    cfg_mngr.loadConfigFile(DEFAULT_CONFIG_PATH)
    return cfg_mngr


# Tests


def test_manager_init() -> None:
    cfg_mngr = ConfigManager()
    assert cfg_mngr.config_dict is not None


def test_load_custom_config(config_manager: ConfigManager) -> None:
    config_manager.loadConfigFile(CUSTOM_CONFIG_PATH)
    assert os.path.samefile(config_manager.getCurrentFilePath(), CUSTOM_CONFIG_PATH)
    # Check that custom path has been saved in default config
    config_manager.selected_config_path = DEFAULT_CONFIG_PATH
    config_manager.loadConfig(DEFAULT_CONFIG_PATH)
    saved_path = config_manager.getConfigValue(CfgPaths.CUSTOM_CONFIG_PATH.value, None)
    assert os.path.samefile(saved_path, CUSTOM_CONFIG_PATH)
    # Remove custom config path in default yaml at end of test
    config_manager.setConfigValue(CfgPaths.CUSTOM_CONFIG_PATH.value, None)


def test_load_non_existing_config(config_manager: ConfigManager) -> None:
    config_manager.loadConfigFile(NON_EXISTING_CONFIG_PATH)
    assert os.path.samefile(config_manager.getCurrentFilePath(), DEFAULT_CONFIG_PATH)


def test_load_other_custom_config_from_custom(config_manager: ConfigManager) -> None:
    """
    If a custom config has been loaded and the user wants to load
    another custom config, update custom config path in default config.
    """
    config_manager.loadConfigFile(CUSTOM_CONFIG_PATH)
    config_manager.loadConfigFile(OTHER_CUSTOM_CONFIG_PATH)
    assert os.path.samefile(
        config_manager.getCurrentFilePath(), OTHER_CUSTOM_CONFIG_PATH
    )
    # Check that custom path has been updated in default config
    config_manager.selected_config_path = DEFAULT_CONFIG_PATH
    config_manager.loadConfig(DEFAULT_CONFIG_PATH)
    saved_path = config_manager.getConfigValue(CfgPaths.CUSTOM_CONFIG_PATH.value, None)
    assert os.path.samefile(saved_path, OTHER_CUSTOM_CONFIG_PATH)
    # Remove custom config path in default yaml at end of test
    config_manager.setConfigValue(CfgPaths.CUSTOM_CONFIG_PATH.value, None)


def test_load_default_config_from_custom(config_manager: ConfigManager) -> None:
    """
    If a custom config has been loaded and the user wants to load
    the default config, remove custom config path from default config.
    """
    if not os.path.samefile(config_manager.getCurrentFilePath(), CUSTOM_CONFIG_PATH):
        config_manager.loadConfigFile(CUSTOM_CONFIG_PATH)
    config_manager.loadConfigFile(DEFAULT_CONFIG_PATH)
    saved_path = config_manager.getConfigValue(CfgPaths.CUSTOM_CONFIG_PATH.value, None)
    assert saved_path == None
