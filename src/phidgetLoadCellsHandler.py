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
    def __init__(self):
        self.log_handler = LogHandler(str(__class__.__name__))
        self.sensor_list = []
        self.sensor_data = {}
        self.sensor_data_mutex = threading.Lock()

        def onVoltageRatioChange(self,
                                 voltageRatio,
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
                    connected_sensor = True
            if not connected_sensor:
                return
            weight = voltageRatio * m + b

            # log_handler.logger.debug("[" + str(serial) + "_" +
            #                          str(channel) + "]: " + str(voltageRatio) + " V (" + str(weight) + " kg)")

            mutex.acquire()
            sensor_data[(serial, channel)] = weight
            mutex.release()

        self.onVoltageRatioChange = onVoltageRatioChange

    def addSensor(self, sensor_params: dict):
        required_keys = ['id', 'name', 'read_data',
                         'serial', 'channel', 'calibration_data']
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
        # self.log_handler.logger.debug("Loaded " + sensor_params['id'])

    def clearSensors(self):
        self.sensor_list.clear()

    def getSensorListDict(self):
        key_list = ['id', 'name', 'read_data', 'status']
        return [{k: sensor[k] for k in key_list} for sensor in self.sensor_list]
    
    def getSensorData(self):
        return [self.sensor_data[tuple] for tuple in self.sensor_data]

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
        sensor_headers = []
        if not self.sensors_connected:
            self.logger.info(
                "Ignoring Load Cells sensors in test, no one connected.")
            return sensor_headers
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue
            try:
                sensor['sensor'].open()
                sensor_headers.append(sensor['name'])
            except (PhidgetException):
                self.logger.warn("Could not open serial " + str(sensor['sensor'].getDeviceSerialNumber(
                )) + ", channel " + str(sensor['sensor'].getChannel()))
                sensor['sensor'].close()
        return sensor_headers

    def stop(self):
        if not self.sensors_connected:
            return
        for sensor in self.sensor_list:
            if not sensor['read_data']:
                continue
            try:
                sensor['sensor'].close()
            except (PhidgetException):
                self.logger.error("Could not close serial " + str(
                    sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
