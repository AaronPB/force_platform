# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.managers.sensorManager import SensorManager
from src.enums.sensorStatus import SStatus
from src.handlers.sensor import Sensor

from loguru import logger


class SensorCalibrationManager:
    def __init__(self) -> None:
        # Sensors
        self.sensor: Sensor
        self.ref_sensor: Sensor
        # Calib params
        self.record_interval_ms: int
        self.record_amount: int
        # Calib measurements
        self.measurement_ready: bool = False
        self.use_ref_sensor: bool = False
        self.ref_value: float
        df_cols = ["ref_value", "sensor_mean", "sensor_std", "data_amount"]
        self.measurements_df = pd.DataFrame(columns=df_cols)
        # Calib results
        self.sensor_slope: float = 1
        self.sensor_intercept: float = 0
        self.calib_score: float = 1

    def setup(
        self,
        sensor: Sensor,
        ref_sensor: Sensor | None = None,
        record_interval_ms: int = 10,
        record_amount: int = 300,
    ) -> None:
        self.sensor = sensor
        self.ref_sensor = ref_sensor
        self.checkConnection(self.sensor)
        self.checkConnection(self.ref_sensor)
        self.record_interval_ms = record_interval_ms
        self.record_amount = record_amount

    def checkConnection(self, sensor: Sensor) -> bool:
        if sensor is None:
            return False
        return sensor.checkConnection()

    # Calibration measurements

    def startMeasurement(
        self, use_ref_sensor: bool = False, ref_value: float = None
    ) -> None:
        self.measurement_ready = False
        self.use_ref_sensor = False
        self.ref_value = ref_value
        if use_ref_sensor and not self.ref_sensor:
            logger.warning("There is no reference sensor connected!")
            return
        if not use_ref_sensor and not ref_value:
            logger.warning("No value provided! Measurement ignored")
            return
        if use_ref_sensor and self.ref_sensor.getStatus() == SStatus.AVAILABLE:
            self.ref_sensor.clearValues()
            self.ref_sensor.connect()
            self.use_ref_sensor = True
        self.sensor.clearValues()
        self.sensor.connect()
        self.measurement_ready = True

    def registerValue(self) -> None:
        if not self.measurement_ready:
            return
        if self.use_ref_sensor:
            self.ref_sensor.registerValue()
        self.sensor.registerValue()

    def stopMeasurement(self) -> None:
        if not self.measurement_ready:
            return
        if self.use_ref_sensor:
            self.ref_sensor.disconnect()
        self.sensor.disconnect()
        self.saveMeasurement()

    # Data management

    def getCalibratedValues(self, sensor: Sensor) -> list[float]:
        slope = sensor.getSlope()
        intercept = sensor.getIntercept()
        return [value * slope + intercept for value in sensor.getValues()]

    def saveMeasurement(self) -> None:
        if self.use_ref_sensor:
            ref_values = self.getCalibratedValues(self.ref_sensor)
            self.ref_value = np.mean(ref_values)
        if not self.ref_value:
            return
        sensor_values = self.sensor.getValues()
        sensor_mean = np.mean(sensor_values)
        sensor_std = np.std(sensor_values)
        new_measurement = [self.ref_value, sensor_mean, sensor_std, len(sensor_values)]
        self.measurements_df.loc[len(self.measurements_df)] = new_measurement

    def removeMeasurement(self, index: int) -> None:
        self.measurements_df.drop(index=index, inplace=True)

    def saveResults(self, sensor_manager: SensorManager) -> None:
        sensor_manager.setSensorSlope(self.sensor, self.sensor_slope)
        sensor_manager.setSensorIntercept(self.sensor, self.sensor_intercept)
        logger.info(
            f"Saved sensor {self.sensor.getName()} "
            + f"slope: {self.sensor.getSlope():.4f}; intercept: {self.sensor.getIntercept():.4f}"
        )

    def clearValues(self) -> None:
        self.measurements_df.drop(self.measurements_df.index, inplace=True)
        self.sensor_slope: float = 1
        self.sensor_intercept: float = 0
        self.calib_score: float = 1

    # Setters and getters

    def refSensorConnected(self) -> bool:
        if not self.ref_sensor:
            return False
        return self.ref_sensor.getStatus() == SStatus.AVAILABLE

    def getRecordInterval(self) -> int:
        return self.record_interval_ms

    def getRecordDuration(self) -> int:
        return int(self.record_interval_ms * self.record_amount)

    def getLastValues(self) -> list:
        return self.measurements_df.iloc[-1].tolist()

    def getResults(self) -> list[float]:
        features = self.measurements_df["sensor_mean"].to_numpy().reshape(-1, 1)
        targets = self.measurements_df["ref_value"].to_numpy().reshape(-1, 1)
        model = LinearRegression().fit(features, targets)
        self.sensor_slope = float(model.coef_[0])
        self.sensor_intercept = float(model.intercept_)
        self.calib_score = model.score(features, targets)
        return [self.sensor_slope, self.sensor_intercept, self.calib_score]

    # Plot data arrays

    def getValuesArrays(self):
        return (
            self.measurements_df["sensor_mean"].to_numpy(),
            self.measurements_df["ref_value"].to_numpy(),
        )

    def getRegressionArrays(self):
        return (
            self.measurements_df["sensor_mean"].to_numpy(),
            (
                self.measurements_df["sensor_mean"] * self.sensor_slope
                + self.sensor_intercept
            ).to_numpy(),
        )
