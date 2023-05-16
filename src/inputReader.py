# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import yaml
import os
import time

from src.handlers.phidgetLoadCellsHandler import PhidgetLoadCellsHandler
from src.handlers.phidgetEncodersHandler import PhidgetEncodersHandler
from src.handlers.taoboticsIMUsHandler import TaoboticsIMUsHandler
from src.sensorCalibrator import SensorCalibrator
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
        self.phidgetP1LoadCellsHandler = PhidgetLoadCellsHandler("Platform1")
        self.phidgetP2LoadCellsHandler = PhidgetLoadCellsHandler("Platform2")
        self.phidgetEncodersHandler = PhidgetEncodersHandler("BarEncoders")
        self.taoboticsIMUsHandler = TaoboticsIMUsHandler("BodyIMUs")

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
        # Phidget Platform Load Cells
        self.loadSensorType(self.phidgetP1LoadCellsHandler,
                            'p1_phidget_loadcell_list')
        self.loadSensorType(self.phidgetP2LoadCellsHandler,
                            'p2_phidget_loadcell_list')
        # Phidget Encoders
        self.loadSensorType(self.phidgetEncodersHandler,
                            'phidget_encoder_list')
        # Taobotics IMUs
        self.loadSensorType(self.taoboticsIMUsHandler, 'taobotics_imu_list')

    def loadSensorType(self, type, config_list):
        if not config_list in self.config:
            self.log_handler.logger.warn(
                "Cannot find " + config_list + "in config! Ignoring list.")
            return
        type.clearSensors()
        config_list_path = self.config[config_list]
        for sensor_id in list(config_list_path.keys()):
            sensor_data = config_list_path[sensor_id].copy()
            sensor_data['id'] = sensor_id  # Add ID to dict
            type.addSensor(sensor_data)

    # Sensors connection
    def connectSensors(self):
        self.log_handler.logger.info("Connecting to specified sensors")
        self.sensor_connected = False
        self.loadSensors()
        # TODO make connections depending on loaded sensors and their type
        self.sensor_connected = any(
            [self.phidgetP1LoadCellsHandler.connect(),
             self.phidgetP2LoadCellsHandler.connect(),
             self.phidgetEncodersHandler.connect(),
             self.taoboticsIMUsHandler.connect()])
        self.log_handler.logger.info("Connection process done!")

    def getPlatform1SensorStatus(self):
        return self.phidgetP1LoadCellsHandler.getSensorListDict()

    def getPlatform2SensorStatus(self):
        return self.phidgetP2LoadCellsHandler.getSensorListDict()

    def getEncoderSensorsStatus(self):
        return self.phidgetEncodersHandler.getSensorListDict()

    def getIMUSensorStatus(self):
        return self.taoboticsIMUsHandler.getSensorListDict()

    def getReaderChecks(self):
        return [self.config_path, self.test_folder, self.test_name, self.sensor_connected]

    # Read process
    def readerStart(self):
        self.log_handler.logger.info("Starting test...")
        # Start sensors
        self.phidgetP1LoadCellsHandler.start()
        self.phidgetP2LoadCellsHandler.start()
        self.phidgetEncodersHandler.start()
        self.taoboticsIMUsHandler.start()
        # Get headers of connected sensors
        dataframe_headers = ['timestamp']
        dataframe_headers.extend(
            self.phidgetP1LoadCellsHandler.getSensorHeaders() +
            self.phidgetP2LoadCellsHandler.getSensorHeaders() +
            self.phidgetEncodersHandler.getSensorHeaders() +
            self.taoboticsIMUsHandler.getSensorHeaders())
        self.log_handler.logger.info("Test headers: " + str(dataframe_headers))
        self.sensor_dataframe = TestDataFrame(dataframe_headers)

    def readerProcess(self):
        # Get and acumulate values in dataframe from all sensor classes
        current_time = round(time.time()*1000)
        data = [current_time]
        data.extend(self.phidgetP1LoadCellsHandler.getSensorData() +
                    self.phidgetP2LoadCellsHandler.getSensorData() +
                    self.phidgetEncodersHandler.getSensorData() +
                    self.taoboticsIMUsHandler.getSensorData())
        self.sensor_dataframe.addRow(data)
        # self.log_handler.logger.debug("Clocking data! - " + str(data))
        # print(str(self.taoboticsIMUsHandler.getSensorData()))

    def readerStop(self):
        self.phidgetP1LoadCellsHandler.stop()
        self.phidgetP2LoadCellsHandler.stop()
        self.phidgetEncodersHandler.stop()
        self.taoboticsIMUsHandler.stop()
        self.log_handler.logger.info("Test finished!")
        self.sensor_dataframe.exportToCSV(os.path.join(
            self.test_folder, self.test_name + '.csv'))
        # Plot results
        single_dataframe = self.sensor_dataframe.getDataFrame().iloc[:, :2]
        preview = DataFramePlotter(single_dataframe)
        preview.plot_line('time', [single_dataframe.columns[1]])

    # Calibration process
    def prepareSensorCalibration(self, sensor_name):
        sensor_config_lists = ['p1_phidget_loadcell_list',
                               'p2_phidget_loadcell_list', 'phidget_encoder_list', 'taobotics_imu_list']
        # Search sensor id
        self.calibration_handler = None
        self.calibration_sensor_data = {}
        for config_list_path in sensor_config_lists:
            config_sensor_list = self.config[config_list_path]
            for sensor_id in list(config_sensor_list.keys()):
                if config_sensor_list[sensor_id]['name'] == sensor_name:
                    self.calibration_sensor_data = config_sensor_list[sensor_id].copy(
                    )
                    # Add ID to dict
                    self.calibration_sensor_data['id'] = sensor_id
                    print('Found it! Path: ' + str(config_list_path))
                    break
            if self.calibration_sensor_data:
                break
        if not self.calibration_sensor_data:
            return False
        if config_list_path == 'p1_phidget_loadcell_list' or config_list_path == 'p2_phidget_loadcell_list':
            self.calibration_handler = PhidgetLoadCellsHandler("Calibration")
        elif config_list_path == 'phidget_encoder_list':
            self.calibration_handler = PhidgetEncodersHandler("Calibration")
        elif config_list_path == 'taobotics_imu_list':
            self.calibration_handler = TaoboticsIMUsHandler("Calibration")
        else:
            self.calibration_handler = None
            return False

        self.calibration_handler.addSensor(self.calibration_sensor_data)
        self.calibration_handler.connect()

        self.calibrator = SensorCalibrator()
        return True

    def calibrationNewTest(self, test_value: float):
        if not self.calibration_handler:
            self.log_handler.logger.error(
                "No calibration sensor handler defined!" +
                "Call prepareSensorCalibration method before testing.")
            return
        self.calibrator.newCalibrationTest(test_value)
        self.calibration_handler.start()

    def calibrateTestProcess(self):
        if not self.calibration_handler:
            self.log_handler.logger.error(
                "No calibration sensor handler defined!" +
                "Call prepareSensorCalibration method before testing.")
            return
        self.calibrator.addTestMeasurement(
            self.calibration_handler.getSensorData()[0])

    def getCalibrateTestResults(self):
        if not self.calibration_handler:
            self.log_handler.logger.error(
                "No calibration sensor handler defined!" +
                "Call prepareSensorCalibration method before testing.")
            return None, None, None
        self.calibration_handler.stop()
        return self.calibrator.getTestResults()
    
    def getCalibrateRegressionResults(self):
        if not self.calibration_handler:
            self.log_handler.logger.error(
                "No calibration sensor handler defined!" +
                "Call prepareSensorCalibration method before testing.")
            return None, None, None
        return self.calibrator.getCalibrationResults()
