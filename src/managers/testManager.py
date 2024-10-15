# -*- coding: utf-8 -*-

import time
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor

from src.managers.sensorManager import SensorManager
from src.handlers.sensorGroup import SensorGroup, Sensor
from src.enums.sensorTypes import STypes

from loguru import logger


class TestManager:
    __test__ = False

    def __init__(self) -> None:
        self.available_sensors: dict[str, Sensor] = {}
        self.test_times: list[int] = []
        self.test_running: bool = False
        self.main_thread: threading.Thread
        self.register_barrier: threading.Barrier
        self.threads_executor: ThreadPoolExecutor

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
            self.register_barrier.wait()
            sensor.registerValue()

    def _registerTime(self) -> None:
        self.test_times.append(round(time.time() * 1000))

    def _registerProcess(self, interval_ms: int) -> None:
        next_time = time.time() + interval_ms / 1000.0
        while self.test_running:
            # Adjust sleep to remaining time
            time.sleep(max(0, next_time - time.time()))
            next_time += interval_ms / 1000.0

            # Register timestamp and set reading event
            try:
                self.register_barrier.wait()
            except threading.BrokenBarrierError:
                # May be triggered if main thread is waiting
                break
        self.threads_executor.shutdown()

    def testStart(self, interval_ms: int) -> None:
        logger.info(f"Starting test...")
        if not self.available_sensors:
            logger.warning(
                "There are no sensors connected! Please check sensor connections first."
            )
            return
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
        self.register_barrier = threading.Barrier(
            parties=len(self.available_sensors) + 1,
            action=self._registerTime,
            timeout=3,
        )
        self.threads_executor = ThreadPoolExecutor(
            max_workers=len(self.available_sensors)
        )
        for sensor in self.available_sensors.values():
            self.threads_executor.submit(self._registerData, sensor)
        self.main_thread = threading.Thread(
            target=self._registerProcess, args=[interval_ms]
        )
        self.main_thread.start()

    def testStop(self) -> None:
        if not self.test_running:
            logger.warning(
                "No test is running but stop request has been called!"
                + "Please check possible errors."
            )
        self.test_running = False
        self.main_thread.join()
        logger.info(f"Test finished")
        [sensor.disconnect() for sensor in self.available_sensors.values()]
        logger.debug("Recorded values size:")
        logger.debug(len(self.test_times))
        logger.debug(
            [len(sensor.getValues()) for sensor in self.available_sensors.values()]
        )

    # Tare methods

    def _tareProcess(
        self, sensor_manager: SensorManager, last_values: int, waiting_time: float
    ) -> None:
        logger.info(
            f"Starting sensor tare. Reading sensors for {waiting_time:.2f} seconds..."
        )
        # Wait to get the required values
        time.sleep(waiting_time)
        logger.info("Taring sensors...")
        tared_sensors_counter = 0
        for sensor in self.available_sensors.values():
            # Only tare loadcells and encoders
            if sensor.getType() not in [
                STypes.SENSOR_LOADCELL,
                STypes.SENSOR_ENCODER,
            ]:
                continue
            # Tare process
            logger.debug(f"Tare sensor {sensor.getName()}")
            slope = sensor.getSlope()
            intercept = sensor.getIntercept()
            calib_values = [
                value * slope + intercept for value in sensor.getValues()[-last_values:]
            ]
            new_intercept = float(sensor.getIntercept() - np.mean(calib_values))
            logger.debug(f"From {intercept} to {new_intercept}")
            sensor_manager.setSensorIntercept(sensor, new_intercept)
            tared_sensors_counter += 1
        logger.info(f"Tare finished! {tared_sensors_counter} sensors has been tared.")

    def tareSensors(
        self, sensor_mngr: SensorManager, tare_amount: int, interval_ms: int
    ) -> None:
        waiting_time = float(tare_amount * interval_ms / 1000)
        tare_thread = threading.Thread(
            target=self._tareProcess, args=[sensor_mngr, tare_amount, waiting_time]
        )
        tare_thread.start()
