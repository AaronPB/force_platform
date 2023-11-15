# -*- coding: utf-8 -*-

import numpy as np
from sklearn.linear_model import LinearRegression

from src.managers.configManager import ConfigManager
from src.sensorLoader import SensorLoader
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorStatus import SensorStatus as SStatus

from loguru import logger


class CalibrationManager:
    def __init__(self, config_mngr: ConfigManager, sensor_loader: SensorLoader) -> None:
        # Global values
        self.config_mngr = config_mngr
        self.sensor_loader = sensor_loader
        self.sensors_connected = False
        self.sensor_values = []
        self.test_values = []
        self.calib_results = []
        self.calib_sensor = None
        self.group_platform1 = sensor_loader.getSensorGroupPlatform1()
        self.group_platform2 = sensor_loader.getSensorGroupPlatform2()
        self.reference_sensor = sensor_loader.getRefSensor()

    def checkConnection(self) -> bool:
        connection_results_list = [
            handler.checkConnections()
            for handler in [self.group_platform1, self.group_platform2]
        ]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    def checkRefSensorConnection(self):
        if self.reference_sensor is None:
            return False
        return self.reference_sensor.checkConnection()

    # Setters and getters

    def calibrateP1Sensor(self, index: int) -> list:
        sensor_list = list(self.group_platform1.sensors.values())
        self.calib_sensor = sensor_list[index]
        return [self.calib_sensor.getName(), self.calib_sensor.getProperties()]

    def calibrateP2Sensor(self, index: int) -> None:
        sensor_list = list(self.group_platform2.sensors.values())
        self.calib_sensor = sensor_list[index]
        return [self.calib_sensor.getName(), self.calib_sensor.getProperties()]

    def getP1SensorStatus(self) -> dict:
        return self.group_platform1.getGroupInfo()

    def getP2SensorStatus(self) -> dict:
        return self.group_platform2.getGroupInfo()

    def getCalibDuration(self) -> int:
        return self.config_mngr.getConfigValue(
            CfgPaths.GENERAL_CALIBRATION_DURATION_MS.value, 3000
        )

    def getCalibTestInterval(self) -> int:
        return self.config_mngr.getConfigValue(
            CfgPaths.GENERAL_CALIBRATION_INTERVAL_MS.value, 10
        )

    def refSensorConnected(self) -> bool:
        if self.reference_sensor is None:
            return False
        return self.reference_sensor.getStatus() == SStatus.AVAILABLE

    # Calibration functions

    def startRecording(self, auto: bool = False):
        self.add_ref_sensor = False
        if auto and not self.refSensorConnected():
            return
        if auto:
            self.reference_sensor.clearValues()
            self.reference_sensor.connect()
            self.add_ref_sensor = True
        self.calib_sensor.clearValues()
        self.calib_sensor.connect()

    def registerValue(self):
        self.calib_sensor.registerValue()
        if self.add_ref_sensor:
            self.reference_sensor.registerValue()

    def stopRecording(self):
        self.calib_sensor.disconnect()
        if self.add_ref_sensor:
            self.reference_sensor.disconnect()

    def getValues(self, test_value: float = None) -> list:
        if test_value is None and not self.add_ref_sensor:
            return [-1, -1, -1, -1]
        if self.add_ref_sensor:
            ref_values = np.array(self.reference_sensor.getCalibValues())
            test_value = np.mean(ref_values)
        values = np.array(self.calib_sensor.getValues())
        values_mean = np.mean(values)
        self.sensor_values.append(values_mean)
        self.test_values.append(test_value)
        return [test_value, values_mean, np.std(values), len(values)]

    def clearAllValues(self):
        self.sensor_values.clear()
        self.test_values.clear()
        self.calib_results.clear()

    def removeValueSet(self, index: int):
        self.sensor_values.pop(index)
        self.test_values.pop(index)

    def getRegressionResults(self) -> list:
        features = np.array(self.sensor_values).reshape(-1, 1)
        targets = np.array(self.test_values).reshape(-1, 1)
        model = LinearRegression().fit(features, targets)
        self.calib_results.clear()
        self.calib_results.append(np.array(model.coef_[0]).item())
        self.calib_results.append(model.intercept_.item())
        self.calib_results.append(model.score(features, targets))
        return self.calib_results

    def getValuesArrays(self):
        return np.array(self.sensor_values), np.array(self.test_values)

    def getRegressionArrays(self):
        sensor_values = np.array(self.sensor_values)
        test_values = sensor_values * self.calib_results[0] + self.calib_results[1]
        return sensor_values, test_values
