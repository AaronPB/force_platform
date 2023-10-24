# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import threading
import concurrent.futures
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from enums.sensorParams import SensorParams as SParams
from enums.sensorStatus import SensorStatus as SStatus
from src.utils import LogHandler


class PhidgetLoadCellsHandler:
    def __init__(self, group_name: str) -> None:
        self.group_name = group_name
        self.log_handler = LogHandler(
            str(__class__.__name__ + '-' + self.group_name))

        self.sensor_data = {}
        # TODO self.dataframe = None
        self.sensor_data_mutex = threading.Lock()

    def onVoltageRatioChange(self, sensor_id: str):
        def handler(vontageRatio):
            self.sensor_data_mutex.acquire()
            self.sensor_data[sensor_id][SParams.VALUE] = vontageRatio
            self.sensor_data_mutex.release()
        return handler

    def setSensorGroup(self, sensor_group_dict: dict) -> bool:
        if not sensor_group_dict:
            self.log_handler.logger.warn('The sensor group is empty.')
            return False

        self.sensor_data.clear()
        required_keys = [SParams.NAME, SParams.CHANNEL,
                         SParams.SERIAL, SParams.READ]
        for sensor_id, sensor_dict in sensor_group_dict:
            self.storeSensor(sensor_id, sensor_dict, required_keys)
        return bool(self.sensor_data)

    def storeSensor(self, sensor_id: str, sensor_dict: dict, required_keys: list) -> None:
        if not all(key in sensor_dict.keys() for key in required_keys):
            self.log_handler.logger.error(
                f'Sensor {sensor_id} does not have the required keys!')
            return

        sensor = sensor_dict.copy()
        # Default status until connection check
        sensor['status'] = SStatus.IGNORED
        sensor['sensor'] = VoltageRatioInput(
            device_serial_number=sensor[SParams.SERIAL],
            channel=sensor[SParams.CHANNEL],
            on_voltage_ratio_change=self.onVoltageRatioChange(sensor_id)
        )

        self.sensor_data[sensor_id] = sensor

    def connectSensor(self, sensor: dict) -> bool:
        if not sensor[SParams.READ]:
            return False
        try:
            sensor[SParams.SENSOR].openWaitForAttachment(2000)
            sensor[SParams.SENSOR].setDataInterval(8)
            sensor[SParams.STATUS] = SStatus.AVAILABLE
        except (PhidgetException):
            self.log_handler.logger.warn("Could not connect to serial " + str(
                sensor['sensor'].getDeviceSerialNumber()) + ", channel " + str(sensor['sensor'].getChannel()))
            sensor[SParams.STATUS] = SStatus.NOT_FOUND
            return False
        return True

    def disconnectSensor(self, sensor: dict) -> None:
        if not sensor[SParams.READ]:
            return
        if sensor[SParams.STATUS] != SStatus.AVAILABLE:
            return

    def checkConnections(self) -> bool:
        if not self.sensor_data:
            self.log_handler.logger.warn(
                'The sensor group is empty. Ignore connection check.')
            return False
        sensor_connections = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensor_connections = executor.map(
                self.connectSensor, self.sensor_data)
            executor.map(self.disconnectSensor, self.sensor_data)
        return any(sensor_connections)

    def startSensors(self) -> None:
        if not self.sensor_data:
            self.log_handler.logger.warn(
                'The sensor group is empty. Ignore start.')
            return
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensor_connections = executor.map(
                self.connectSensor, self.sensor_data)
        # TODO dataframe  and tare management

    def stopSensors(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.disconnectSensor, self.sensor_data)
