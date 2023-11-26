# -*- coding: utf-8 -*-

import threading
from loguru import logger
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *


class PhidgetLoadCell:
    def __init__(self, serial: int, channel: int) -> None:
        self.handler = VoltageRatioInput()
        self.handler.setDeviceSerialNumber(serial)
        self.handler.setChannel(channel)
        self.handler.setOnVoltageRatioChangeHandler(self.onVoltageRatioChange)
        self.mutex = threading.Lock()
        self.value = None

    def onVoltageRatioChange(self, handler: VoltageRatioInput, voltageRatio):
        self.mutex.acquire()
        self.value = voltageRatio
        self.mutex.release()

    def connect(self, wait_ms: int = 2000, interval_ms: int = 8) -> bool:
        try:
            self.handler.openWaitForAttachment(wait_ms)
            self.handler.setDataInterval(interval_ms)
        except PhidgetException:
            logger.warning(
                f"Could not connect to serial {self.handler.getDeviceSerialNumber()}, channel {self.handler.getChannel()}"
            )
            return False
        return True

    def disconnect(self) -> None:
        try:
            self.handler.close()
        except PhidgetException:
            logger.error(
                f"Could not disconnect serial {self.handler.getDeviceSerialNumber()}, channel {self.handler.getChannel()}"
            )

    def getValue(self):
        self.mutex.acquire()
        value = self.value
        self.mutex.release()
        return value
