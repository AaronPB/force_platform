# -*- coding: utf-8 -*-

import threading
from Phidget22.Phidget import *
from Phidget22.Devices.Encoder import *


# TODO replace prints to log_handler
class PhidgetEncoder:
    def __init__(self, serial: int, channel: int) -> None:
        self.handler = Encoder()
        self.handler.setDeviceSerialNumber(serial)
        self.handler.setChannel(channel)
        self.handler.setOnPositionChangeHandler(self.onPositionChange)
        self.mutex = threading.Lock()
        self.value = None

    def onPositionChange(self, handler: Encoder, positionChange):
        self.mutex.acquire()
        self.value = positionChange
        self.mutex.release()

    def connect(self, wait_ms: int = 2000, interval_ms: int = 8) -> bool:
        try:
            self.handler.openWaitForAttachment(wait_ms)
            self.handler.setDataInterval(interval_ms)
        except (PhidgetException):
            print(
                f'Could not connect to serial {self.handler.getDeviceSerialNumber()}, channel {self.handler.getChannel()}')
            return False
        return True

    def disconnect(self) -> None:
        try:
            self.handler.close()
        except (PhidgetException):
            print(
                f'Could not disconnect serial {self.handler.getDeviceSerialNumber()}, channel {self.handler.getChannel()}')

    def getValue(self):
        self.mutex.acquire()
        value = self.value
        self.mutex.release()
        return value
