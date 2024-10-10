# -*- coding: utf-8 -*-

import time
import threading

from src.handlers.sensorGroup import SensorGroup, Sensor

from loguru import logger


class TestManager:
    __test__ = False

    def __init__(self) -> None:
        self.available_sensors: dict[str, Sensor] = {}
        self.test_times: list[int] = []
        self.test_running: bool = False
        self.threads: list[threading.Thread] = []
        self.main_thread: threading.Thread
        self.register_event = threading.Event()

    # Setters and getters
    def getSensorConnected(self) -> bool:
        return len(self.available_sensors) > 0

    def getTestTimes(self) -> list:
        return self.test_times

    # Test methods
    def checkConnection(self, sensor_groups: list[SensorGroup]) -> None:
        if not sensor_groups:
            return
        self.available_sensors.clear()
        for group in sensor_groups:
            # Only add available sensors to the class
            if group.checkConnections():
                self.available_sensors.update(group.getSensors(only_available=True))

    def _registerData(self, sensor: Sensor) -> None:
        while self.test_running:
            self.register_event.wait()
            sensor.registerValue()

    def _registerProcess(self, interval_ms: int) -> None:
        next_time = time.time() + interval_ms / 1000.0
        while self.test_running:
            # Adjust sleep to remaining time
            time.sleep(max(0, next_time - time.time()))
            next_time += interval_ms / 1000.0

            # Register timestamp and set reading event
            self.test_times.append(round(time.time() * 1000))
            self.register_event.set()

            self.register_event.clear()

    def testStart(self, interval_ms: int = 100) -> None:
        logger.info(f"Starting test...")
        if not self.available_sensors:
            logger.warning(
                "There are no sensors connected! Please check sensor connections first."
            )
            return
        self.threads.clear()
        self.test_times.clear()
        [sensor.clearValues() for sensor in self.available_sensors.values()]
        # Connect sensors and check if all of them are available
        connected_sensors: list[Sensor] = []
        for sensor in self.available_sensors.values():
            if not sensor.connect():
                logger.error(
                    f"Sensor {sensor.getName()} of id {sensor.getID()} is not connected!!"
                    + " \n The test has been cancelled. Check connections again."
                )
                [sensor.disconnect() for sensor in connected_sensors]
                return
            connected_sensors.append(sensor)
        # Create sensor threads
        self.test_running = True
        self.register_event.clear()
        for sensor in self.available_sensors:
            thread = threading.Thread(target=self._registerData, args=[sensor])
            self.threads.append(thread)
            thread.start()
        self.main_thread = threading.Thread(
            target=self._registerProcess, args=[interval_ms]
        )
        self.main_thread.start()

    def testStop(self) -> None:
        if not self.test_running:
            logger.info("No test is running. Ignoring stop request.")
            return
        self.test_running = False
        [thread.join() for thread in self.threads]
        self.main_thread.join()
        logger.info(f"Test finished")
        [sensor.disconnect() for sensor in self.available_sensors.values()]
