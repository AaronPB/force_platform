# -*- coding: utf-8 -*-

# Replace current managers to load a predefined set of data.

import os
import yaml
import pandas as pd
from src.managers.sensorManager import SensorManager
from src.managers.dataManager import DataManager
from src.enums.sensorStatus import SStatus


class DataTester:
    def __init__(self):
        raw_data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "tests",
            "files",
            "full_dataset_RAW.csv",
        )
        calib_data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "tests",
            "files",
            "full_dataset.csv",
        )
        self.df_raw = pd.read_csv(raw_data_path)
        self.df = pd.read_csv(calib_data_path)
        self.cfg_mngr = CustomConfigManager()

    def overrideManagers(
        self, sensor_manager: SensorManager, data_manager: DataManager
    ) -> None:
        sensor_manager.setup(self.cfg_mngr)
        # Modify sensor status to available
        for group in sensor_manager.getGroups():
            for sensor in group.getSensors().values():
                sensor.status = SStatus.AVAILABLE
        # Replace imported data
        time_list = self.df.iloc[:, 0]
        data_manager.df_raw = self.df_raw.iloc[:, 1:]
        data_manager.df_calibrated = self.df.iloc[:, 1:]
        data_manager.timestamp_list = time_list
        data_manager.timeincr_list = [(t - time_list[0]) / 1000 for t in time_list]


class CustomConfigManager:
    def __init__(self) -> None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        with open(config_path, "r") as file:
            self.config_dict = yaml.load(file, Loader=yaml.FullLoader)

    def setConfigValue(self, key_path: str, value) -> None:
        pass

    def getConfigValue(self, key_path: str, default_value=None):
        keys = key_path.split(".")
        config = self.config_dict
        for key in keys[:-1]:
            config = config.get(key, {})
        return config.get(keys[-1], default_value)
