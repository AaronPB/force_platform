# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation
from scipy.signal import butter, filtfilt
from src.qtUIs.widgets.matplotlibWidgets import (
    PlotFigureWidget,
    PlotPlatformForcesWidget,
    PlotPlatformCOPWidget,
)
from src.managers.sensorManager import SensorManager
from src.handlers import SensorGroup, Sensor
from src.enums.plotTypes import PlotTypes
from src.enums.sensorTypes import SGTypes, STypes
from src.enums.sensorStatus import SGStatus

from loguru import logger


class DataManager:
    def __init__(self):
        # Time
        self.timestamp_list: list = []
        self.timeincr_list: list = []
        # Data
        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df_calibrated: pd.DataFrame = pd.DataFrame()
        self.df_filtered: pd.DataFrame = pd.DataFrame()
        # Sensor header suffixes
        self.imu_ang_headers: list[str] = ["qx", "qy", "qz", "qw"]
        self.imu_vel_headers: list[str] = ["wx", "wy", "wz"]
        self.imu_acc_headers: list[str] = ["x_acc", "y_acc", "z_acc"]
        # WIP Platform loadcell sensors orientation
        self.forces_sign: dict[str, int] = {
            "X_1": 1,
            "X_2": -1,
            "X_3": -1,
            "X_4": 1,
            "Y_1": 1,
            "Y_2": 1,
            "Y_3": -1,
            "Y_4": -1,
            "Z_1": 1,
            "Z_2": 1,
            "Z_3": 1,
            "Z_4": 1,
        }

    def clearDataFrames(self) -> None:
        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df_calibrated: pd.DataFrame = pd.DataFrame()
        self.df_filtered: pd.DataFrame = pd.DataFrame()

    # Data load methods

    def loadData(self, time_list: list, sensor_groups: list[SensorGroup]) -> None:
        self.clearDataFrames()
        self.timestamp_list = time_list
        self.timeincr_list = [(t - time_list[0]) / 1000 for t in time_list]
        for group in sensor_groups:
            if not group.getRead():
                continue
            if group.getStatus() == SGStatus.ERROR:
                continue
            for sensor in group.getAvailableSensors().values():
                if sensor.getType() == STypes.SENSOR_IMU:
                    values_list = self.getListedData(sensor)
                    for i, suffix in enumerate(
                        self.imu_ang_headers
                        + self.imu_vel_headers
                        + self.imu_acc_headers
                    ):
                        imu_name = sensor.getName() + "_" + suffix
                        self.df_raw[imu_name] = values_list[i]
                        # No need to calibrate IMUs
                        self.df_calibrated[imu_name] = values_list[i]
                    continue
                self.df_raw[sensor.getName()] = sensor.getValues()
                slope = sensor.getSlope()
                intercept = sensor.getIntercept()
                self.df_calibrated[sensor.getName()] = [
                    value * slope + intercept for value in sensor.getValues()
                ]

    # Transforms values lists into separate variable lists.
    # Ex: [ti [gx, gy, gz]] -> [gx[ti], gy[ti], gz[ti]]
    def getListedData(self, sensor: Sensor) -> list[list[float]]:
        main_list = sensor.getValues()
        new_main_list: list[list[float]] = [[] for _ in range(len(main_list[0]))]
        for value_list in main_list:
            for i, value in enumerate(value_list):
                new_main_list[i].append(value)
        return new_main_list

    def isRangedPlot(self, idx1: int, idx2: int) -> bool:
        if idx1 != 0 or idx2 != 0:
            if idx2 > idx1 and idx1 >= 0 and idx2 <= len(self.df_filtered):
                return True
        return False

    # Getters

    def getDataSize(self) -> int:
        return len(self.df_raw)

    def getGroupPlotWidget(
        self,
        plot_type: PlotTypes,
        sensor_names: list[str],
        idx1: int = 0,
        idx2: int = 0,
    ) -> PlotPlatformForcesWidget | PlotPlatformCOPWidget | PlotFigureWidget:
        # Platform groups
        if (
            plot_type == PlotTypes.GROUP_PLATFORM_COP
            or plot_type == PlotTypes.GROUP_PLATFORM_FORCES
        ):
            # Make forces dataframes
            df_fx = pd.DataFrame()
            df_fy = pd.DataFrame()
            df_fz = pd.DataFrame()
            for sensor_name in sensor_names:
                sign = 1
                for key in self.forces_sign.keys():
                    if key in sensor_name:
                        sign = self.forces_sign[key]
                        break
                if "X_" in sensor_name:
                    df_fx[sensor_name] = self.getForce(sensor_name, sign)
                    continue
                if "Y_" in sensor_name:
                    df_fy[sensor_name] = self.getForce(sensor_name, sign)
                    continue
                if "Z_" in sensor_name:
                    df_fz[sensor_name] = self.getForce(sensor_name, sign)
                    continue
                logger.warning(
                    f"Could not recognize sensor {sensor_name}."
                    + " Needs X_, Y_ or Z_ in name to be identified."
                )
            if plot_type == PlotTypes.GROUP_PLATFORM_COP:
                plotter = PlotPlatformCOPWidget()
                if df_fx.shape[1] != 4:
                    logger.error(
                        "Could not build COP plot!"
                        + f"Need 4 X axis sensors, only {df_fx.shape[1]} provided."
                    )
                    return plotter
                if df_fy.shape[1] != 4:
                    logger.error(
                        "Could not build COP plot!"
                        + f"Need 4 Y axis sensors, only {df_fy.shape[1]} provided."
                    )
                    return plotter
                if df_fz.shape[1] != 4:
                    logger.error(
                        "Could not build COP plot!"
                        + f"Need 4 Z axis sensors, only {df_fz.shape[1]} provided."
                    )
                    return plotter
                # TODO WIP
                if self.isRangedPlot(idx1, idx2):
                    df_fx = df_fx[idx1:idx2]
                    df_fy = df_fy[idx1:idx2]
                    df_fz = df_fz[idx1:idx2]
                cop = self.getPlatformCOP(df_fx, df_fy, df_fz)
                ellipse_params = self.getEllipseFromCOP(cop[0], cop[1])
                plotter.setupPlot(cop, ellipse_params)
                return plotter
            if plot_type == PlotTypes.GROUP_PLATFORM_FORCES:
                plotter = PlotPlatformForcesWidget()
                if self.isRangedPlot(idx1, idx2):
                    plotter.setupRangedPlot(
                        self.timeincr_list, df_fx, df_fy, df_fz, idx1, idx2
                    )
                    return plotter
                plotter.setupPlot(self.timeincr_list, df_fx, df_fy, df_fz)
                return plotter
        return PlotFigureWidget()

    def getPlotPreviewWidget(
        self,
        sensor_name: str,
        idx1: int = 0,
        idx2: int = 0,
    ) -> PlotFigureWidget:
        plotter = PlotFigureWidget()

        # Check first if dataframe contains sensor_name
        if sensor_name not in self.df_filtered.columns:
            logger.error(f"Sensor name {sensor_name} not found in dataframe results!")
            return plotter

        df = self.df_filtered[sensor_name].copy(deep=True)

        if self.isRangedPlot(idx1, idx2):
            plotter.setupRangedPreviewPlot(df, idx1, idx2)
            return plotter
        plotter.setupPlot(df)
        return plotter

    def getSensorPlotWidget(
        self,
        plot_type: PlotTypes,
        sensor_name: str,
        idx1: int = 0,
        idx2: int = 0,
    ) -> PlotFigureWidget:
        plotter = PlotFigureWidget()

        # Check first if dataframe contains sensor_name
        col_exist = False
        for column in self.df_filtered.columns:
            if sensor_name in column:
                col_exist = True
                break
        if not col_exist:
            print(self.df_filtered)
            logger.error(f"Sensor name {sensor_name} not found in dataframe results!")
            return plotter

        # Do process depending on requested plot type
        df: pd.DataFrame = pd.DataFrame()
        if plot_type == PlotTypes.SENSOR_LOADCELL_FORCE:
            sign = 1
            for key in self.forces_sign.keys():
                if key in sensor_name:
                    sign = self.forces_sign[key]
                    break
            df = self.getForce(sensor_name, sign)
        elif plot_type == PlotTypes.SENSOR_ENCODER_DISTANCE:
            df = self.getDistance(sensor_name)
        elif plot_type == PlotTypes.SENSOR_IMU_ANGLES:
            df = self.getIMUAngles(sensor_name, self.imu_ang_headers)
        elif plot_type == PlotTypes.SENSOR_IMU_VELOCITY:
            df = self.getIMUValues(sensor_name, self.imu_vel_headers)
        elif plot_type == PlotTypes.SENSOR_IMU_ACCELERATION:
            df = self.getIMUValues(sensor_name, self.imu_acc_headers)

        # Setup widget and return
        if df.empty:
            return plotter
        if isinstance(df, pd.Series):
            df = df.to_frame()
        df.insert(0, "times", self.timeincr_list)
        if self.isRangedPlot(idx1, idx2):
            plotter.setupRangedPlot(df, idx1, idx2)
            return plotter
        plotter.setupPlot(df)
        return plotter

    def getRawDataframe(self) -> pd.DataFrame:
        return self.formatDataframe(self.df_raw.copy(deep=True))

    def getCalibrateDataframe(self) -> pd.DataFrame:
        return self.formatDataframe(self.df_calibrated.copy(deep=True))

    def formatDataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # Format dataframe values to 0.000000e+00
        df = df.map("{:.6e}".format)
        # Add timestamp values
        df.insert(0, "timestamp", self.timestamp_list)
        return df

    # Data process methods

    # ButterWorth filter
    def applyButterFilter(self, fs: int = 100, fc: int = 5, order: int = 6):
        b, a = butter(order, fc / (0.5 * fs), btype="low", analog=False)
        self.df_filtered = pd.DataFrame()
        for col in self.df_calibrated:
            self.df_filtered[col] = filtfilt(b, a, self.df_calibrated[col])

    # - Sensor methods
    def getForce(self, sensor_name: str, sign: int) -> pd.DataFrame:
        df = self.df_filtered[sensor_name].copy(deep=True)
        df *= sign
        return df

    def getDistance(self, sensor_name: str) -> pd.DataFrame:
        return self.df_filtered[sensor_name]

    def getIMUAngles(self, sensor_name: str, suffix_list: list[str]) -> pd.DataFrame:
        df_quat: pd.DataFrame = self.getIMUValues(sensor_name, suffix_list)
        headers = [sensor_name + "_" + suffix for suffix in suffix_list]

        rot = Rotation.from_quat(df_quat[headers].to_numpy())
        euler_ang_deg = np.degrees(rot.as_euler("xyz"))

        df_euler = pd.DataFrame(
            euler_ang_deg,
            columns=[
                sensor_name + "_yaw",
                sensor_name + "_pitch",
                sensor_name + "_roll",
            ],
        )

        return df_euler

    def getIMUValues(self, sensor_name: str, suffix_list: list[str]) -> pd.DataFrame:
        headers = [sensor_name + "_" + suffix for suffix in suffix_list]
        return self.df_filtered[headers]

    # - Platform group methods

    # Expected input format: name_1, name_2, name_3, name_4
    # Output: x1, x2, x3, x4
    def getPlatformForces(self, sensor_names: list[str]) -> pd.DataFrame:
        df_list: list[pd.DataFrame] = []
        for sensor_name in sensor_names:
            sign = 1
            for key in self.forces_sign.keys():
                if key in sensor_name:
                    sign = self.forces_sign[key]
                    break
            df_list.append(self.getForce(sensor_name, sign))
        return pd.concat(df_list)

    def getPlatformCOP(
        self, df_fx: pd.DataFrame, df_fy: pd.DataFrame, df_fz: pd.DataFrame
    ) -> tuple[pd.Series, pd.Series]:
        # Platform dimensions
        lx = 508  # mm
        ly = 308  # mm
        h = 20  # mm
        # Get sum forces
        fx = df_fx.sum(axis=1)
        fy = df_fy.sum(axis=1)
        fz = df_fz.sum(axis=1)
        # Operate
        mx = (
            ly
            / 2
            * (
                -df_fz.iloc[:, 0]
                - df_fz.iloc[:, 1]
                + df_fz.iloc[:, 2]
                + df_fz.iloc[:, 3]
            )
        )
        my = (
            lx
            / 2
            * (
                -df_fz.iloc[:, 0]
                + df_fz.iloc[:, 1]
                + df_fz.iloc[:, 2]
                - df_fz.iloc[:, 3]
            )
        )
        # Get COP
        cop_x = (-h * fx - my) / fz
        cop_y = (-h * fy + mx) / fz
        cop_x = cop_x - np.mean(cop_x)
        cop_y = cop_y - np.mean(cop_y)
        return [cop_x, cop_y]

    def getEllipseFromCOP(
        self, copx: np.array, copy: np.array
    ) -> tuple[np.array, np.array, float]:

        cov_matrix = np.cov(copx, copy)

        # Eigen vectors and angular rotation
        D, V = np.linalg.eig(cov_matrix)
        theta = np.arctan2(V[1, 0], V[0, 0])

        ellipse_axis = np.sqrt(D)

        # Ellipse params
        a = ellipse_axis[0]
        b = ellipse_axis[1]
        area = np.pi * a * b
        x0 = np.mean(copx)
        y0 = np.mean(copy)

        # Ellipse angle in rads
        phi = np.linspace(0, 2 * np.pi, 100)

        # Ellipse coords
        x = x0 + a * np.cos(phi) * np.cos(theta) - b * np.sin(phi) * np.sin(theta)
        y = y0 + a * np.cos(phi) * np.sin(theta) + b * np.sin(phi) * np.cos(theta)

        return x, y, area

    # Tare sensors

    def tareSensors(self, sensor_manager: SensorManager, last_values: int) -> None:
        for group in sensor_manager.getGroups():
            for sensor in group.getAvailableSensors().values():
                # Only tare loadcells and encoders
                if sensor.getType() not in [
                    STypes.SENSOR_LOADCELL,
                    STypes.SENSOR_ENCODER,
                ]:
                    continue
                # Tare process
                logger.debug(f"Tare sensor {sensor.getName()}")
                slope = sensor.getSlope()
                intercept = sensor.getIntercept()
                calib_values = [
                    value * slope + intercept
                    for value in sensor.getValues()[-last_values:]
                ]
                new_intercept = float(sensor.getIntercept() - np.mean(calib_values))
                logger.debug(f"From {intercept} to {new_intercept}")
                sensor_manager.setSensorIntercept(sensor, new_intercept)
