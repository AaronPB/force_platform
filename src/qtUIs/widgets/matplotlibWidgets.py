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

        self.lines_ax1 = []
        self.lines_ax2 = []
        self.lines_ax3 = []

        self.setup()

    def setup(self):
        self.no_lines_defined = False
        self.ax1.set_title(f"Forces - {self.group_name}")
        self.ax1.set_ylabel("Forces Z (kg)")
        self.ax2.set_ylabel("Forces X (kg)")
        self.ax3.set_ylabel("Forces Y (kg)")
        self.ax3.set_xlabel("Time (s)")
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.grid(True)
            ax.plot(0, 0)
        self.canvas.draw()

    def defineLines(self, ax, lines_ax: list, names: list):
        for name in names:
            (line,) = ax.plot(0, 0, label=name)
            lines_ax.append(line)
        (line,) = ax.plot(0, 0, label="Sum forces")
        lines_ax.append(line)
        ax.legend()
        self.no_lines_defined = True

    def update(self, timestamp_list: list, forces_data: dict = None):
        if forces_data is None:
            return
        fx_keys = [key for key in forces_data.keys() if "LoadCell_X" in key]
        fy_keys = [key for key in forces_data.keys() if "LoadCell_Y" in key]
        fz_keys = [key for key in forces_data.keys() if "LoadCell_Z" in key]

        if not self.no_lines_defined:
            self.defineLines(self.ax1, self.lines_ax1, fz_keys)
            self.defineLines(self.ax2, self.lines_ax2, fx_keys)
            self.defineLines(self.ax3, self.lines_ax3, fy_keys)

        # Invert signs when label is 1 or 4
        fx_values = [
            np.array(forces_data[key]) * -1
            if "1" in key or "4" in key
            else np.array(forces_data[key])
            for key in fx_keys
        ]
        # Invert signs when label is 1 or 2
        fy_values = [
            np.array(forces_data[key]) * -1
            if "1" in key or "2" in key
            else np.array(forces_data[key])
            for key in fy_keys
        ]
        fz_values = [np.array(forces_data[key]) for key in fz_keys]

        fx_values_np = np.array(fx_values)
        fy_values_np = np.array(fy_values)
        fz_values_np = np.array(fz_values)

        # Get resultant forces
        fx_sum = fy_sum = fz_sum = np.zeros(len(timestamp_list))
        if fx_values_np.size != 0:
            fx_sum = np.sum(fx_values_np, axis=0)
        if fy_values_np.size != 0:
            fy_sum = np.sum(fy_values_np, axis=0)
        if fz_values_np.size != 0:
            fz_sum = np.sum(fz_values_np, axis=0)

        time_incr_np = timestamp_list
        time_incr_np = np.array(
            [(t - timestamp_list[0]) / 1000 for t in timestamp_list]
        )

        i = 0
        for values in fz_values:
            self.lines_ax1[i].set_data(time_incr_np, values)
            i += 1
        self.lines_ax1[i].set_data(time_incr_np, fz_sum)

        i = 0
        for values in fx_values:
            self.lines_ax2[i].set_data(time_incr_np, values)
            i += 1
        self.lines_ax2[i].set_data(time_incr_np, fx_sum)

        i = 0
        for values in fy_values:
            self.lines_ax3[i].set_data(time_incr_np, values)
            i += 1
        self.lines_ax3[i].set_data(time_incr_np, fy_sum)

        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.relim()
            ax.autoscale_view()

        self.canvas.draw()

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
        self.ax.clear()
        self.ax.set_title(f"COP - {self.group_name}")
        self.ax.set_xlabel("Medio-Lateral Motion (mm)")
        self.ax.set_ylabel("Anterior-Posterior Motion (mm)")
        self.ax.grid(True)
        self.ax.plot(0, 0)

        # Platform rectangle patch (mm)
        x_len = 600
        y_len = 400
        rectangle = patches.Rectangle(
            (-x_len / 2, -y_len / 2), x_len, y_len, edgecolor="blue", facecolor="none"
        )
        self.ax.add_patch(rectangle)

        # Last pose circle
        self.circle = patches.Circle(
            (0, 0), 6, edgecolor="#326295", facecolor="white", linewidth=2.0
        )
        self.ax.add_patch(self.circle)

        self.canvas.draw()

    def update(self, cop_list: list = None):
        if cop_list is None:
            return
        last_indexes = 100
        cop_x = np.array(cop_list[0])
        cop_y = np.array(cop_list[1])

        self.ax.clear()
        self.ax.plot(cop_x, cop_y, label="Recorded values")
        self.ax.plot(
            cop_x[-last_indexes],
            cop_y[-last_indexes],
            label=f"Last {last_indexes} values",
        )

        self.circle.set_center(cop_x[-1], cop_y[-1])

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
            ax = self.figure.add_subplot(math.ceil(total_subplots / 2), 2, i + 1)
            ax.plot(0, 0)
            ax.grid(True)
            ax.set_title("Encoder n")
            # ax.set_xlabel('Time(s)')
            ax.set_ylabel("Angles (deg)")
            self.subplots.append(ax)

    def update(self, timestamp_list: list):
        # TODO
        np_time = np.array(timestamp_list)
        np_time_incr = np.diff(np_time)

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
            ax = self.figure.add_subplot(math.ceil(total_subplots / 2), 2, i + 1)
            ax.plot(0, 0)
            ax.grid(True)
            ax.set_title("IMU n")
            # ax.set_xlabel('Time(s)')
            ax.set_ylabel("Angles (deg)")
            self.subplots.append(ax)

    def update(self, timestamp_list: list):
        # TODO
        np_time = np.array(timestamp_list)
        np_time_incr = np.diff(np_time)

        pass

    def clear(self):
        self.setup()
