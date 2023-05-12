# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 12/05/2023
"""

import threading
from Phidget22.Phidget import *
from Phidget22.Devices.Encoder import *
from src.utils import LogHandler


class PhidgetEncodersHandler:
    def __init__(self, sensor_set_name):
        self.log_handler = LogHandler(
            str(__class__.__name__ + '-' + sensor_set_name))
        self.sensor_list = []
        self.sensor_data = {}
        self.sensor_data_mutex = threading.Lock()

        def onPositionChangeHandler(self,
                                    positionChange, timeChange, indexTriggered,
                                    mutex: threading.Lock() = self.sensor_data_mutex,
                                    sensor_list: list = self.sensor_list,
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
            distance = positionChange  # * m + b

            # log_handler.logger.debug("[" + str(serial) + "_" +
            #                          str(channel) + "]: " + str(positionChange) + " pos " +
            #                          str(timeChange) + " millis " + str(indexTriggered) + " trigger (" +
            #                          str(distance) + " N)")

            mutex.acquire()
            sensor_data[name] = distance
            mutex.release()

        self.onPositionChangeHandler = onPositionChangeHandler

    def addSensor(self, sensor_params: dict):
        required_keys = ['id', 'name', 'read_data',
                         'serial', 'channel', 'calibration_data', 'initial_position']
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

    def getSensorListDict(self):
        key_list = ['id', 'name', 'read_data', 'status']
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

    # Returns true if there is at least one sensor connected
    def connect(self):
        self.sensors_connected = False
        if not self.sensor_list:
            self.log_handler.logger.info(
                "No encoders added to try connection.")
            return self.sensors_connected
        for sensor in self.sensor_list:
            if not sensor['sensor'].getAttached() and sensor['read_data']:
                try:
                    sensor['sensor'].openWaitForAttachment(2000)  # in ms
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
                "Ignoring Encoders sensors in test, no one connected.")
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
            # WIP Initial value
            self.sensor_data[sensor['name']] = -1

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
