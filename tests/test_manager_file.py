# -*- coding: utf-8 -*-

import pytest
import os
import glob
import pandas as pd
from src.managers.fileManager import FileManager
from pytest import MonkeyPatch


# General mocks, builders and fixtures


class ConfigManagerMock:
    def __init__(self) -> None:
        pass

    def setConfigValue(self, config_path: str, value) -> None:
        pass

    def getConfigValue(self, config_path: str, default_value):
        return default_value


@pytest.fixture
def file_manager() -> FileManager:
    file_manager = FileManager()
    file_manager.setup(config_manager=ConfigManagerMock())
    file_manager.file_path = os.path.dirname(__file__)
    return file_manager


@pytest.fixture
def dataframe() -> pd.DataFrame:
    example_data = {
        "timestamp": ["1111111", "1111112", "1111113"],
        "LoadCell_1": [1.23948, 1.239894, 1.458289],
    }
    return pd.DataFrame(example_data)


# Tests


def test_check_file_suffix(monkeypatch: MonkeyPatch, file_manager: FileManager) -> None:
    glob_patterns = {
        os.path.join(file_manager.file_path, "Test.*"): [
            "Test.csv",
            "Test_RAW.csv",
        ],
        os.path.join(file_manager.file_path, "Test_1.*"): [
            "Test_1.csv",
            "Test_RAW_1.csv",
        ],
        os.path.join(file_manager.file_path, "Test_2.*"): [
            "Test_2.csv",
            "Test_RAW_2.csv",
        ],
        os.path.join(file_manager.file_path, "Test_3.*"): [],
    }

    def mock_glob(pattern):
        return glob_patterns.get(pattern, [])

    monkeypatch.setattr(glob, "glob", mock_glob)
    file_manager.checkFileName("Test")
    assert file_manager.getFileName() == "Test_3"


def test_check_file_suffix_different_forms(
    monkeypatch: MonkeyPatch, file_manager: FileManager
) -> None:
    glob_patterns = {
        os.path.join(file_manager.file_path, "Test.*"): ["Test.csv", "Test_RAW.csv"],
        os.path.join(file_manager.file_path, "Test_1.*"): ["Test_RAW_1.csv"],
        os.path.join(file_manager.file_path, "Test_2.*"): ["Test_2.pk1"],
        os.path.join(file_manager.file_path, "Test_3.*"): ["Test_3.txt"],
        os.path.join(file_manager.file_path, "Test_4.*"): [],
    }

    def mock_glob(pattern):
        return glob_patterns.get(pattern, [])

    monkeypatch.setattr(glob, "glob", mock_glob)
    file_manager.checkFileName("Test")
    assert file_manager.getFileName() == "Test_4"


def test_file_name_setter(file_manager: FileManager) -> None:
    new_name = "New test"
    file_manager.setFileName(new_name)
    assert file_manager.getFileName() == new_name


def test_file_name_setter_equal(file_manager: FileManager) -> None:
    new_name = "Test"
    file_manager.setFileName(new_name)
    assert file_manager.getFileName() == new_name


def test_filepath_name_setter(file_manager: FileManager) -> None:
    test_path = "/test/path"
    file_manager.setFilePath(test_path)
    assert file_manager.getFilePath() == test_path


def test_file_name_check(file_manager: FileManager) -> None:
    file_manager.checkFileName()
    assert file_manager.getFileName() == "Test"


def test_file_name_getter(file_manager: FileManager) -> None:
    assert file_manager.getFileName() == "Test"


def test_file_path_getter(file_manager: FileManager) -> None:
    assert os.path.samefile(file_manager.getFilePath(), os.path.dirname(__file__))


def test_file_path_exists(file_manager: FileManager) -> None:
    assert file_manager.getPathExists()


def test_file_path_not_exists(file_manager: FileManager) -> None:
    file_manager.setFilePath("/test/non/existing/path")
    assert not file_manager.getPathExists()


def test_file_save_csv_dataframe(
    file_manager: FileManager, dataframe: pd.DataFrame
) -> None:
    file_manager.saveDataToCSV(df=dataframe)
    total_path = os.path.join(
        file_manager.getFilePath(), file_manager.getFileName() + ".csv"
    )
    file_exists = os.path.exists(total_path)
    if file_exists:
        os.remove(total_path)
    assert file_exists


def test_file_save_failure_csv_dataframe(
    file_manager: FileManager, dataframe: pd.DataFrame
) -> None:
    file_manager.setFilePath("/test/non/existing/path")
    file_manager.saveDataToCSV(df=dataframe)
    total_path = os.path.join(
        file_manager.getFilePath(), file_manager.getFileName() + ".csv"
    )
    file_exists = os.path.exists(total_path)
    assert not file_exists


def test_file_save_binary_dataframe(
    file_manager: FileManager, dataframe: pd.DataFrame
) -> None:
    file_manager.saveDataToBinary(df=dataframe)
    total_path = os.path.join(
        file_manager.getFilePath(), file_manager.getFileName() + ".pk1"
    )
    file_exists = os.path.exists(total_path)
    if file_exists:
        os.remove(total_path)
    assert file_exists


def test_file_save_failure_binary_dataframe(
    file_manager: FileManager, dataframe: pd.DataFrame
) -> None:
    file_manager.setFilePath("/test/non/existing/path")
    file_manager.saveDataToBinary(df=dataframe)
    total_path = os.path.join(
        file_manager.getFilePath(), file_manager.getFileName() + ".pk1"
    )
    file_exists = os.path.exists(total_path)
    assert not file_exists
