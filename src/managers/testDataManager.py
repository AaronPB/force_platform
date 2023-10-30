import numpy as np
from src.qtUIs.widgets.matplotlibWidgets import *
from src.managers.testManager import TestManager


class TestDataManager:
    def __init__(self, test_manager: TestManager):
        self.test_mngr = test_manager
        self.setupPlotWidgets()

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
            encoders_group_name, encoders_group_size)
        self.imu_angles_widget = PlotIMUWidget(
            imus_group_name, imus_group_size)

    def updatePlotWidgetDraw(self, index, timestamp_list: list):
        # WIP
        time_len = len(timestamp_list)
        if index == 1:
            self.forces_p1_widget.update(timestamp_list, self.getForcesTotal(
                self.test_mngr.sensor_group_platform1, time_len))
            self.forces_p2_widget.update(timestamp_list, self.getForcesTotal(
                self.test_mngr.sensor_group_platform2, time_len))
            return
        if index == 2:
            self.cop_p1_widget.update(timestamp_list, self.getStabilograms(
                self.test_mngr.sensor_group_platform1, time_len))
            self.cop_p2_widget.update(timestamp_list, self.getStabilograms(
                self.test_mngr.sensor_group_platform2, time_len))
            return
        if index == 3:
            self.encoders_widget.update(timestamp_list, self.getEncoderData(
                self.test_mngr.sensor_group_encoders, time_len))
            return
        if index == 4:
            self.imu_angles_widget.update(
                timestamp_list, self.getIMUAngles(self.test_mngr.sensor_group_imus, time_len))
            return

    def getPlaftormForces(self, sensor_group: SensorGroup, time_len: int) -> dict:
        platform_data_dict = self.getCalibratedData(sensor_group)
        if not platform_data_dict:
            return None
        if len(platform_data_dict) != time_len:
            return None
        if any(len(data) != time_len for data in platform_data_dict.values()):
            return None
        return platform_data_dict

    def getStabilograms(self, sensor_group: SensorGroup, time_len: int) -> list:
        data_list = []
        platform_data_dict = self.getCalibratedData(sensor_group)
        if len(platform_data_dict) != 12:
            return None
        if any(len(data) != time_len for data in platform_data_dict.values()):
            return None
        # Initial values
        lx = 508  # (mm) x distance between sensors
        ly = 308  # (mm) y distance between sensors
        h = 20    # (mm) z distance between sensors and upper platform
        # Create list [fx1, ..., fx4, fy1, ..., fy4, fz1, ..., fz4]
        forces_list = []
        for values in platform_data_dict.values():
            forces_list.append(np.array(values))
        forces_np = np.array(forces_list)
        # Operate
        fx = forces_np[:, 0:4].sum(axis=1)
        fy = forces_np[:, 4:8].sum(axis=1)
        fz = forces_np[:, 8:12].sum(axis=1)
        mx = ly/2 * (-forces_np[:, 0:4].sum(axis=1))
        my = lx/2 * (-forces_np[:, 0:4].sum(axis=1))
        mz = ly/2 * (-forces_np[:, 4:8].sum(axis=1)) + \
            lx/2 * (forces_np[:, 8:12].sum(axis=1))
        # Get COP and relative COP
        cop_x = (-h * fx - my)/fz
        cop_y = (-h * fy + mx)/fz
        relcop_x = cop_x - np.mean(cop_x)
        relcop_y = cop_y - np.mean(cop_y)
        return [relcop_x, relcop_y]

    def getEncoderData(self, sensor_group: SensorGroup, time_len: int) -> dict:
        encoder_data_dict = self.getCalibratedData(sensor_group)
        if not encoder_data_dict:
            return None
        if any(len(data) != time_len for data in encoder_data_dict.values()):
            return None
        return encoder_data_dict

    def getIMUAngles(self, sensor_group: SensorGroup, time_len: int) -> dict:
        data_dict = {}
        # TODO Transform to Euler data
        return data_dict

    def getRawData(self, sensor_group: SensorGroup) -> dict:
        raw_data_dict = {}
        sensor_group_info = sensor_group.getGroupInfo()
        sensor_group_values = sensor_group.getGroupValues()
        for sensor_id, values in sensor_group_values.items():
            sensor_name = sensor_group_info[sensor_id][0]
            raw_data_dict[sensor_name] = values
        return raw_data_dict

    def getCalibratedData(self, sensor_group: SensorGroup) -> dict:
        calib_data_dict = {}
        sensor_group_info = sensor_group.getGroupInfo()
        sensor_group_values = sensor_group.getGroupValues()
        sensor_group_calibparams = sensor_group.getGroupCalibrationParams()
        for sensor_id, values in sensor_group_values.items():
            sensor_name = sensor_group_info[sensor_id][0]
            calib_params = sensor_group_calibparams[sensor_id]
            slope, intercept = calib_params[0], calib_params[1]
            calib_values = [slope * value + intercept for value in values]
            calib_data_dict[sensor_name] = calib_values
        return calib_data_dict

    def saveDataToCSV(self, timestamp_list: list):
        # Create dataframe with all updaters returns
        pass
