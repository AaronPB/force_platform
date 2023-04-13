# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from src.utils import LogHandler


class PhidgetLoadCellsHandler:
    def __init__(self):
        self.sensor_list = []
        self.log_handler = LogHandler(str(__class__.__name__))

        def onPhidgetVoltageRatioChange(self, voltageRatio):
            print("[" + str(self.getDeviceSerialNumber()) + "_" +
                  str(self.getChannel()) + "]: " + str(voltageRatio))
        self.onPhidgetVoltageRatioChange = onPhidgetVoltageRatioChange

    def addSensor(self, sensor_params: dict):
        required_keys = ['id', 'name', 'read_data', 'serial', 'channel']
        if not all(key in sensor_params.keys() for key in required_keys):
            raise ValueError(
                "El diccionario no tiene todas las keys requeridas.")

        sensor = {}
        sensor['id'] = sensor_params['id']
        sensor['name'] = sensor_params['name']
        sensor['read_data'] = sensor_params['read_data']
        sensor['status'] = "Ignored"  # Default status until connection check
        sensor['sensor'] = VoltageRatioInput()
        sensor['sensor'].setDeviceSerialNumber(sensor_params['serial'])
        sensor['sensor'].setChannel(sensor_params['channel'])
        sensor['sensor'].setOnVoltageRatioChangeHandler(
            self.onPhidgetVoltageRatioChange)

        self.sensor_list.append(sensor)
        # self.log_handler.logger.debug("Loaded " + sensor_params['id'])

    def clearSensors(self):
        self.sensor_list.clear()

    def getSensorListDict(self):
        key_list = ['id', 'name', 'read_data', 'status']
        return [{k: sensor[k] for k in key_list} for sensor in self.sensor_list]

    # Return boolean array with connection status (true == connected)
    def connect(self):
        check_list = []
        if not self.sensor_list:
            self.log_handler.logger.info(
                "No load cells added to try connection.")
            return check_list
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
                    check_list.append(True)
                    # print(loadCell['input'].getSensorType())
                except (PhidgetException):
                    self.log_handler.logger.warn("Could not connect to serial " + str(
                        sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
                    sensor['status'] = "Disconnected"
                    check_list.append(False)
        return check_list

    def start(self):
        if not self.sensor_list:
            self.logger.info(
                "Ignoring Load Cells sensors in test, no one loaded.")
            return
        for sensor in self.sensor_list:
            try:
                sensor['sensor'].open()
            except (PhidgetException):
                self.logger.warn("Could not open serial " + str(sensor['sensor'].getDeviceSerialNumber(
                )) + ", channel " + str(sensor['sensor'].getChannel()))
                sensor['sensor'].close()

    def stop(self):
        if not self.sensor_list:
            return
        for sensor in self.sensor_list:
            try:
                sensor.close()
            except (PhidgetException):
                self.logger.error("Could not close serial " + str(
                    sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
