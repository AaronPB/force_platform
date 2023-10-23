# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 12/05/2023
"""

import threading
import concurrent.futures
from Phidget22.Phidget import *
from Phidget22.Devices.Encoder import *
from src.utils import LogHandler


class PhidgetEncodersHandler:
    def __init__(self, sensor_set_name):
        self.log_handler = LogHandler(
            str(__class__.__name__ + '-' + sensor_set_name))
        self.sensor_list = []
        self.sensor_data = {}
        self.sensor_data_raw = {}
        self.sensor_data_mutex = threading.Lock()

        def onPositionChangeHandler(self,
                                    positionChange, timeChange, indexTriggered,
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
                    init_pose = sensor['initial_position']
                    connected_sensor = True
                    break
            if not connected_sensor:
                return

            # log_handler.logger.debug("[" + str(serial) + "_" +
            #                          str(channel) + "]: " + "Incr pulse: " + str(positionChange) + " Incr dist:" +
            #                          str(positionChange * m) + " mm")

            mutex.acquire()
            sensor_data_raw[name] = sensor_data_raw.get(
                name, init_pose) + positionChange
            sensor_data[name] = sensor_data_raw[name] * m + b
            mutex.release()

        self.onPositionChangeHandler = onPositionChangeHandler

    def addSensor(self, sensor_params: dict):
        required_keys = ['id', 'name', 'read_data', 'serial',
                         'channel', 'calibration_data', 'properties',
                         'initial_position', 'config_path']
        if not all(key in sensor_params.keys() for key in required_keys):
            self.log_handler.logger.error(
                "Sensor does not have the required keys!")
            return

        sensor = sensor_params.copy()
        sensor['status'] = "Ignored"  # Default status until connection check
        sensor['sensor'] = Encoder()
        sensor['sensor'].setDeviceSerialNumber(sensor_params['serial'])
        sensor['sensor'].setChannel(sensor_params['channel'])
        # sensor['sensor'].setPosition(sensor_params['initial_position'])
        sensor['sensor'].setOnPositionChangeHandler(
            self.onPositionChangeHandler)

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
        key_list = ['id', 'name', 'read_data',
                    'status', 'properties', 'config_path']
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

    def checkSensorConnection(self, sensor):
        if not sensor['read_data']:
            return False
        if sensor['sensor'].getAttached():
            return False

        try:
            sensor['sensor'].openWaitForAttachment(
                1000)  # default value, in ms
            sensor['sensor'].setDataInterval(8)  # default value, in ms
            # FIXME Identifica también los otros canales aunque no haya sensor conectado!
            # if loadCell['input'].getSensorType() != Bridge.PHIDGET_BRIDGE_SENSOR_TYPE_NONE:
            #     loadCell['status'] = "Active"
            #     self.phidget_sensor_connected = True
            # Close communication until start process
            sensor['status'] = "Active"
            sensor['sensor'].close()
            # print(loadCell['input'].getSensorType())
        except (PhidgetException):
            self.log_handler.logger.warn("Could not connect to serial " + str(
                sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
            sensor['status'] = "Disconnected"
            return False

        return True
    
    def connectSensor(self, sensor):
        if sensor['status'] != "Active":
            return
        try:
            sensor['sensor'].openWaitForAttachment(2000)  # in ms
            sensor['sensor'].setDataInterval(8)  # in ms
        except (PhidgetException):
            self.log_handler.logger.warn("Could not connect to serial " + str(
                sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))

    def disconnectSensor(self, sensor):
        if sensor['status'] != "Active":
            return
        try:
            sensor['sensor'].close()
        except (PhidgetException):
            self.log_handler.logger.error("Could not close serial " + str(
                sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))

    # Returns true if there is at least one sensor connected
    def connect(self):
        self.sensors_connected = False
        if not self.sensor_list:
            self.log_handler.logger.info(
                "No encoders added to try connection.")
            return self.sensors_connected
        sensor_connections = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensor_connections = executor.map(
                self.checkSensorConnection, self.sensor_list)

        self.sensors_connected = any(sensor_connections)
        return self.sensors_connected

    def start(self):
        if not self.sensors_connected:
            self.log_handler.logger.info(
                "Ignoring Encoders sensors in test, no one connected.")
            return
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.connectSensor, self.sensor_list)
        for sensor in self.sensor_list:
            if sensor['status'] != "Active":
                continue
            # WIP Initial value
            self.sensor_data[sensor['name']] = -1

    def stop(self):
        if not self.sensors_connected:
            return
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.disconnectSensor, self.sensor_list)
