import os
import glob
import pandas as pd
from loguru import logger
from src.managers.configManager import ConfigManager
from src.enums.configPaths import ConfigPaths as CfgPaths
from typing import Protocol


class ConfigYAMLHandler(Protocol):
    def setConfigValue(self, key_path: str, value) -> None: ...

    def getConfigValue(self, key_path: str, default_value=None): ...


class FileManager:
    def __init__(self) -> None:
        self.cfg_mngr: ConfigYAMLHandler = None
        self.file_name: str = "Test"
        self.file_name_suffix: str = ""
        self.file_path: str = os.path.join(os.path.dirname(__file__), "..", "..")

    def setup(self, config_manager: ConfigYAMLHandler):
        self.cfg_mngr = config_manager
        self.file_name = self.cfg_mngr.getConfigValue(
            CfgPaths.TEST_NAME.value, self.file_name
        )
        self.file_path = self.cfg_mngr.getConfigValue(
            CfgPaths.TEST_FOLDER_PATH.value, self.file_path
        )
        if self.getPathExists():
            self.checkFileName()

    def checkFileNameSuffix(self, file_name: str) -> int:
        total_path = os.path.join(self.file_path, file_name + ".*")
        if not glob.glob(total_path):
            return 0
        suffix_num = 1
        suffix_num_max = 100
        while suffix_num < suffix_num_max:
            new_name = f"{file_name}_{suffix_num}"
            total_path = os.path.join(self.file_path, new_name + ".*")
            if not glob.glob(total_path):
                break
            suffix_num += 1
        return suffix_num

    # Setters and getters

    def setFileName(self, name: str) -> None:
        if name == self.file_name:
            self.checkFileName()
            return
        self.file_name = name
        self.checkFileName()
        if self.cfg_mngr is not None:
            self.cfg_mngr.setConfigValue(CfgPaths.TEST_NAME.value, self.file_name)
        logger.info(f"Changed test name to: {self.file_name}")

    def setFilePath(self, path: str):
        self.file_path = path
        if self.cfg_mngr is not None:
            self.cfg_mngr.setConfigValue(
                CfgPaths.TEST_FOLDER_PATH.value, self.file_path
            )
        logger.info(f"Changed test folder path to: {self.file_path}")

    def checkFileName(self, file_name: str = None) -> None:
        if not file_name:
            file_name = self.file_name
        file_suffix_num = 0
        suffix_list = ["", "_RAW"]
        for suffix in suffix_list:
            num = self.checkFileNameSuffix(file_name + suffix)
            if num > file_suffix_num:
                file_suffix_num = num
        if file_suffix_num > 0:
            self.file_name_suffix = f"_{file_suffix_num}"
            logger.warning(
                f"There is already a file named {file_name}. "
                + f"The new file will be {file_name + self.file_name_suffix}"
            )
        if file_suffix_num == 0:
            self.file_name_suffix = ""

    def getFileName(self) -> str:
        return self.file_name + self.file_name_suffix

    def getFilePath(self) -> str:
        return self.file_path

    def getPathExists(self) -> bool:
        return os.path.exists(self.file_path)

    # File saving methods

    def saveDataToCSV(self, df: pd.DataFrame, name_suffix: str = ""):
        if not self.getPathExists():
            logger.warning("The file path does not exist!")
            return
        file_name = self.file_name + self.file_name_suffix + name_suffix
        total_path = os.path.join(self.file_path, file_name + ".csv")
        df.to_csv(total_path, index=False)

        file_size = os.path.getsize(total_path) / (1024 * 1024)
        logger.info(
            f"Test file {file_name} saved in {self.file_path} ({str(round(file_size, 2))} MB)"
        )

    def saveDataToBinary(self, df: pd.DataFrame, name_suffix: str = ""):
        if not self.getPathExists():
            logger.warning("The file path does not exist!")
            return
        file_name = self.file_name + self.file_name_suffix + name_suffix
        total_path = os.path.join(self.file_path, file_name + ".pk1")
        df.to_pickle(total_path)

        file_size = os.path.getsize(total_path) / (1024 * 1024)
        logger.info(
            f"Test file {file_name} saved in {self.file_path} ({str(round(file_size, 2))} MB)"
        )
