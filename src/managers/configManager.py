# -*- coding: utf-8 -*-

import os
import yaml
from src.enums.configPaths import ConfigPaths
from src.utils import LogHandler


class ConfigManager:
    def __init__(self) -> None:
        self.log_handler = LogHandler(str(__class__.__name__))
        self.default_config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'config.yaml')
        self.selected_config_path = self.default_config_path

        self.loadConfigFile(self.selected_config_path)

    def loadConfigFile(self, file_path) -> None:
        if file_path == self.default_config_path:
            self.log_handler.logger.info(
                f'Loading default config settings: {file_path}.')
            self.loadConfig(file_path)
            # Check custom file path
            custom_config_path = self.getConfigValue(
                ConfigPaths.GENERAL_CUSTOM_CONFIG_PATH.value)
            if custom_config_path:
                self.loadConfigFile(custom_config_path)
            return
        if not os.path.exists(file_path):
            self.log_handler.logger.warn(
                f'Could not find custom config file: {file_path}.')
            return
        self.log_handler.logger.info(f'Loading custom file: {file_path}.')
        # First save new custom config path in default config
        self.loadConfig(self.default_config_path)
        self.setConfigValue(
            ConfigPaths.GENERAL_CUSTOM_CONFIG_PATH.value, str(file_path))
        self.loadConfig(file_path)
        self.selected_config_path = file_path

    def loadConfig(self, path) -> None:
        with open(path, "r") as file:
            self.config_dict = yaml.load(file, Loader=yaml.FullLoader)

    def saveConfig(self) -> None:
        with open(self.selected_config_path, "w") as file:
            yaml.dump(self.config_dict, file, sort_keys=False)

    # Setters and getters

    def setConfigValue(self, key_path: str, value) -> None:
        keys = key_path.split('.')
        config = self.config_dict
        for key in keys[:-1]:
            config = config.get(key, {})
        config[keys[-1]] = value
        self.saveConfig()

    def getConfigValue(self, key_path: str, default_value=None):
        keys = key_path.split('.')
        config = self.config_dict
        for key in keys[:-1]:
            config = config.get(key, {})
        return config.get(keys[-1], default_value)

    def getCurrentFilePath(self):
        return self.selected_config_path
