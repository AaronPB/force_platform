# -*- coding: utf-8 -*-

import numpy as np
from src.qtUIs.widgets.matplotlibWidgets import *
from src.managers.testManager import TestManager


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
            self.updatePlatformForces()
            return
        if index == 2:
            self.cop_p1_widget.update(
                self.getStabilograms(self.test_mngr.sensor_group_platform1, time_len)
            )
            self.cop_p2_widget.update(
                self.getStabilograms(self.test_mngr.sensor_group_platform2, time_len)
            )
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

    def updatePlatformForces(self) -> None:
        # Get data
        time_list = self.test_mngr.getTestTimes().copy()
        p1_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform1)
        p2_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform2)
        # Get arrays for plots
        times_np = np.array([(t - time_list[0]) / 1000 for t in time_list])
        forces_x_p1, forces_y_p1, forces_z_p1 = self.getForces(
            times_np.size, p1_data_dict
        )
        forces_x_p2, forces_y_p2, forces_z_p2 = self.getForces(
            times_np.size, p2_data_dict
        )
        # Update plots with values
        self.forces_p1_widget.update(times_np, forces_x_p1, forces_y_p1, forces_z_p1)
        self.forces_p2_widget.update(times_np, forces_x_p2, forces_y_p2, forces_z_p2)

    def getForces(self, default_len: int, data_dict: dict):
        sum_key = "Sum forces"
        forces_x = {sum_key: np.zeros(default_len)}
        forces_y = {sum_key: np.zeros(default_len)}
        forces_z = {sum_key: np.zeros(default_len)}

        for key, values in data_dict.items():
            values_np = np.array(values)
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

        # TODO update sum

        return forces_x, forces_y, forces_z

    def getStabilograms(self, sensor_group: SensorGroup, time_len: int) -> list:
        data_list = []
        platform_data_dict = self.getSensorData(sensor_group)
        if len(platform_data_dict) != 12:
            return None
        if any(len(data) != time_len for data in platform_data_dict.values()):
            return None
        # Initial values
        lx = 508  # (mm) x distance between sensors
        ly = 308  # (mm) y distance between sensors
        h = 20  # (mm) z distance between sensors and upper platform
        # Create list [fx1, ..., fx4, fy1, ..., fy4, fz1, ..., fz4]
        forces_list = []
        for values in platform_data_dict.values():
            forces_list.append(np.array(values))
        forces_np = np.array(forces_list)
        # Operate
        fx = forces_np[:, 0:4].sum(axis=1)
        fy = forces_np[:, 4:8].sum(axis=1)
        fz = forces_np[:, 8:12].sum(axis=1)
        mx = ly / 2 * (-forces_np[:, 0:4].sum(axis=1))
        my = lx / 2 * (-forces_np[:, 0:4].sum(axis=1))
        mz = ly / 2 * (-forces_np[:, 4:8].sum(axis=1)) + lx / 2 * (
            forces_np[:, 8:12].sum(axis=1)
        )
        # Get COP and relative COP
        cop_x = (-h * fx - my) / fz
        cop_y = (-h * fy + mx) / fz
        relcop_x = cop_x - np.mean(cop_x)
        relcop_y = cop_y - np.mean(cop_y)
        return [relcop_x, relcop_y]

    def getEncoderData(self, sensor_group: SensorGroup, time_len: int) -> dict:
        encoder_data_dict = self.getSensorData(sensor_group)
        if not encoder_data_dict:
            return None
        if any(len(data) != time_len for data in encoder_data_dict.values()):
            return None
        return encoder_data_dict

    def getIMUAngles(self, sensor_group: SensorGroup, time_len: int) -> dict:
        data_dict = {}
        # TODO Transform to Euler data
        return data_dict

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
