# -*- coding: utf-8 -*-

from loguru import logger
from mrpt.pymrpt import mrpt


class TaoboticsIMU:
    def __init__(self, serial: int, channel: int = None) -> None:
        self.serial = serial
        self.value_list = []

        self.setHandler()

    def setHandler(self):
        if hasattr(self, "handler"):
            del self.handler
        self.handler = mrpt.hwdrivers.CTaoboticsIMU()
        self.handler.setSerialPort(self.serial)

    def connect(self, wait_ms: int = 2000, interval_ms: int = 8) -> bool:
        try:
            self.handler.initialize()
        except Exception:
            logger.warning(f"Could not connect to serial {self.serial}")
            return False
        return (
            self.handler.getState()
            == mrpt.hwdrivers.CGenericSensor.TSensorState.ssWorking
        )

    def disconnect(self) -> None:
        self.setHandler()

    def getValue(self):
        if (
            self.handler.getState()
            != mrpt.hwdrivers.CGenericSensor.TSensorState.ssWorking
        ):
            return self.value_list

        self.handler.doProcess()
        obs_list = self.handler.getObservations()

        if obs_list.empty():
            return self.value_list

        q_x = q_y = q_z = q_w = -1
        w_x = w_y = w_z = -1
        x_acc = y_acc = z_acc = -1
        for t, obs in obs_list:
            # Quaternions
            q_x = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_X)
            q_y = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_Y)
            q_z = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_Z)
            q_w = obs.get(mrpt.obs.TIMUDataIndex.IMU_ORI_QUAT_W)
            # Angular velocities
            w_x = obs.get(mrpt.obs.TIMUDataIndex.IMU_WX)
            w_y = obs.get(mrpt.obs.TIMUDataIndex.IMU_WY)
            w_z = obs.get(mrpt.obs.TIMUDataIndex.IMU_WZ)
            # Accelerations
            x_acc = obs.get(mrpt.obs.TIMUDataIndex.IMU_X_ACC)
            y_acc = obs.get(mrpt.obs.TIMUDataIndex.IMU_Y_ACC)
            z_acc = obs.get(mrpt.obs.TIMUDataIndex.IMU_Z_ACC)

        self.value_list = [q_x, q_y, q_z, q_w, w_x, w_y, w_z, x_acc, y_acc, z_acc]

        return self.value_list
