# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from mrpt.pymrpt import mrpt
from src.qtUIs.widgets.matplotlibWidgets import (
    PlotFigureWidget,
    PlotPlatformCOPWidget,
)
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
        self.imu_ang_headers: list[str] = ["q_x", "q_y", "q_z", "q_w"]
        self.imu_vel_headers: list[str] = ["w_x", "w_y", "w_z"]
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

    # Data load methods

    def loadData(self, time_list: list, sensor_groups: list[SensorGroup]) -> None:
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
                    for suffix, values in enumerate(
                        self.imu_ang_headers
                        + self.imu_vel_headers
                        + self.imu_acc_headers,
                        values_list,
                    ):
                        imu_name = sensor.getName() + "_" + suffix
                        self.df_raw[imu_name] = values
                        # No need to calibrate IMUs
                        self.df_calibrated[imu_name] = values
                    continue
                self.df_raw[sensor.getName()] = sensor.getValues()
                slope = sensor.getSlope()
                intercept = sensor.getIntercept()
                self.df_calibrated[sensor.getName()] = [
                    value * slope + intercept for value in sensor.getValues()
                ]
        # TODO Just for test purposes. Move to proper place in future.
        self.applyButterFilter()

    # Transforms values lists into separate variable lists.
    # Ex: [ti [gx, gy, gz]] -> [gx[ti], gy[ti], gz[ti]]
    def getListedData(self, sensor: Sensor) -> list[list[float]]:
        main_list = sensor.getValues()
        new_main_list: list[list[float]] = [[]]
        for value_list in main_list:
            for i, value in enumerate(value_list):
                new_main_list[i].append(value)
        return new_main_list

    # Getters

    def getGroupPlotWidget(
        self,
        plot_type: PlotTypes,
        sensor_names: list[str],
        idx1: int = 0,
        idx2: int = 0,
    ) -> None:
        # WIP
        if plot_type == PlotTypes.GROUP_PLATFORM_COP:
            if len(sensor_names) != 12:
                logger.error(
                    f"Could not build COP plot!"
                    + "Need 12 sensors, only {len(sensor_names)} provided."
                )
                return None
            # TODO process to build COP graph
            return None
        if plot_type == PlotTypes.GROUP_PLATFORM_FORCES:
            if len(sensor_names) != 12:
                logger.error(
                    f"Could not build forces plot!"
                    + "Need 12 sensors, only {len(sensor_names)} provided."
                )
                return None
            # TODO process to build forces graph
            return None
        return None

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

        # Check input ranges values
        ranged_plot = False
        if idx1 != 0 or idx2 != 0:
            if idx2 > idx1 and idx1 >= 0 and idx2 <= len(self.df_filtered):
                ranged_plot = True

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
        if ranged_plot:
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
        yaw_list = []
        pitch_list = []
        roll_list = []
        degrees_conv = float(180 / math.pi)

        for _, row in df_quat.iterrows():
            quat = mrpt.math.CQuaternion_double_t(
                row[sensor_name + "_" + self.imu_ang_headers[3]],
                row[sensor_name + "_" + self.imu_ang_headers[0]],
                row[sensor_name + "_" + self.imu_ang_headers[1]],
                row[sensor_name + "_" + self.imu_ang_headers[2]],
            )
            pose = mrpt.poses.CPose3D(quat, 0, 0, 0)
            yaw_list.append(pose.yaw() * degrees_conv)
            pitch_list.append(pose.pitch() * degrees_conv)
            roll_list.append(pose.roll() * degrees_conv)

        return pd.DataFrame(
            {
                sensor_name + "_yaw": yaw_list,
                sensor_name + "_pitch": pitch_list,
                sensor_name + "_roll": roll_list,
            }
        )

    def getIMUValues(self, sensor_name: str, suffix_list: list[str]) -> pd.DataFrame:
        imu_index_list: list[str] = []
        for suffix in suffix_list:
            imu_index_list.append(sensor_name + "_" + suffix)
        return self.df_filtered[imu_index_list]

    # - TODO Platform group methods

    def getPlatformForces(self) -> pd.DataFrame:
        pass

    def getPlatformCOP(self) -> pd.DataFrame:
        pass

    # TODO Tare sensors

    def tareSensors(self, sensor_list: list[Sensor]) -> None:
        pass
