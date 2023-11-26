# -*- coding: utf-8 -*-

import pytest
import os
import pandas as pd
from src.managers.testFileManager import TestFileManager
from pytest import MonkeyPatch


# General mocks, builders and fixtures


class ConfigManagerMock:
    def __init__(self) -> None:
        self.set_cfg_value_calls = 0

    def setConfigValue(self, config_path: str, value) -> None:
        self.set_cfg_value_calls += 1

    def getConfigValue(self, config_path: str, default_value=None):
        if default_value is None:
            return "value"
        return default_value


@pytest.fixture
def test_manager() -> TestFileManager:
    test_mngr = TestFileManager(cfg_mngr=ConfigManagerMock())
    test_mngr.file_path = os.path.dirname(__file__)
    return test_mngr


@pytest.fixture
def dataframe() -> pd.DataFrame:
    example_data = {
        "timestamp": ["1111111", "1111112", "1111113"],
        "LoadCell_1": [1.23948, 1.239894, 1.458289],
    }
    return pd.DataFrame(example_data)


# Tests


def test_check_no_duplicated_file(test_manager: TestFileManager) -> None:
    new_name = "New test"
    test_name = test_manager.checkDuplicatedName(new_name)
    assert test_name == new_name


def test_check_duplicated_file(
    monkeypatch: MonkeyPatch, test_manager: TestFileManager
) -> None:
    os_exists_mock = [True]

    def mock_exists(path):
        os_exists_status = os_exists_mock[0]
        os_exists_mock[0] = False
        return os_exists_status

    monkeypatch.setattr(os.path, "exists", mock_exists)
    result = test_manager.checkDuplicatedName("Test")
    assert result == "Test_1"


def test_file_name_setter(test_manager: TestFileManager) -> None:
    new_name = "New test"
    test_manager.setFileName(new_name)
    config_manager: ConfigManagerMock = test_manager.cfg_mngr
    assert config_manager.set_cfg_value_calls == 1


def test_file_name_setter_equal(test_manager: TestFileManager) -> None:
    new_name = "Test"
    test_manager.setFileName(new_name)
    config_manager: ConfigManagerMock = test_manager.cfg_mngr
    assert config_manager.set_cfg_value_calls == 0


def test_filepath_name_setter(test_manager: TestFileManager) -> None:
    test_manager.setFilePath("/test/path")
    config_manager: ConfigManagerMock = test_manager.cfg_mngr
    assert config_manager.set_cfg_value_calls == 1


def test_file_name_getter(test_manager: TestFileManager) -> None:
    assert test_manager.getFileName() == "Test"


def test_file_path_getter(test_manager: TestFileManager) -> None:
    assert os.path.samefile(test_manager.getFilePath(), os.path.dirname(__file__))


def test_file_path_exists(test_manager: TestFileManager) -> None:
    assert test_manager.getPathExists()


def test_file_path_not_exists(test_manager: TestFileManager) -> None:
    test_manager.setFilePath("/test/non/existing/path", check_name=False)
    assert not test_manager.getPathExists()


def test_file_save_csv_dataframe(
    test_manager: TestFileManager, dataframe: pd.DataFrame
) -> None:
    test_manager.saveDataToCSV(df=dataframe)
    total_path = os.path.join(
        test_manager.getFilePath(), test_manager.getFileName() + ".csv"
    )
    file_exists = os.path.exists(total_path)
    if file_exists:
        os.remove(total_path)
    assert file_exists


def test_file_save_failure_csv_dataframe(
    test_manager: TestFileManager, dataframe: pd.DataFrame
) -> None:
    test_manager.setFilePath("/test/non/existing/path", check_name=False)
    test_manager.saveDataToCSV(df=dataframe)
    total_path = os.path.join(
        test_manager.getFilePath(), test_manager.getFileName() + ".csv"
    )
    file_exists = os.path.exists(total_path)
    if file_exists:
        os.remove(total_path)
    assert not file_exists


def test_file_save_binary_dataframe(
    test_manager: TestFileManager, dataframe: pd.DataFrame
) -> None:
    test_manager.saveDataToBinary(df=dataframe)
    total_path = os.path.join(
        test_manager.getFilePath(), test_manager.getFileName() + ".pk1"
    )
    file_exists = os.path.exists(total_path)
    if file_exists:
        os.remove(total_path)
    assert file_exists


def test_file_save_failure_binary_dataframe(
    test_manager: TestFileManager, dataframe: pd.DataFrame
) -> None:
    test_manager.setFilePath("/test/non/existing/path", check_name=False)
    test_manager.saveDataToBinary(df=dataframe)
    total_path = os.path.join(
        test_manager.getFilePath(), test_manager.getFileName() + ".pk1"
    )
    file_exists = os.path.exists(total_path)
    if file_exists:
        os.remove(total_path)
    assert not file_exists
