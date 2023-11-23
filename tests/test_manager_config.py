# -*- coding: utf-8 -*-

import pytest
import os
from src.managers.configManager import ConfigManager
from src.enums.configPaths import ConfigPaths as CfgPaths


# General mocks, builders and fixtures


def defaultConfigPath() -> str:
    return os.path.join(os.path.dirname(__file__), "files", "default_config.yaml")


def customConfigPath() -> str:
    return os.path.join(os.path.dirname(__file__), "files", "custom_config.yaml")


def otherCustomConfigPath() -> str:
    return os.path.join(os.path.dirname(__file__), "files", "other_custom_config.yaml")


@pytest.fixture
def config_manager() -> ConfigManager:
    cfg_mngr = ConfigManager()
    # Rewrite config paths to the test default_config file
    cfg_mngr.default_config_path = defaultConfigPath()
    cfg_mngr.selected_config_path = defaultConfigPath()
    cfg_mngr.loadConfigFile(defaultConfigPath())
    return cfg_mngr


# Tests


def test_manager_init() -> None:
    cfg_mngr = ConfigManager()
    assert cfg_mngr.config_dict is not None


def test_load_custom_config(config_manager: ConfigManager) -> None:
    config_manager.loadConfigFile(customConfigPath())
    assert os.path.samefile(config_manager.getCurrentFilePath(), customConfigPath())
    # Check that custom path has been saved in default config
    config_manager.selected_config_path = defaultConfigPath()
    config_manager.loadConfig(defaultConfigPath())
    saved_path = config_manager.getConfigValue(
        CfgPaths.GENERAL_CUSTOM_CONFIG_PATH.value, None
    )
    assert os.path.samefile(saved_path, customConfigPath())


def test_load_other_custom_config_from_custom(config_manager: ConfigManager) -> None:
    """
    If a custom config has been loaded and the user wants to load
    another custom config, update custom config path in default config.
    """
    if not os.path.samefile(config_manager.getCurrentFilePath(), customConfigPath()):
        config_manager.loadConfigFile(customConfigPath())
    config_manager.loadConfigFile(otherCustomConfigPath())
    assert os.path.samefile(
        config_manager.getCurrentFilePath(), otherCustomConfigPath()
    )
    # Check that custom path has been updated in default config
    config_manager.selected_config_path = defaultConfigPath()
    config_manager.loadConfig(defaultConfigPath())
    saved_path = config_manager.getConfigValue(
        CfgPaths.GENERAL_CUSTOM_CONFIG_PATH.value, None
    )
    assert os.path.samefile(saved_path, otherCustomConfigPath())


def test_load_default_config_from_custom(config_manager: ConfigManager) -> None:
    """
    If a custom config has been loaded and the user wants to load
    the default config, remove custom config path from default config.
    """
    if not os.path.samefile(config_manager.getCurrentFilePath(), customConfigPath()):
        config_manager.loadConfigFile(customConfigPath())
    config_manager.loadConfigFile(defaultConfigPath())
    saved_path = config_manager.getConfigValue(
        CfgPaths.GENERAL_CUSTOM_CONFIG_PATH.value, None
    )
    assert saved_path == None
