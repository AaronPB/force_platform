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
from src.utils import LogHandler, TestDataFrame, DataFramePlotter, StabilogramPlotter


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
        self.loadGeneralSettings()
        self.loadSensors()

    def loadGeneralSettings(self):
        # TODO config format check
        general_settings_path = self.config['general_settings']
        # Get test and calibration times
        self.QT_times_dict = {}
        # Default values (all in ms)
        self.QT_times_dict['calibration_interval'] = 10
        self.QT_times_dict['calibration_time'] = 2000
        self.QT_times_dict['test_interval'] = 10
        self.QT_times_dict['test_tare_time'] = 3000
        calibration_times_path = general_settings_path['calibration_times']
        if 'data_interval_ms' in calibration_times_path:
            self.QT_times_dict['calibration_interval'] = calibration_times_path['data_interval_ms']
        if 'recording_time' in calibration_times_path:
            self.QT_times_dict['calibration_time'] = calibration_times_path['recording_time']
        test_times_path = general_settings_path['test_times']
        if 'data_interval_ms' in test_times_path:
            self.QT_times_dict['test_interval'] = test_times_path['data_interval_ms']
        if 'tare_time_ms' in test_times_path:
            self.QT_times_dict['test_tare_time'] = test_times_path['tare_time_ms']

        # Check test path and test name
        self.test_folder = ""
        self.test_name = ""
        test_file_path = general_settings_path['test_file_path']
        if 'folder' in test_file_path:
            if os.path.isdir(test_file_path['folder']):
                self.test_folder = os.path.join(test_file_path['folder'])
        if 'name' in test_file_path:
            self.test_name = test_file_path['name']

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
            sensor_data['config_path'] = str(
                config_list) + '.' + str(sensor_id)  # Add config path to dict
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

    def getTestInterval(self):
        return self.QT_times_dict['test_interval']
    
    def getTestTareTime(self):
        return self.QT_times_dict['test_tare_time']
    
    def getCalibrationInterval(self):
        return self.QT_times_dict['calibration_interval']
    
    def getCalibrationTime(self):
        return self.QT_times_dict['calibration_time']
    
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

    # == READ PROCESS
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
        self.sensor_dataframe_raw = TestDataFrame(dataframe_headers)

    def readerProcess(self):
        # Get and acumulate values in dataframe from all sensor classes
        current_time = round(time.time()*1000)
        data = [current_time]
        data_raw = [current_time]
        data.extend(self.phidgetP1LoadCellsHandler.getSensorData() +
                    self.phidgetP2LoadCellsHandler.getSensorData() +
                    self.phidgetEncodersHandler.getSensorData() +
                    self.taoboticsIMUsHandler.getSensorData())
        data_raw.extend(self.phidgetP1LoadCellsHandler.getSensorDataRaw() +
                        self.phidgetP2LoadCellsHandler.getSensorDataRaw() +
                        self.phidgetEncodersHandler.getSensorDataRaw() +
                        self.taoboticsIMUsHandler.getSensorData())
        self.sensor_dataframe.addRow(data)
        self.sensor_dataframe_raw.addRow(data_raw)
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
        self.sensor_dataframe_raw.exportToCSV(os.path.join(
            self.test_folder, self.test_name + '_RAW' + '.csv'))
        # WIP Plot results
        plot_columns = [0, 1, 2, 3, 4]
        plot_dataframe = self.sensor_dataframe.getDataFrame(
        ).iloc[:, plot_columns].copy()
        print(plot_dataframe)
        preview = DataFramePlotter(plot_dataframe)
        preview.plot_line('time', plot_dataframe.columns[1:])

    # Return fixed format of:
    # - Relative COP of Platform 1
    # - Relative COP of Platform 2
    # - TODO IMU values
    def getPlotterData(self):
        x_cop_p1 = y_cop_p1 = 0
        x_cop_p2 = y_cop_p2 = 0
        ankle_angle = thigh_angle = trunk_angle = 0

        sensor_dataframe = self.sensor_dataframe.getDataFrame()
        dataframe_size = sensor_dataframe.shape[1]
        if dataframe_size < 13:
            self.log_handler.logger.warn(
                "Ignoring relative COP values because the sensor dataframe has "
                + str(dataframe_size) + " instead of minimum 13.")
            return [x_cop_p1, y_cop_p1, x_cop_p2, y_cop_p2, ankle_angle, thigh_angle, trunk_angle]

        # Get relative COPs for both platforms
        if len(self.phidgetP1LoadCellsHandler.getSensorHeaders()) == 12:
            sensor_cols = self.phidgetP1LoadCellsHandler.getSensorHeaders()
            sensor_cols.insert(0, 'timestamp')
            stabilogram_p1 = StabilogramPlotter(
                sensor_dataframe[sensor_cols].copy())
            x_cop_p1, y_cop_p1 = stabilogram_p1.getPlotValues()
        if len(self.phidgetP2LoadCellsHandler.getSensorHeaders()) == 12:
            sensor_cols = self.phidgetP2LoadCellsHandler.getSensorHeaders()
            sensor_cols.insert(0, 'timestamp')
            stabilogram_p2 = StabilogramPlotter(
                sensor_dataframe[sensor_cols].copy())
            x_cop_p2, y_cop_p2 = stabilogram_p2.getPlotValues()
        # Get IMU values
        if len(self.taoboticsIMUsHandler.getSensorHeaders()) > 0:
            # TODO process
            pass

        return [x_cop_p1, y_cop_p1, x_cop_p2, y_cop_p2, ankle_angle, thigh_angle, trunk_angle]

    # == TARE PROCESS
    def tareApply(self, timestamp_init, timestamp_end):
        # Set new offset to all sensors and safe new intercept values in config
        mean_values_dict = self.sensor_dataframe.getIntervalMeanData(
            timestamp_init, timestamp_end)
        self.log_handler.logger.debug(
            "Mean values list: \n" + str(mean_values_dict))
        self.phidgetP1LoadCellsHandler.tareSensors(mean_values_dict)
        self.phidgetP2LoadCellsHandler.tareSensors(mean_values_dict)
        self.phidgetEncodersHandler.tareSensors(mean_values_dict)

    # == CALIBRATION PROCESS
    def prepareSensorCalibration(self, sensor_name):
        sensor_config_lists = ['p1_phidget_loadcell_list',
                               'p2_phidget_loadcell_list',
                               'phidget_encoder_list',
                               'taobotics_imu_list']
        # Search sensor id
        self.calibration_handler = None
        self.reference_calibration_handler = None
        self.reference_calibration_available = False
        self.calibration_sensor_data = {}
        for config_list_path in sensor_config_lists:
            config_sensor_list = self.config[config_list_path]
            for sensor_id in list(config_sensor_list.keys()):
                if config_sensor_list[sensor_id]['name'] == sensor_name:
                    self.calibration_sensor_data = config_sensor_list[sensor_id].copy(
                    )
                    # Add ID and path to dict
                    self.calibration_sensor_data['id'] = sensor_id
                    self.calibration_sensor_data['config_path'] = config_list_path + \
                        '.' + sensor_id
                    break
            if self.calibration_sensor_data:
                break
        if not self.calibration_sensor_data:
            return False
        if config_list_path == 'p1_phidget_loadcell_list' or config_list_path == 'p2_phidget_loadcell_list':
            self.calibration_handler = PhidgetLoadCellsHandler("Calibration")
            self.reference_calibration_handler = PhidgetLoadCellsHandler(
                "Reference Calibration")
        elif config_list_path == 'phidget_encoder_list':
            self.calibration_handler = PhidgetEncodersHandler("Calibration")
            self.reference_calibration_handler = PhidgetEncodersHandler(
                "Reference Calibration")
        elif config_list_path == 'taobotics_imu_list':
            self.calibration_handler = TaoboticsIMUsHandler("Calibration")
            self.reference_calibration_handler = TaoboticsIMUsHandler(
                "Reference Calibration")
        else:
            return False

        # Add sensor that is beaing calibrated and the reference if it is defined in config
        self.calibration_handler.addSensor(self.calibration_sensor_data)
        if 'calibration_sensor' in self.config:
            reference_sensor_data = self.config['calibration_sensor'].copy()
            reference_sensor_data['id'] = 'calibration_sensor'
            reference_sensor_data['config_path'] = 'calibration_sensor'
            self.reference_calibration_handler.addSensor(reference_sensor_data)
            self.reference_calibration_available = self.reference_calibration_handler.connect()
        if not self.calibration_handler.connect():
            return False

        # Init calibration class and start sensor reading
        self.calibrator = SensorCalibrator()
        self.calibration_handler.start()
        if self.reference_calibration_available:
            self.reference_calibration_handler.start()
        return True

    def calibrationNewTest(self, test_value: float = None):
        self.calibrator.newCalibrationTest(test_value)

    def calibrateTestProcess(self):
        sensor_data_raw = self.calibration_handler.getSensorDataRaw()
        if not sensor_data_raw:
            return
        reference_sensor_data = None
        if self.reference_calibration_available:
            reference_sensor_data = self.reference_calibration_handler.getSensorData()[
                0]
        self.calibrator.addTestMeasurement(
            sensor_data_raw[0], reference_sensor_data)

    def isCalibrationReferenceConnected(self):
        return self.reference_calibration_available

    def getCalibrateTestResults(self):
        return self.calibrator.getTestResults()

    def getCalibrateRegressionResults(self):
        return self.calibrator.getCalibrationResults()

    def calibrateTestStop(self):
        self.calibration_handler.stop()
        self.reference_calibration_handler.stop()
