# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import threading
from mrpt import pymrpt
from src.utils import LogHandler
mrpt = pymrpt.mrpt


class TaoRoboticsIMUsHandler:
    def __init__(self):
        self.log_handler = LogHandler(str(__class__.__name__))
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

        self.sensor_list.append(sensor)

    def clearSensors(self):
        self.sensor_list.clear()

    def getSensorListDict(self):
        key_list = ['id', 'name', 'read_data', 'status']
        return [{k: sensor[k] for k in key_list} for sensor in self.sensor_list]

    def getSensorData(self):
        self.sensor_data_mutex.acquire()
        # Get data list
        for sensor in self.sensor_list:
            if sensor['read_data']:
                sensor['sensor'].doProcess()
                obs_list = sensor['sensor'].getObservations()
                if not obs_list.empty():
                    # TODO get: 4 quaternions and 3 angular velocities
                    pass
        data = list(self.sensor_data.values())
        self.sensor_data_mutex.release()
        return data

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
                    sensor['status'] = "Active"
                    # sensor['sensor'].close() FIXME add close option??
                    self.sensors_connected = True
                except (Exception):
                    self.log_handler.logger.warn(
                        "Could not connect to IMU " + str(sensor['name']))
                    sensor['status'] = "Disconnected"
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
            try:
                sensor['sensor'].initialize()
                sensor_headers.append(sensor['name'])
            except (Exception):
                self.log_handler.logger.warn(
                    "Could not connect to IMU " + str(sensor['name']))
                # sensor['sensor'].close() FIXME add close option??
        return sensor_headers

    def stop(self):
        if not self.sensors_connected:
            return
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue
            try:
                # sensor['sensor'].close() FIXME add close option??
                pass
            except (Exception):
                self.log_handler.logger.error(
                    "Could not close IMU " + str(sensor['name']))
