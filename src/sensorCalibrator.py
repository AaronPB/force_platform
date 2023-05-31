# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 16/05/2023
"""

import numpy as np

from sklearn.linear_model import LinearRegression
from src.utils import LogHandler, TestDataFrame


class SensorCalibrator:
    def __init__(self):
        self.log_handler = LogHandler(str(__class__.__name__))
        self.initialize()

    def initialize(self):
        self.sensor_calibration_dataframe = TestDataFrame(
            ['test_value', 'mean', 'std', 'measurements'])

    def newCalibrationTest(self, test_value: float = None):
        self.test_value = test_value
        self.test_sensor_data = np.array([])
        self.test_reference_sensor_data = np.array([])

    def addTestMeasurement(self, sensor_value: float, reference_sensor_value: float = None):
        self.test_sensor_data = np.append(self.test_sensor_data, sensor_value)
        if self.test_value is None and reference_sensor_value is not None:
            self.test_reference_sensor_data = np.append(
                self.test_reference_sensor_data, reference_sensor_value)
        # self.log_handler.logger.debug(str(sensor_value) + "\n" + str(self.test_sensor_data) + "\n SIZE: " + str(self.test_sensor_data.size))

    def getTestResults(self):
        value = mean = std = sensor_measurements = None
        # Check first if reference sensor values has been recorded
        reference_sensor_measurements = self.test_reference_sensor_data.size
        if self.test_value is None and reference_sensor_measurements == 0:
            self.log_handler.logger.error(
                "There is no reference measurements to get results from!!")
            return value, mean, std, sensor_measurements
        value = self.test_value
        if value is None:
            value = np.mean(self.test_reference_sensor_data)
        # Check then sensor test measurements
        sensor_measurements = self.test_sensor_data.size
        self.log_handler.logger.debug(
            "SIZE: " + str(self.test_sensor_data.size))
        if sensor_measurements == 0:
            self.log_handler.logger.error(
                "There is no measurements to get results from!!")
            return value, mean, std, sensor_measurements
        # Get all test results
        mean = np.mean(self.test_sensor_data)
        std = np.std(self.test_sensor_data)
        self.sensor_calibration_dataframe.addRow(
            [value, mean, std, sensor_measurements])
        self.log_handler.logger.debug("==== Test results for test value: " + str(value) + "\nMean: " + str(
            mean) + " STD: " + str(std) + " Number of measurements: " + str(sensor_measurements))
        return value, mean, std, sensor_measurements

    def getCalibrationResults(self):
        slope = -1  # Parameter m
        intercept = -1  # Parameter b
        score = -1  # r2
        if self.sensor_calibration_dataframe.getDataFrame().empty:
            self.log_handler.logger.warn("Calibration data is empty!")
            return slope, intercept, score, -1, -1

        # Linear regression
        features = self.sensor_calibration_dataframe.getDataFrame()[
            'mean'].values.reshape(-1, 1)
        targets = self.sensor_calibration_dataframe.getDataFrame()[
            'test_value'].values.reshape(-1, 1)
        model = LinearRegression().fit(features, targets)

        slope = np.array(model.coef_[0])
        intercept = model.intercept_
        score = model.score(features, targets)

        self.log_handler.logger.debug("===== CALIBRATION RESULTS \nSlope: " + str(
            slope) + " Intercept: " + str(intercept) + "r2: " + str(score))
        return slope.item(), intercept.item(), score, features, targets
