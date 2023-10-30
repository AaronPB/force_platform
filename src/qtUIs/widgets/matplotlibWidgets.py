import numpy as np
import matplotlib.patches as patches
import math
from PySide6 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.handlers.sensorGroup import SensorGroup


class PlotPlatformForcesWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str):
        super(PlotPlatformForcesWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.group_name = group_name

        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312, sharex=self.ax1)
        self.ax3 = self.figure.add_subplot(313, sharex=self.ax1)

        self.setup()

    def setup(self):
        # TODO set name of sensor group
        self.ax1.set_title(f'Forces - {self.group_name}')
        self.ax1.set_ylabel('Forces Z (kg)')
        self.ax2.set_ylabel('Forces X (kg)')
        self.ax3.set_ylabel('Forces Y (kg)')
        self.ax3.set_xlabel('Time (s)')
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.grid(True)
            ax.plot(0, 0)
        self.canvas.draw()

    def update(self, timestamp_list: list):
        # TODO
        np_time = np.array(timestamp_list)
        np_time_incr = np.diff(np_time)

        data_dict = self.sensor_group.getGroupValues()
        calib_dict = self.sensor_group.getGroupCalibrationParams()

        pass

    def clear(self):
        self.setup()


class PlotPlatformCOPWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str):
        super(PlotPlatformCOPWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.group_name = group_name

        self.ax = self.figure.add_subplot()

        self.setup()

    def setup(self):
        # TODO set name of sensor group
        self.ax.set_title(f'COP - {self.group_name}')
        self.ax.set_xlabel('Medio-Lateral Motion (mm)')
        self.ax.set_ylabel('Anterior-Posterior Motion (mm)')
        self.ax.grid(True)
        self.ax.plot(0, 0)

        # Platform rectangle patch (mm)
        x_len = 600
        y_len = 400
        rectangle = patches.Rectangle(
            (-x_len/2, -y_len/2), x_len, y_len, edgecolor='blue', facecolor='none')
        self.ax.add_patch(rectangle)

        # Last pose circle
        self.circle = patches.Circle(
            (0, 0), 6, edgecolor='#326295', facecolor='white', linewidth=2.0)
        self.ax.add_patch(self.circle)

        self.canvas.draw()

    def update(self, timestamp_list: list):
        # TODO
        np_time = np.array(timestamp_list)
        np_time_incr = np.diff(np_time)

        data_dict = self.sensor_group.getGroupValues()
        calib_dict = self.sensor_group.getGroupCalibrationParams()

        pass

    def clear(self):
        self.setup()


class PlotEncoderWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str, group_size: int):
        super(PlotEncoderWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.group_name = group_name
        self.group_size = group_size
        self.subplots = []

        self.setup()

    def setup(self):
        self.createSubplots(self.group_size)
        self.canvas.draw()

    def createSubplots(self, total_subplots: int = 4):
        # TODO iterate over group sensor info
        for i in range(total_subplots):
            ax = self.figure.add_subplot(math.ceil(total_subplots/2), 2, i+1)
            ax.plot(0, 0)
            ax.grid(True)
            ax.set_title('Encoder n')
            # ax.set_xlabel('Time(s)')
            ax.set_ylabel('Angles (deg)')
            self.subplots.append(ax)

    def update(self, timestamp_list: list):
        # TODO
        np_time = np.array(timestamp_list)
        np_time_incr = np.diff(np_time)

        data_dict = self.sensor_group.getGroupValues()
        calib_dict = self.sensor_group.getGroupCalibrationParams()

        pass

    def clear(self):
        self.setup()


class PlotIMUWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str, group_size: int):
        super(PlotIMUWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.group_name = group_name
        self.group_size = group_size
        self.subplots = []

        self.setup()

    def setup(self):
        # TODO get total amount of sensors in group
        self.createSubplots(self.group_size)
        self.canvas.draw()

    def createSubplots(self, total_subplots: int = 4):
        # TODO iterate over group sensor info
        for i in range(total_subplots):
            ax = self.figure.add_subplot(math.ceil(total_subplots/2), 2, i+1)
            ax.plot(0, 0)
            ax.grid(True)
            ax.set_title('IMU n')
            # ax.set_xlabel('Time(s)')
            ax.set_ylabel('Angles (deg)')
            self.subplots.append(ax)

    def update(self, timestamp_list: list):
        # TODO
        np_time = np.array(timestamp_list)
        np_time_incr = np.diff(np_time)

        data_dict = self.sensor_group.getGroupValues()
        calib_dict = self.sensor_group.getGroupCalibrationParams()

        pass

    def clear(self):
        self.setup()
