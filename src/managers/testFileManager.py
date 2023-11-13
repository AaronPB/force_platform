import os
import pandas as pd
from loguru import logger
from src.managers.configManager import ConfigManager
from src.enums.configPaths import ConfigPaths as CfgPaths


class TestFileManager:
    def __init__(self, cfg_mngr: ConfigManager) -> None:
        self.cfg_mngr = cfg_mngr
        self.file_name = self.cfg_mngr.getConfigValue(
            CfgPaths.GENERAL_TEST_NAME.value, "Test"
        )
        self.file_path = self.cfg_mngr.getConfigValue(
            CfgPaths.GENERAL_TEST_FOLDER.value, ""
        )

    def checkDuplicatedName(self, name: str) -> str:
        total_path = os.path.join(self.file_path, name + ".csv")
        if not os.path.exists(total_path):
            return name
        suffix_num = 1
        while True:
            new_name = (
                f"{os.path.splitext(name)[0]}_{suffix_num}{os.path.splitext(name)[1]}"
            )
            total_path = os.path.join(self.file_path, new_name + ".csv")
            if not os.path.exists(total_path):
                logger.warning(
                    f"There is already a file named {name}. The new file will be {new_name}"
                )
                break
            suffix_num += 1
        return new_name

    # Setters and getters

    def setFileName(self, name: str) -> None:
        name = self.checkDuplicatedName(name)
        if name == self.file_name:
            return
        self.file_name = name
        self.cfg_mngr.setConfigValue(CfgPaths.GENERAL_TEST_NAME.value, self.file_name)
        logger.info(f"Changed test name to: {self.file_name}")

    def setFilePath(self, path: str, check_name: bool = True):
        self.file_path = path
        self.cfg_mngr.setConfigValue(CfgPaths.GENERAL_TEST_FOLDER.value, self.file_path)
        logger.info(f"Changed test folder path to: {self.file_path}")
        if check_name:
            self.setFileName(self.file_name)

    def checkFileName(self) -> None:
        self.setFileName(self.file_name)

    def getFileName(self) -> str:
        return self.file_name

    def getFilePath(self) -> str:
        return self.file_path

    def getPathExists(self) -> bool:
        return os.path.exists(self.file_path)

    # File saving methods

    def saveDataToCSV(self, df: pd.DataFrame, name_suffix: str = ""):
        if not self.getPathExists():
            logger.warning("The file path does not exist!")
            return
        file_name = self.file_name + name_suffix
        total_path = os.path.join(self.file_path, file_name + ".csv")
        df.to_csv(total_path, index=False)

        file_size = os.path.getsize(total_path) / (1024 * 1024)
        logger.info(
            f"Test file saved in {self.file_path} ({str(round(file_size, 2))} MB)"
        )

    def saveDataToBinary(self, df: pd.DataFrame):
        if not self.getPathExists():
            logger.warning("The file path does not exist!")
            return
        total_path = os.path.join(self.file_path, self.file_name + ".pk1")
        df.to_pickle(total_path, index=False)

        file_size = os.path.getsize(total_path) / (1024 * 1024)
        logger.info(
            f"Test file saved in {self.file_path} ({str(round(file_size, 2))} MB)"
        )
