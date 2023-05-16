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

    def newCalibrationTest(self, test_value: float):
        self.test_value = test_value
        self.test_sensor_data = np.array([])

    def addTestMeasurement(self, sensor_value: float):
        self.test_sensor_data = np.append(self.test_sensor_data, sensor_value)
        # self.log_handler.logger.debug(str(sensor_value) + "\n" + str(self.test_sensor_data) + "\n SIZE: " + str(self.test_sensor_data.size))

    def getTestResults(self):
        mean = std = -1
        measurements = self.test_sensor_data.size
        self.log_handler.logger.debug(
            "SIZE: " + str(self.test_sensor_data.size))
        if measurements == 0:
            self.log_handler.logger.error(
                "There is no measurements to get results from!!")
            return mean, std, measurements
        mean = np.mean(self.test_sensor_data)
        std = np.std(self.test_sensor_data)
        self.sensor_calibration_dataframe.addRow(
            [self.test_value, mean, std, measurements])
        self.log_handler.logger.debug("==== Test results for load: " + str(self.test_value) + "\nMean: " + str(
            mean) + " STD: " + str(std) + "Number of measurements: " + str(measurements))
        return mean, std, measurements

    def getCalibrationResults(self):
        slope = -1  # Parameter m
        intercept = -1  # Parameter b
        score = -1  # r2
        if self.sensor_calibration_dataframe.getDataFrame().empty:
            self.log_handler.logger.warn("Calibration data is empty!")
            return slope, intercept, score

        # Linear regression
        features = self.sensor_calibration_dataframe.getDataFrame()[
            'mean'].values
        targets = self.sensor_calibration_dataframe.getDataFrame()[
            'test_value'].values
        model = LinearRegression().fit(features, targets)

        slope = model.coef_[0]
        intercept = model.intercept_
        score = model.score(features, targets)

        # TODO plot results??
        self.log_handler.logger.debug("===== CALIBRATION RESULTS \nSlope: " + str(
            slope) + " Intercept: " + str(intercept) + "r2: " + str(score))
        return slope, intercept, score
