# -*- coding: utf-8 -*-

import threading
from loguru import logger
from Phidget22.Phidget import *
from Phidget22.Devices.Encoder import *


class PhidgetEncoder:
    def __init__(self, serial: int, channel: int) -> None:
        self.handler = Encoder()
        self.handler.setDeviceSerialNumber(serial)
        self.handler.setChannel(channel)
        self.handler.setOnPositionChangeHandler(self.onPositionChange)
        self.mutex = threading.Lock()
        self.value: float = 0

    def onPositionChange(
        self, handler: Encoder, positionChange, timeChange, indexTriggered
    ):
        self.mutex.acquire()
        self.value += positionChange
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
