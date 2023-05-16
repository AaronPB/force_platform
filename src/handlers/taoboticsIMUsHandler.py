# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 05/05/2023
"""

import threading
from mrpt import pymrpt
from src.utils import LogHandler
mrpt = pymrpt.mrpt


class TaoboticsIMUsHandler:
    def __init__(self, sensor_set_name):
        self.log_handler = LogHandler(
            str(__class__.__name__ + '-' + sensor_set_name))
        self.sensor_list = []
        self.sensor_data = {}
        self.sensor_data_mutex = threading.Lock()

    def addSensor(self, sensor_params: dict):
        required_keys = ['id', 'name', 'read_data',
                         'serial', 'channel', 'calibration_data']
        if not all(key in sensor_params.keys() for key in required_keys):
            self.log_handler.logger.error(
                "Sensor does not have the required keys!")
            return

        sensor = sensor_params.copy()
        sensor['status'] = "Ignored"  # Default status until connection check
        sensor['sensor'] = mrpt.hwdrivers.CTaoboticsIMU()
        sensor['sensor'].setSerialPort(sensor_params['serial'])
        sensor['sensor'].setSensorLabel(sensor_params['name'])

        self.sensor_list.append(sensor)

    def clearSensors(self):
        for sensor in self.sensor_list:
            del (sensor['sensor'])
        self.sensor_list.clear()
        self.sensor_data.clear()

    def getSensorListDict(self):
        key_list = ['id', 'name', 'read_data', 'status']
        return [{k: sensor[k] for k in key_list} for sensor in self.sensor_list]

    def getSensorHeaders(self):
        # First iteration to collect sensor names
        self.getSensorData()
        # Send keys
        self.sensor_data_mutex.acquire()
        keys = list(self.sensor_data.keys())
        self.sensor_data_mutex.release()
        new_keys = []
        data_types = ['qx', 'qy', 'qz', 'qw', 'wx', 'wy', 'wz']
        for key in keys:
            for suf in data_types:
                new_keys.append(key + '_' + suf)
        return new_keys

    # Returns a list of dictionaries
    def getSensorData(self):
        # Get data list
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue

            if sensor['sensor'].getState() != mrpt.hwdrivers.CGenericSensor.TSensorState.ssWorking:
                continue

            q_x = q_y = q_z = q_w = w_x = w_y = w_z = -1
            sensor['sensor'].doProcess()
            obs_list = sensor['sensor'].getObservations()
            if not obs_list.empty():
                for t, obs in obs_list:
                    # Quaternions
                    q_x = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_X)
                    q_y = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_Y)
                    q_z = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_Z)
                    q_w = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_W)
                    # Angular velocities
                    w_x = obs.get(mrpt.obs.TIMUDataIndex.IMU_WX)
                    w_y = obs.get(mrpt.obs.TIMUDataIndex.IMU_WY)
                    w_z = obs.get(mrpt.obs.TIMUDataIndex.IMU_WZ)
            values = [q_x, q_y, q_z, q_w, w_x, w_y, w_z]
            self.sensor_data_mutex.acquire()
            self.sensor_data[sensor['name']] = values
            self.sensor_data_mutex.release()

        self.sensor_data_mutex.acquire()
        data = list(self.sensor_data.values())
        self.sensor_data_mutex.release()
        return sum(data, [])

    # Returns true if there is at least one sensor connected
    def connect(self):
        self.sensors_connected = False
        if not self.sensor_list:
            self.log_handler.logger.info(
                "No IMUs added to try connection.")
            return self.sensors_connected
        for sensor in self.sensor_list:
            if sensor['read_data']:
                try:
                    sensor['sensor'].initialize()
                except (Exception):
                    self.log_handler.logger.error(
                        "IMU " + str(sensor['name']) + " throws an exception!")
                    sensor['status'] = "Disconnected"
                    continue

                if sensor['sensor'].getState() != mrpt.hwdrivers.CGenericSensor.TSensorState.ssWorking:
                    self.log_handler.logger.warn(
                        "Could not connect to IMU " + str(sensor['name']))
                    sensor['status'] = "Disconnected"
                    continue

                sensor['status'] = "Active"
                self.sensors_connected = True
        return self.sensors_connected

    def start(self):
        sensor_headers = []
        if not self.sensors_connected:
            self.log_handler.logger.info(
                "Ignoring IMU sensors in test, no one connected.")
            return sensor_headers
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue
            if sensor['sensor'].getState() != mrpt.hwdrivers.CGenericSensor.TSensorState.ssWorking:
                try:
                    sensor['sensor'].initialize()
                except (Exception):
                    self.log_handler.logger.error(
                        "IMU " + str(sensor['name']) + " throws an exception!")
                if sensor['sensor'].getState() != mrpt.hwdrivers.CGenericSensor.TSensorState.ssWorking:
                    self.log_handler.logger.warn(
                        "Could not connect to IMU " + str(sensor['name']))
                    continue
            sensor_headers.append(sensor['name'])
        return sensor_headers

    def stop(self):
        self.clearSensors()
        # if not self.sensors_connected:
        #     return
        # for sensor in self.sensor_list:
        #     if not sensor['read_data']:
        #         continue
        #     try:
        #         # sensor['sensor'].close() FIXME add close option??
        #         pass
        #     except (Exception):
        #         self.log_handler.logger.error(
        #             "Could not close IMU " + str(sensor['name']))
