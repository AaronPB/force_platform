# -*- coding: utf-8 -*-

import numpy as np
from src.qtUIs.widgets.matplotlibWidgets import (
    PlotPlatformForcesWidget,
    PlotPlatformCOPWidget,
    PlotEncoderWidget,
    PlotIMUWidget,
)
from src.managers.testManager import TestManager
from src.handlers.sensorGroup import SensorGroup


class TestDataManager:
    def __init__(self, test_manager: TestManager):
        self.test_mngr = test_manager
        self.setupPlotWidgets()
        self.time_list = []
        self.data_platform1 = {}
        self.data_platform2 = {}
        self.data_encoders = {}
        self.data_imus = {}

    def setupPlotWidgets(self):
        p1_group_name = self.test_mngr.sensor_group_platform1.getGroupName()
        p2_group_name = self.test_mngr.sensor_group_platform2.getGroupName()
        encoders_group_name = self.test_mngr.sensor_group_encoders.getGroupName()
        encoders_group_size = self.test_mngr.sensor_group_encoders.getGroupSize()
        imus_group_name = self.test_mngr.sensor_group_imus.getGroupName()
        imus_group_size = self.test_mngr.sensor_group_imus.getGroupSize()

        self.forces_p1_widget = PlotPlatformForcesWidget(p1_group_name)
        self.forces_p2_widget = PlotPlatformForcesWidget(p2_group_name)
        self.cop_p1_widget = PlotPlatformCOPWidget(p1_group_name)
        self.cop_p2_widget = PlotPlatformCOPWidget(p2_group_name)
        self.encoders_widget = PlotEncoderWidget(
            encoders_group_name, encoders_group_size
        )
        self.imu_angles_widget = PlotIMUWidget(imus_group_name, imus_group_size)

    def updatePlotWidgetDraw(self, index, timestamp_list: list = None):
        time_len = 100
        if index == 1:
            self.updatePlatformForces(1000)
            return
        if index == 2:
            self.updateStabilograms(2000)
            return
        if index == 3:
            self.encoders_widget.update(
                timestamp_list,
                self.getEncoderData(self.test_mngr.sensor_group_encoders, time_len),
            )
            return
        if index == 4:
            self.imu_angles_widget.update(
                timestamp_list,
                self.getIMUAngles(self.test_mngr.sensor_group_imus, time_len),
            )
            return

    def updatePlatformForces(self, last_values: int = None) -> None:
        # Get data
        time_list = self.test_mngr.getTestTimes().copy()
        p1_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform1)
        p2_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform2)
        # Get arrays for plots
        times_np = np.array([(t - time_list[0]) / 1000 for t in time_list])
        if last_values:
            times_np = times_np[-last_values:]
        forces_x_p1, forces_y_p1, forces_z_p1 = self.getForces(
            times_np.size, p1_data_dict, last_values
        )
        forces_x_p2, forces_y_p2, forces_z_p2 = self.getForces(
            times_np.size, p2_data_dict, last_values
        )
        # Update plots with values
        self.forces_p1_widget.update(times_np, forces_x_p1, forces_y_p1, forces_z_p1)
        self.forces_p2_widget.update(times_np, forces_x_p2, forces_y_p2, forces_z_p2)

    def getForces(self, array_len: int, data_dict: dict, last_values: int = None):
        sum_key = "Sum forces"
        forces_x = {sum_key: np.zeros(array_len)}
        forces_y = {sum_key: np.zeros(array_len)}
        forces_z = {sum_key: np.zeros(array_len)}

        for key, values in data_dict.items():
            values_np = np.array(values)
            if last_values:
                values_np = values_np[-last_values:]
            if "LoadCell_Z" in key:
                forces_z[key] = values_np
                forces_z[sum_key] += values_np
            if "LoadCell_X" in key:
                sign = 1
                if "1" in key or "4" in key:
                    sign = -1
                forces_x[key] = values_np * sign
                forces_x[sum_key] += forces_x[key]
            if "LoadCell_Y" in key:
                sign = 1
                if "1" in key or "2" in key:
                    sign = -1
                forces_y[key] = values_np * sign
                forces_y[sum_key] += forces_y[key]

        return forces_x, forces_y, forces_z

    def updateStabilograms(self, last_values: int = None) -> None:
        # Get data
        time_len = last_values
        if not time_len:
            time_len = len(self.test_mngr.getTestTimes().copy())
        p1_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform1)
        p2_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform2)
        p1_size = len(p1_data_dict)
        p2_size = len(p2_data_dict)
        # Get arrays for plots
        if p1_size == 12:
            forces_x_p1, forces_y_p1, forces_z_p1 = self.getForces(
                time_len, p1_data_dict, last_values
            )
            cop_x_p1, cop_y_p1 = self.getCOP(
                time_len, forces_x_p1, forces_y_p1, forces_z_p1
            )
        if p2_size == 12:
            forces_x_p2, forces_y_p2, forces_z_p2 = self.getForces(
                time_len, p2_data_dict, last_values
            )

            cop_x_p2, cop_y_p2 = self.getCOP(
                time_len, forces_x_p2, forces_y_p2, forces_z_p2
            )
        # Update plots with values
        if p1_size == 12:
            self.cop_p1_widget.update(cop_x_p1, cop_y_p1)
        if p2_size == 12:
            self.cop_p2_widget.update(cop_x_p2, cop_y_p2)

    def getCOP(self, array_len: int, forces_x: dict, forces_y: dict, forces_z: dict):
        relcop_x = np.zeros(array_len)
        relcop_y = np.zeros(array_len)
        # Initial values
        lx = 508  # (mm) x distance between sensors
        ly = 308  # (mm) y distance between sensors
        h = 20  # (mm) z distance between sensors and upper platform
        # Create forces np matrixes
        forces_x_np = np.array(list(forces_x.values()))
        forces_y_np = np.array(list(forces_y.values()))
        forces_z_np = np.array(list(forces_z.values()))
        # Operate
        fx = forces_x_np[0]
        fy = forces_y_np[0]
        fz = forces_z_np[0]
        mx = (
            ly
            / 2
            * (-forces_z_np[4] + forces_z_np[1] + forces_z_np[2] - forces_z_np[3])
        )
        my = (
            lx
            / 2
            * (-forces_z_np[4] + forces_z_np[1] + forces_z_np[2] + forces_z_np[3])
        )

        # Get COP and relative COP
        cop_x = (-h * fx - my) / fz
        cop_y = (-h * fy + mx) / fz
        relcop_x = cop_x - np.mean(cop_x)
        relcop_y = cop_y - np.mean(cop_y)
        return relcop_x, relcop_y

    def updateEncoders(self) -> None:
        # Get data
        time_list = self.test_mngr.getTestTimes().copy()
        encoder_data_dict = self.getSensorData(self.test_mngr.sensor_group_encoders)
        # Get arrays for plots
        times_np = np.array([(t - time_list[0]) / 1000 for t in time_list])
        encoder_data_np = {}
        for key, values in encoder_data_dict.items():
            encoder_data_np[key] = np.array(values)
        # Update plots with values
        self.encoders_widget.update(times_np, encoder_data_np)

    def updateIMUAngles(self) -> None:
        # Get data
        time_list = self.test_mngr.getTestTimes().copy()
        imu_data_dict = self.getSensorData(self.test_mngr.sensor_group_imus)
        # Get arrays for plots
        times_np = np.array([(t - time_list[0]) / 1000 for t in time_list])
        imu_data_np = {}
        for key, values in imu_data_dict.items():
            imu_data_np[key] = self.getAngles(times_np.size, values)
        # Update plots with values
        self.encoders_widget.update(times_np, imu_data_np)

    def getAngles(self, array_len: int, data_dict: dict) -> list:
        ankle_angles_np = np.zeros(array_len)
        knee_angles_np = np.zeros(array_len)
        hip_angles_np = np.zeros(array_len)

        # TODO Transform to Euler data

        return [ankle_angles_np, knee_angles_np, hip_angles_np]

    def getSensorData(self, sensor_group: SensorGroup, raw_data: bool = False) -> dict:
        data_dict = {}
        sensor_group_info = sensor_group.getGroupInfo().copy()
        sensor_group_values = sensor_group.getGroupCalibValues().copy()
        if raw_data:
            sensor_group_values = sensor_group.getGroupValues().copy()
        for sensor_id, values in sensor_group_values.items():
            sensor_name = sensor_group_info[sensor_id][0]
            data_dict[sensor_name] = values
        return data_dict

    def saveDataToCSV(self, timestamp_list: list):
        # Create dataframe with all updaters returns
        pass
