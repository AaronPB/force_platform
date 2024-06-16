# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from scipy.linalg import lstsq

from src.managers.sensorManager import SensorManager
from src.managers.fileManager import FileManager
from src.enums.sensorStatus import SStatus
from src.handlers import SensorGroup, Sensor

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


class PlatformCalibrationManager:
    def __init__(self) -> None:
        # Sensors
        self.platform_group: SensorGroup
        self.ref_sensor: list[Sensor]
        # Calib params
        self.record_interval_ms: int
        self.record_amount: int
        # Calib measurements
        self.measurement_ready: bool = False
        self.use_ref_sensor: bool = False
        self.ref_value: float
        self.df_distance_cols = ["l_x", "l_y", "l_z"]
        self.df_triaxial_cols = ["V_fx", "V_fy", "V_fy"]
        self.df_platform_cols = [
            "V_f1",
            "V_f2",
            "V_f3",
            "V_f4",
            "V_f5",
            "V_f6",
            "V_f7",
            "V_f8",
            "V_f9",
            "V_f10",
            "V_f11",
            "V_f12",
        ]
        # - Measurement dataframes with mean values of sensors
        self.measurement_distances_df = pd.DataFrame(columns=self.df_distance_cols)
        df_triaxial_cols_mean = [col + "_mean" for col in self.df_triaxial_cols]
        df_platform_cols_mean = [col + "_mean" for col in self.df_platform_cols]
        self.measurement_mean_df = pd.DataFrame(
            columns=df_triaxial_cols_mean + df_platform_cols_mean
        )
        df_triaxial_cols_std = [col + "_std" for col in self.df_triaxial_cols]
        df_platform_cols_std = [col + "_std" for col in self.df_platform_cols]
        self.measurement_std_df = pd.DataFrame(
            columns=df_triaxial_cols_std + df_platform_cols_std
        )
        # Calib results
        self.calibration_matrix = None
        self.std_dev_matrix = None
        # File manager
        self.file_mngr: FileManager

    def setup(
        self,
        platform_group: SensorGroup,
        ref_sensor: list[Sensor],
        record_interval_ms: int = 10,
        record_amount: int = 300,
    ) -> None:
        self.platform_group = platform_group
        self.ref_sensor = ref_sensor
        # TODO Meaning of this checks?
        self.platform_group.checkConnections()
        for sensor in self.ref_sensor:
            sensor.checkConnection()
        self.record_interval_ms = record_interval_ms
        self.record_amount = record_amount
        self.setupFileManager()

    # Prepare FileManager
    def setupFileManager(self):
        self.file_mngr = FileManager()
        formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"platform_calibs/calibration_{self.platform_group.getName()}_{formatted_date}"
        folder_path = os.path.join(self.file_mngr.getFilePath(), folder_name)
        # Crear la carpeta
        try:
            os.makedirs(folder_path, exist_ok=True)
            logger.info(f"New calibration folder created in {folder_path}")
        except Exception as e:
            logger.error(
                f"Could not create folder with name {folder_name} in {self.file_mngr.getFilePath()}"
            )
        self.file_mngr.setFilePath(folder_path)

    # Calibration measurements

    def startMeasurement(self, distances: list[int]) -> None:
        self.platform_group.clearValues()
        [sensor.clearValues() for sensor in self.ref_sensor]
        self.platform_group.start()
        [sensor.connect() for sensor in self.ref_sensor]
        self.measurement_ready = True
        self.measurement_distances_df.loc[len(self.measurement_distances_df)] = (
            distances
        )

    def registerValue(self) -> None:
        if not self.measurement_ready:
            return
        self.platform_group.register()
        [sensor.registerValue() for sensor in self.ref_sensor]

    def stopMeasurement(self) -> None:
        if not self.measurement_ready:
            return
        self.platform_group.stop()
        [sensor.disconnect() for sensor in self.ref_sensor]
        self.saveMeasurement()

    # Data management

    def saveMeasurement(self) -> None:
        df_raw: pd.DataFrame = pd.DataFrame()
        new_measurement_means = []
        new_measurement_stds = []
        for sensor in self.ref_sensor:
            new_measurement_means.append(np.mean(sensor.getValues()))
            new_measurement_stds.append(np.std(sensor.getValues()))
            df_raw[sensor.getName()] = sensor.getValues()
        for sensor in self.platform_group.getSensors().values():
            new_measurement_means.append(np.mean(sensor.getValues()))
            new_measurement_stds.append(np.std(sensor.getValues()))
            df_raw[sensor.getName()] = sensor.getValues()
        # Save means and stds data into dataframes, moving z axis data to end of list.
        self.measurement_mean_df.loc[len(self.measurement_mean_df)] = (
            new_measurement_means[:3]
            + new_measurement_means[7:]
            + new_measurement_means[3:7]
        )
        self.measurement_std_df.loc[len(self.measurement_std_df)] = (
            new_measurement_stds[:3]
            + new_measurement_stds[7:]
            + new_measurement_stds[3:7]
        )
        # Save raw data in calibration folder
        file_name = "-".join(
            self.measurement_distances_df.iloc[-1].astype(str).tolist()
        )
        self.file_mngr.setFileName(file_name)
        self.file_mngr.saveDataToCSV(df_raw)

    def removeMeasurement(self, index: int) -> None:
        self.measurement_distances_df.drop(index=index, inplace=True)
        self.measurement_mean_df.drop(index=index, inplace=True)
        self.measurement_std_df.drop(index=index, inplace=True)

    def saveResults(self, sensor_manager: SensorManager) -> None:
        # sensor_manager.setSensorSlope(self.sensor, self.sensor_slope)
        # sensor_manager.setSensorIntercept(self.sensor, self.sensor_intercept)
        # logger.info(
        #     f"Saved sensor {self.sensor.getName()} "
        #     + f"slope: {self.sensor.getSlope():.4f}; intercept: {self.sensor.getIntercept():.4f}"
        # )
        pass

    def clearValues(self) -> None:
        self.measurement_distances_df.drop(
            self.measurement_distances_df.index, inplace=True
        )
        self.measurement_mean_df.drop(self.measurement_mean_df.index, inplace=True)
        self.measurement_std_df.drop(self.measurement_std_df.index, inplace=True)

    # Setters and getters

    def refSensorConnected(self) -> bool:
        if not self.ref_sensor:
            return False
        return all(
            [sensor.getStatus() == SStatus.AVAILABLE for sensor in self.ref_sensor]
        )

    def getRecordInterval(self) -> int:
        return self.record_interval_ms

    def getRecordDuration(self) -> int:
        return int(self.record_interval_ms * self.record_amount)

    def getLastValues(self) -> list:
        # TODO
        # return self.measurements_df.iloc[-1].tolist()
        pass

    def getResults(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        force_ratio_x = self.ref_sensor[0].getSlope()
        force_ratio_y = self.ref_sensor[1].getSlope()
        force_ratio_z = self.ref_sensor[2].getSlope()
        mean_values = self.measurement_mean_df
        distance_values = self.measurement_distances_df

        M = len(mean_values)
        Zf = []
        f = []
        for i in range(M):
            # Process data for M measurement
            # Applied force in triaxial sensor
            fpM = np.array(
                [
                    mean_values.at[i, self.df_triaxial_cols[1]] * force_ratio_y,
                    mean_values.at[i, self.df_triaxial_cols[0]] * force_ratio_x,
                    mean_values.at[i, self.df_triaxial_cols[2]] * force_ratio_z,
                ]
            )
            # Transform force to platform center (fM)
            delta_x = distance_values.at[i, self.df_distance_cols[0]]
            delta_y = distance_values.at[i, self.df_distance_cols[1]]
            delta_z = distance_values.at[i, self.df_distance_cols[2]]
            delta = np.array(
                [[0, -delta_z, delta_y], [delta_z, 0, -delta_x], [-delta_y, delta_x, 0]]
            )
            fM = np.dot(np.vstack([np.eye(3), delta]), fpM)
            # Define platform sensor values matrix
            vfM = np.array([mean_values.at[i, col] for col in self.df_platform_cols])
            # Build A matrix
            ZfM = np.kron(np.eye(6), vfM.T)
            # Concatenate M matrixes into general matrixes.
            Zf.append(ZfM)
            f.append(fM)
        # Apply least squares
        Zf = np.vstack(Zf)
        f = np.hstack(f).reshape(-1, 1)
        x, residuals, rank, s = lstsq(Zf, f)
        # Reshape calibration and deviation matrixes
        C = x.reshape(12, 6).T
        covariance_matrix = 25 * np.linalg.inv(np.dot(Zf.T, Zf))
        std_devs = np.sqrt(np.diag(covariance_matrix))
        # Save matrixes in dataframes
        self.calibration_matrix = pd.DataFrame(C)
        self.std_dev_matrix = pd.DataFrame(std_devs)
        return (self.calibration_matrix, self.std_dev_matrix)
