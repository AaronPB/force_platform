import time
import handlers

from managers.configManager import ConfigManager
from enums.configPaths import ConfigPaths as CfgPaths
from src.utils import LogHandler


class TestManager:
    def __init__(self, config_mngr: ConfigManager) -> None:
        self.log_handler = LogHandler(str(__class__.__name__))

        # Initial values
        self.config_mngr = config_mngr
        self.sensors_connected = False

        # Sensor handlers
        self.sensor_handlers = [
            handlers.PhidgetLoadCellsHandler('Platform 1'),
            handlers.PhidgetLoadCellsHandler('Platform 2'),
            handlers.PhidgetEncodersHandler('Barbell Encoders'),
            handlers.TaoboticsIMUsHandler('Body IMUs')
        ]
        self.sensor_config_paths = [
            CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION,
            CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION,
            CfgPaths.PHIDGET_ENCODER_CONFIG_SECTION,
            CfgPaths.TAOBOTICS_IMU_CONFIG_SECTION
        ]

        # TODO check other needed initializers

    def importSensors(self) -> None:
        for handler, config_path in zip(self.sensor_handlers, self.sensor_config_paths):
            sensor_group = self.config_mngr.getConfigValue(config_path)
            handler.setSensorGroup(sensor_group)

    def checkConnection(self) -> bool:
        self.sensors_connected = any(
            handler.checkSensorsConnection() for handler in self.sensor_handlers)
        return self.sensors_connected

    def testStart(self) -> None:
        [handler.startSensors() for handler in self.sensor_handlers]

    def testRegisterValues(self) -> None:
        current_time = round(time.time()*1000)
        # TODO [handler.registerData() for handler in self.sensor_handlers]

    def testStop(self) -> None:
        [handler.stopSensors() for handler in self.sensor_handlers]
