# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import yaml
import os
import time

from src.phidgetLoadCellsHandler import PhidgetLoadCellsHandler
from src.taoboticsIMUsHandler import TaoboticsIMUsHandler
from src.utils import LogHandler, TestDataFrame, DataFramePlotter


class InputReader:
    def __init__(self):
        self.log_handler = LogHandler(str(__class__.__name__))

        # Initial values
        self.config_path = False
        self.test_folder = False
        self.test_name = False
        self.sensor_connected = False

        # Init sensor handlers
        self.phidgetLoadCellsHandler = PhidgetLoadCellsHandler()
        self.taoboticsIMUsHandler = TaoboticsIMUsHandler()

        # Load config
        self.config_path = os.path.join(
            os.path.dirname(__file__), '..', 'config.yaml')
        self.configLoad()
        if 'custom_config_path' in self.config:
            self.config_path = os.path.join(self.config['custom_config_path'])
            if os.path.exists(self.config_path):
                print('Loading custom file: ' + self.config_path)
                self.configLoad()
            else:
                print('Could not find custom config file: ' +
                      self.config_path + '.\nDefault config has been loaded.')
        self.configLoadParams()

    # Config methods
    def configLoad(self):
        with open(self.config_path, "r") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

    def configSave(self):
        with open(self.config_path, "w") as file:
            yaml.dump(self.config, file, sort_keys=False)

    def configEdit(self, keyPath, value):
        keys = keyPath.split('.')
        currentDict = self.config
        for key in keys[:-1]:
            currentDict = currentDict[key]
        currentDict[keys[-1]] = value
        self.configSave()

    def configLoadParams(self):
        self.loadFiles()
        self.loadSensors()

    def loadFiles(self):
        # Check test path and test name
        self.test_folder = ""
        self.test_name = ""
        if 'folder' in self.config['test_options']:
            if os.path.isdir(self.config['test_options']['folder']):
                self.test_folder = os.path.join(
                    self.config['test_options']['folder'])
        if 'name' in self.config['test_options']:
            self.test_name = self.config['test_options']['name']

    # Filter config sensor lists
    def loadSensors(self):
        # Phidget Sensors
        if 'p1_phidget_loadcell_list' in self.config:
            self.phidgetLoadCellsHandler.clearSensors()
            config_list_path = self.config['p1_phidget_loadcell_list']
            for sensor_id in list(config_list_path.keys()):
                sensor_data = config_list_path[sensor_id].copy()
                sensor_data['id'] = sensor_id  # Add ID to dict
                self.phidgetLoadCellsHandler.addSensor(sensor_data)
        # Taobotics IMUs
        if 'taobotics_imu_list' in self.config:
            self.taoboticsIMUsHandler.clearSensors()
            config_list_path = self.config['taobotics_imu_list']
            for sensor_id in list(config_list_path.keys()):
                sensor_data = config_list_path[sensor_id].copy()
                sensor_data['id'] = sensor_id  # Add ID to dict
                self.taoboticsIMUsHandler.addSensor(sensor_data)
        # TODO put more sensor types when defined

    # Sensors connection
    def connectSensors(self):
        self.log_handler.logger.info("Connecting to specified sensors")
        self.sensor_connected = False
        self.loadSensors()
        # TODO make connections depending on loaded sensors and their type
        self.sensor_connected = any(
            [self.phidgetLoadCellsHandler.connect(), self.taoboticsIMUsHandler.connect()])
        self.log_handler.logger.info("Connection process done!")

    def getSensorStatus(self):
        sensorStatus = self.phidgetLoadCellsHandler.getSensorListDict()
        # TODO taobotics imus
        return sensorStatus

    def getReaderChecks(self):
        return [self.config_path, self.test_folder, self.test_name, self.sensor_connected]

    # Read process
    def readerStart(self):
        self.log_handler.logger.info("Starting test...")
        # Start sensors
        self.phidgetLoadCellsHandler.start()
        self.taoboticsIMUsHandler.start()
        # Get headers of connected sensors
        dataframe_headers = ['timestamp']
        dataframe_headers.extend(
            self.phidgetLoadCellsHandler.getSensorHeaders() + self.taoboticsIMUsHandler.getSensorHeaders())
        self.log_handler.logger.info("Test headers: " + str(dataframe_headers))
        self.sensor_dataframe = TestDataFrame(dataframe_headers)

    def readerProcess(self):
        # Get and acumulate values in dataframe from all sensor classes
        current_time = round(time.time()*1000)
        data = [current_time]
        data.extend(self.phidgetLoadCellsHandler.getSensorData() +
                    self.taoboticsIMUsHandler.getSensorData())
        self.sensor_dataframe.addRow(data)
        # self.log_handler.logger.debug("Clocking data! - " + str(data))
        # print(str(self.taoboticsIMUsHandler.getSensorData()))

    def readerStop(self):
        self.phidgetLoadCellsHandler.stop()
        self.taoboticsIMUsHandler.stop()
        self.log_handler.logger.info("Test finished!")
        self.sensor_dataframe.exportToCSV(os.path.join(
            self.test_folder, self.test_name + '.csv'))
        # Plot results
        # preview = DataFramePlotter(self.sensor_dataframe.getDataFrame())
        # preview.plot_line('time', [
        #                   self.phidgetLoadCellsHandler.getSensorHeaders()])
