# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import threading
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from src.utils import LogHandler


class PhidgetLoadCellsHandler:
    log_handler = None

    def __init__(self, sensor_set_name):
        self.log_handler = LogHandler(
            str(__class__.__name__ + '-' + sensor_set_name))
        self.sensor_list = []
        self.sensor_data = {}
        self.sensor_data_raw = {}
        self.sensor_data_mutex = threading.Lock()

        def onVoltageRatioChange(self,
                                 voltageRatio,
                                 mutex: threading.Lock() = self.sensor_data_mutex,
                                 sensor_list: list = self.sensor_list,
                                 sensor_data_raw: dict = self.sensor_data_raw,
                                 sensor_data: dict = self.sensor_data,
                                 log_handler: LogHandler = self.log_handler,):
            serial = self.getDeviceSerialNumber()
            channel = self.getChannel()
            connected_sensor = False
            m = b = 0
            for i, sensor in enumerate(sensor_list):
                if not sensor['read_data']:
                    continue
                if sensor['serial'] == serial and sensor['channel'] == channel:
                    m = sensor['calibration_data']['m']
                    b = sensor['calibration_data']['b']
                    name = sensor['name']
                    connected_sensor = True
                    break
            if not connected_sensor:
                return
            force = voltageRatio * m + b

            # log_handler.logger.debug("[" + str(serial) + "_" +
            #                          str(channel) + "]: " + str(voltageRatio) + " V (" + str(force) + " N)")

            mutex.acquire()
            sensor_data_raw[name] = voltageRatio
            sensor_data[name] = force
            mutex.release()

        self.onVoltageRatioChange = onVoltageRatioChange

    def addSensor(self, sensor_params: dict):
        required_keys = ['id', 'name', 'read_data',
                         'serial', 'channel', 'calibration_data',
                         'config_path']
        if not all(key in sensor_params.keys() for key in required_keys):
            self.log_handler.logger.error(
                "Sensor does not have the required keys!")
            return

        sensor = sensor_params.copy()
        sensor['status'] = "Ignored"  # Default status until connection check
        sensor['sensor'] = VoltageRatioInput()
        sensor['sensor'].setDeviceSerialNumber(sensor_params['serial'])
        sensor['sensor'].setChannel(sensor_params['channel'])
        sensor['sensor'].setOnVoltageRatioChangeHandler(
            self.onVoltageRatioChange)

        self.sensor_list.append(sensor)

    def clearSensors(self):
        self.sensor_list.clear()
        self.sensor_data.clear()

    def tareSensors(self, tare_dict: dict):
        for sensor in self.sensor_list:
            if sensor['name'] in tare_dict:
                prev_value = sensor['calibration_data']['b']
                sensor['calibration_data']['b'] -= tare_dict[sensor['name']]
                self.log_handler.logger.debug(
                    "TARED " + sensor['name'] + " with value: " + str(prev_value) + " to value: " + str(sensor['calibration_data']['b']))

    def getSensorListDict(self):
        key_list = ['id', 'name', 'read_data', 'status', 'config_path']
        return [{k: sensor[k] for k in key_list} for sensor in self.sensor_list]

    def getSensorHeaders(self):
        self.sensor_data_mutex.acquire()
        keys = list(self.sensor_data.keys())
        self.sensor_data_mutex.release()
        return keys

    def getSensorData(self):
        self.sensor_data_mutex.acquire()
        data = list(self.sensor_data.values())
        self.sensor_data_mutex.release()
        return data

    def getSensorDataRaw(self):
        self.sensor_data_mutex.acquire()
        data = list(self.sensor_data_raw.values())
        self.sensor_data_mutex.release()
        return data

    # Returns true if there is at least one sensor connected
    def connect(self):
        self.sensors_connected = False
        if not self.sensor_list:
            self.log_handler.logger.info(
                "No load cells added to try connection.")
            return self.sensors_connected
        for sensor in self.sensor_list:
            if not sensor['sensor'].getAttached() and sensor['read_data']:
                try:
                    sensor['sensor'].openWaitForAttachment(1000)  # in ms
                    sensor['sensor'].setDataInterval(8)  # in ms
                    # FIXME Identifica también los otros canales aunque no haya sensor conectado!
                    # if loadCell['input'].getSensorType() != Bridge.PHIDGET_BRIDGE_SENSOR_TYPE_NONE:
                    #     loadCell['status'] = "Active"
                    #     self.phidget_sensor_connected = True
                    # Close communication until start process
                    sensor['status'] = "Active"
                    sensor['sensor'].close()
                    self.sensors_connected = True
                    # print(loadCell['input'].getSensorType())
                except (PhidgetException):
                    self.log_handler.logger.warn("Could not connect to serial " + str(
                        sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
                    sensor['status'] = "Disconnected"
        return self.sensors_connected

    def start(self):
        if not self.sensors_connected:
            self.log_handler.logger.info(
                "Ignoring Load Cells sensors in test, no one connected.")
            return
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue
            try:
                sensor['sensor'].openWaitForAttachment(2000)  # in ms
                sensor['sensor'].setDataInterval(8)  # in ms
            except (PhidgetException):
                self.log_handler.logger.warn("Could not open serial " + str(sensor['sensor'].getDeviceSerialNumber(
                )) + ", channel " + str(sensor['sensor'].getChannel()))
                sensor['sensor'].close()

    def stop(self):
        if not self.sensors_connected:
            return
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue
            try:
                sensor['sensor'].close()
            except (PhidgetException):
                self.log_handler.logger.error("Could not close serial " + str(
                    sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
