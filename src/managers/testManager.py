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
        self.register_barrier: threading.Barrier

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

    def _registerTime(self) -> None:
        self.test_times.append(round(time.time() * 1000))

    def _registerData(self, sensor: Sensor, start_event: threading.Event) -> None:
        start_event.wait()
        while self.test_running:
            sensor.registerValue()
            try:
                self.register_barrier.wait()
            except threading.BrokenBarrierError:
                logger.warning(
                    f"Sensor {sensor.getName()} of id {sensor.getID()} "
                    + "has not responded at the requested register time."
                )
                self.test_running
                break

    def testStart(self) -> None:
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
        self.register_barrier = threading.Barrier(
            parties=len(self.available_sensors),
            action=self._registerTime,
            timeout=0.01,
        )
        start_event = threading.Event()
        self.test_running = True
        for sensor in self.available_sensors:
            thread = threading.Thread(
                target=self._registerData, args=[sensor, start_event]
            )
            self.threads.append(thread)
            thread.start()
        self._registerTime()    # Register initial timestamp
        start_event.set()       # Start all threads
        # TODO Handle BrokenBarrierError in entire test

    def testStop(self) -> None:
        if not self.test_running:
            logger.info("No test is running. Ignoring stop request.")
            return
        self.test_running = False
        [thread.join() for thread in self.threads]
        logger.info(f"Test finished")
        [sensor.disconnect() for sensor in self.available_sensors.values()]
