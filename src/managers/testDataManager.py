# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
from mrpt.pymrpt import mrpt
from src.qtUIs.widgets.matplotlibWidgets import (
    PlotPlatformForcesWidget,
    PlotPlatformCOPWidget,
    PlotEncoderWidget,
    PlotIMUWidget,
)
from src.managers.testManager import TestManager
from src.handlers.sensorGroup import SensorGroup
from src.enums.configPaths import ConfigPaths as CfgPaths


class TestDataManager:
    def __init__(self, test_manager: TestManager):
        self.test_mngr = test_manager
        self.setupPlotWidgets()
        self.time_list = []
        self.data_platform1 = {}
        self.data_platform2 = {}
        self.data_encoders = {}
        self.data_imus = {}

        self.forces_max_values = self.test_mngr.config_mngr.getConfigValue(
            CfgPaths.GENERAL_PLOTTERS_MAX_FORCES.value, 1000
        )
        self.stabilogram_max_values = self.test_mngr.config_mngr.getConfigValue(
            CfgPaths.GENERAL_PLOTTERS_MAX_STABILOGRAM.value, 1000
        )
        self.encoders_max_values = self.test_mngr.config_mngr.getConfigValue(
            CfgPaths.GENERAL_PLOTTERS_MAX_ENCODERS.value, 1000
        )
        self.imus_max_values = self.test_mngr.config_mngr.getConfigValue(
            CfgPaths.GENERAL_PLOTTERS_MAX_IMUS.value, 1000
        )

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

    def updatePlotWidgetDraw(self, index: int) -> None:
        if index == 1:
            self.updatePlatformForces(self.forces_max_values)
            return
        if index == 2:
            self.updateStabilograms(self.stabilogram_max_values)
            return
        if index == 3:
            self.updateEncoders(self.encoders_max_values)
            return
        if index == 4:
            self.updateIMUAngles(self.imus_max_values)
            return

    def checkDataLen(self, times: list, data: list, last_values: int = None):
        if not data or not times:
            return False, 0
        times_len = len(times)
        data_len = len(data)
        if times_len == data_len:
            if last_values is not None and data_len > last_values:
                return True, last_values
            return True, times_len
        if last_values is not None and data_len > last_values:
            return True, last_values
        return False, times_len

    def updatePlatformForces(self, last_values: int = None) -> None:
        # Get data
        time_list = self.test_mngr.getTestTimes().copy()
        p1_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform1)
        p2_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform2)
        # Check values
        p1_ready, plot_len1 = self.checkDataLen(
            time_list, next(iter(p1_data_dict.values()), None), last_values
        )
        p2_ready, plot_len2 = self.checkDataLen(
            time_list, next(iter(p2_data_dict.values()), None), last_values
        )
        if not p1_ready and not p2_ready:
            return
        # Get arrays for plots
        if p1_ready:
            times_np = np.array(
                [(t - time_list[0]) / 1000 for t in time_list[-plot_len1:]]
            )
            forces_x_p1, forces_y_p1, forces_z_p1 = self.getForces(
                p1_data_dict, plot_len1
            )
            self.forces_p1_widget.update(
                times_np, forces_x_p1, forces_y_p1, forces_z_p1
            )
        if p2_ready:
            times_np = np.array(
                [(t - time_list[0]) / 1000 for t in time_list[-plot_len2:]]
            )
            forces_x_p2, forces_y_p2, forces_z_p2 = self.getForces(
                p2_data_dict, plot_len2
            )
            self.forces_p2_widget.update(
                times_np, forces_x_p2, forces_y_p2, forces_z_p2
            )
        # Update plots with values
        # self.forces_p1_widget.update(times_np, forces_x_p1, forces_y_p1, forces_z_p1)
        # self.forces_p2_widget.update(times_np, forces_x_p2, forces_y_p2, forces_z_p2)

    def getForces(self, data_dict: dict, plot_len: int = None):
        sum_key = "Sum forces"
        forces_x = {sum_key: np.zeros(plot_len)}
        forces_y = {sum_key: np.zeros(plot_len)}
        forces_z = {sum_key: np.zeros(plot_len)}

        for key, values in data_dict.items():
            values_np = np.array(values[-plot_len:])
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
        time_list = self.test_mngr.getTestTimes().copy()
        p1_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform1)
        p2_data_dict = self.getSensorData(self.test_mngr.sensor_group_platform2)
        p1_size = len(p1_data_dict)
        p2_size = len(p2_data_dict)
        if p1_size != 12 and p2_size != 12:
            return
        # Check values
        p1_ready, plot_len1 = self.checkDataLen(
            time_list, next(iter(p1_data_dict.values()), None), last_values
        )
        p2_ready, plot_len2 = self.checkDataLen(
            time_list, next(iter(p2_data_dict.values()), None), last_values
        )
        if not p1_ready and not p2_ready:
            return
        # Get arrays for plots
        if p1_size == 12 and p1_ready:
            forces_x_p1, forces_y_p1, forces_z_p1 = self.getForces(
                p1_data_dict, plot_len1
            )
            cop_x_p1, cop_y_p1 = self.getCOP(forces_x_p1, forces_y_p1, forces_z_p1)
            self.cop_p1_widget.update(cop_x_p1, cop_y_p1)
        if p2_size == 12 and p2_ready:
            forces_x_p2, forces_y_p2, forces_z_p2 = self.getForces(
                p2_data_dict, plot_len2
            )
            cop_x_p2, cop_y_p2 = self.getCOP(forces_x_p2, forces_y_p2, forces_z_p2)
            self.cop_p2_widget.update(cop_x_p2, cop_y_p2)

    def getCOP(self, forces_x: dict, forces_y: dict, forces_z: dict):
        # Initial values (distance between sensors and upper platform, in mm)
        lx, ly, h = 508, 308, 20
        # Create forces np matrixes
        forces_x_np = np.array(list(forces_x.values()))
        forces_y_np = np.array(list(forces_y.values()))
        forces_z_np = np.array(list(forces_z.values()))
        # Operate
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
        # Get COP
        cop_x = (-h * forces_x_np[0] - my) / forces_z_np[0]
        cop_y = (-h * forces_y_np[0] + mx) / forces_z_np[0]
        return cop_x, cop_y

    def updateEncoders(self, last_values: int = None) -> None:
        # Get data
        time_list = self.test_mngr.getTestTimes().copy()
        encoder_data_dict = self.getSensorData(self.test_mngr.sensor_group_encoders)
        encoders_ready, plot_len = self.checkDataLen(
            time_list, encoder_data_dict, last_values
        )
        if not encoders_ready:
            return
        # Get arrays for plots
        times_np = np.array([(t - time_list[0]) / 1000 for t in time_list[-plot_len:]])
        encoder_data_np = {}
        for key, values in encoder_data_dict.items():
            values_np = np.array(values)
            if last_values:
                values_np = values_np[-plot_len:]
            encoder_data_np[key] = values_np
        # Update plots with values
        self.encoders_widget.update(times_np, encoder_data_np)

    def updateIMUAngles(self, last_values: int = None) -> None:
        # Get data
        imu_data_dict = self.getSensorData(
            self.test_mngr.sensor_group_imus, raw_data=True
        )
        if not imu_data_dict:
            return
        time_list = self.test_mngr.getTestTimes().copy()
        imus_ready, plot_len = self.checkDataLen(
            time_list, next(iter(imu_data_dict.values()), None), last_values
        )
        if not imus_ready:
            return
        # Get arrays for plots
        times_np = np.array([(t - time_list[0]) / 1000 for t in time_list[-plot_len:]])
        imu_data_np = {}
        for key, values in imu_data_dict.items():
            if not values[0]:
                continue
            imu_data_np[key] = self.getAngles(plot_len, values)
        # Update plots with values
        self.imu_angles_widget.update(times_np, imu_data_np)

    def getAngles(self, array_len: int, data_list: list) -> list:
        yaw_list = []
        pitch_list = []
        roll_list = []
        degrees_conv = float(180 / math.pi)

        for data in data_list[-array_len:]:
            # data: qx, qy, qz, qx, w[...], acc[...]
            quat = mrpt.math.CQuaternion_double_t(data[3], data[0], data[1], data[2])
            pose = mrpt.poses.CPose3D(quat, 0, 0, 0)
            yaw_list.append(pose.yaw() * degrees_conv)
            pitch_list.append(pose.pitch() * degrees_conv)
            roll_list.append(pose.roll() * degrees_conv)

        return [yaw_list, pitch_list, roll_list]

    def getSensorData(self, sensor_group: SensorGroup, raw_data: bool = False) -> dict:
        data_dict = {}
        if not sensor_group.getGroupIsActive():
            return data_dict
        sensor_group_info = sensor_group.getGroupInfo().copy()
        sensor_group_values = {}
        if raw_data:
            sensor_group_values = sensor_group.getGroupValues().copy()
        else:
            sensor_group_values = sensor_group.getGroupCalibValues().copy()
        for sensor_id, values in sensor_group_values.items():
            sensor_name = sensor_group_info[sensor_id][0]
            data_dict[sensor_name] = values
        return data_dict

    def getIMUData(self, sensor_data: dict, imu_data_list: list) -> dict:
        data_dict = {}
        for key, values in sensor_data.items():
            # FIXME despite not being connected, there will be a list with empty lists...
            if not values[0]:
                continue
            for i, imu_data in enumerate(imu_data_list):
                new_key = f"{key}_{imu_data}"
                if new_key not in data_dict:
                    data_dict[new_key] = []
                data_dict[new_key].extend([value[i] for value in values])
        return data_dict

    def getGroupMeanValues(self, sensor_group: SensorGroup, last_values: int) -> dict:
        mean_dict = {}
        if not sensor_group.getGroupIsActive():
            return mean_dict
        sensor_group_values = sensor_group.getGroupCalibValues().copy()
        for sensor_id, values in sensor_group_values.items():
            mean_dict[sensor_id] = np.mean(values[-int(last_values) :])
        return mean_dict

    def tareSensors(self, value_range: int) -> None:
        for sensor_group in [
            self.test_mngr.sensor_group_platform1,
            self.test_mngr.sensor_group_platform2,
            self.test_mngr.sensor_group_encoders,
        ]:
            mean_dict = self.getGroupMeanValues(sensor_group, value_range)
            sensor_group.tareSensors(mean_dict)

    def getDataFrame(self, raw_data: bool = False) -> pd.DataFrame:
        timestamp_dict = {"timestamp": self.test_mngr.getTestTimes().copy()}
        p1_loadcells_dict = self.getSensorData(
            self.test_mngr.sensor_group_platform1, raw_data
        )
        p2_loadcells_dict = self.getSensorData(
            self.test_mngr.sensor_group_platform2, raw_data
        )
        encoders_dict = self.getSensorData(
            self.test_mngr.sensor_group_encoders, raw_data
        )
        imus_dict = self.getSensorData(self.test_mngr.sensor_group_imus, True)
        imu_data_list = [
            "q_x",
            "q_y",
            "q_z",
            "q_w",
            "w_x",
            "w_y",
            "w_z",
            "x_acc",
            "y_acc",
            "z_acc",
        ]
        imus_strip_dict = self.getIMUData(imus_dict, imu_data_list)
        merged_data = {
            **timestamp_dict,
            **p1_loadcells_dict,
            **p2_loadcells_dict,
            **encoders_dict,
            **imus_strip_dict,
        }
        df = pd.DataFrame(merged_data)
        # Format dataframes values to 0.000000e+00
        df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: "{:.6e}".format(x))
        return df
