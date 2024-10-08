# -*- coding: utf-8 -*-

import os
import yaml
from typing import Any
from loguru import logger


_DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "config.yaml"
)
_CUSTOM_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "custom.yaml")


class ConfigManager:
    def __init__(self) -> None:
        self.config_dict: dict = {}
        self.config_path: str = _DEFAULT_CONFIG_PATH
        if os.path.exists(_CUSTOM_CONFIG_PATH):
            self.config_path = _CUSTOM_CONFIG_PATH
        self.loadConfig(self.config_path)

    def loadConfig(self, path) -> None:
        with open(path, "r") as file:
            self.config_dict = yaml.load(file, Loader=yaml.FullLoader)

    def updateCustomConfig(self, streamlit_file_uploader) -> None:
        self.config_path = _CUSTOM_CONFIG_PATH
        self.config_dict = yaml.load(streamlit_file_uploader, Loader=yaml.FullLoader)
        self.saveConfig()

    def saveConfig(self) -> None:
        with open(self.config_path, "w") as file:
            yaml.dump(self.config_dict, file, sort_keys=False)

    # Setters and getters

    def setConfigValue(self, key_path: str, value: Any) -> None:
        keys = key_path.split(".")
        config = self.config_dict
        for key in keys[:-1]:
            config = config.get(key, {})
        config[keys[-1]] = value
        self.saveConfig()

    def getConfigValue(
        self, key_path: str, default_value: Any | None = None
    ) -> Any | None:
        keys = key_path.split(".")
        config = self.config_dict
        for key in keys[:-1]:
            config = config.get(key, {})
        return config.get(keys[-1], default_value)

    def getCurrentFilePath(self) -> str:
        return self.config_path
