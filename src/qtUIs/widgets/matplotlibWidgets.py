import numpy as np
import matplotlib.patches as patches
import math
from PySide6 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotPlatformForcesWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str):
        super(PlotPlatformForcesWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.group_name = group_name

        self.setup()

    def setup(self):
        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312, sharex=self.ax1)
        self.ax3 = self.figure.add_subplot(313, sharex=self.ax1)
        self.lines_ax1 = []
        self.lines_ax2 = []
        self.lines_ax3 = []

        self.lines_defined = False
        self.ax1.set_title(f"Forces - {self.group_name}")
        self.ax1.set_ylabel("Forces Z (kg)")
        self.ax2.set_ylabel("Forces X (kg)")
        self.ax3.set_ylabel("Forces Y (kg)")
        self.ax3.set_xlabel("Time (s)")
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.grid(True)
        self.canvas.draw()

    def defineLines(self, ax, lines_ax: list, names: list):
        for name in names:
            (line,) = ax.plot(0, 0, label=name)
            lines_ax.append(line)
        lines_ax.append(line)
        ax.legend(loc="upper right")
        self.lines_defined = True

    def update(
        self, times_np: np.ndarray, forces_x: dict, forces_y: dict, forces_z: dict
    ):
        if not self.lines_defined:
            self.defineLines(self.ax1, self.lines_ax1, list(forces_z.keys()))
            self.defineLines(self.ax2, self.lines_ax2, list(forces_x.keys()))
            self.defineLines(self.ax3, self.lines_ax3, list(forces_y.keys()))

        for i, values_np in enumerate(forces_z.values()):
            self.lines_ax1[i].set_data(times_np, values_np)
        for i, values_np in enumerate(forces_x.values()):
            self.lines_ax2[i].set_data(times_np, values_np)
        for i, values_np in enumerate(forces_y.values()):
            self.lines_ax3[i].set_data(times_np, values_np)

        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.relim()
            ax.autoscale_view()

        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.setup()


class PlotPlatformCOPWidget(QtWidgets.QWidget):
    def __init__(self, group_name: str):
        super(PlotPlatformCOPWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.group_name = group_name
        self.last_indexes = 20

        self.setup()

    def setup(self):
        self.ax = self.figure.add_subplot()
        self.ax.set_title(f"COP - {self.group_name}")
        self.ax.set_xlabel("Medio-Lateral Motion (mm)")
        self.ax.set_ylabel("Anterior-Posterior Motion (mm)")
        self.ax.grid(True)
        (self.line_total,) = self.ax.plot(0, 0, label="Recorded values", color="blue")
        (self.line_last,) = self.ax.plot(
            0, 0, label=f"Last {self.last_indexes} values", color="red"
        )
        self.ax.legend(loc="upper right")

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

    def update(self, cop_x_np: np.ndarray, cop_y_np: np.ndarray):
        self.line_total.set_data(cop_x_np, cop_y_np)
        self.line_last.set_data(
            cop_x_np[-self.last_indexes :], cop_y_np[-self.last_indexes :]
        )
        self.circle.set_center([cop_x_np[-1:], cop_y_np[-1:]])

        self.canvas.draw()

    def clear(self):
        self.figure.clear()
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
        self.subplots_lines = []
        self.subplots_ax = []

        self.setup()

    def setup(self):
        self.createSubplots(
            ["Encoder " + str(i) for i in range(1, self.group_size + 1)]
        )
        self.canvas.draw()

    def createSubplots(self, encoder_names: list, real_set: bool = False):
        encoders_len = len(encoder_names)
        if real_set:
            self.figure.clear()
            self.subplots_lines.clear()
            self.subplots_ax.clear()
        for i, encoder_name in enumerate(encoder_names):
            ax = self.figure.add_subplot(math.ceil(encoders_len / 2), 2, i + 1)
            ax.grid(True)
            (line,) = ax.plot(0, 0)
            ax.set_title(encoder_name)
            # ax.set_xlabel('Time(s)')
            ax.set_ylabel("Distance (mm)")
            self.subplots_lines.append(line)
            self.subplots_ax.append(ax)
        self.subplots_set = real_set

    def update(self, times_np: np.ndarray, encoders_dict: dict):
        if not self.subplots_set:
            self.createSubplots(list(encoders_dict.keys()), True)

        for ax, line, values_np in zip(
            self.subplots_ax, self.subplots_lines, encoders_dict.values()
        ):
            line.set_data(times_np, values_np)
            ax.relim()
            ax.autoscale_view()

        self.canvas.draw()

    def clear(self):
        self.figure.clear()
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
        self.subplots_lines = []
        self.subplots_ax = []

        self.setup()

    def setup(self):
        self.createSubplots(["IMU " + str(i) for i in range(1, self.group_size + 1)])
        self.canvas.draw()

    def createSubplots(self, imu_names: list, real_set: bool = False):
        imus_len = len(imu_names)
        if real_set:
            self.figure.clear(keep_observers=True)
            self.subplots_lines.clear()
            self.subplots_ax.clear()
        for i, encoder_name in enumerate(imu_names):
            ax = self.figure.add_subplot(math.ceil(imus_len / 2), 2, i + 1)
            ax.grid(True)
            (line_x,) = ax.plot(0, 0, label="X", color="red")
            (line_y,) = ax.plot(0, 0, label="Y", color="blue")
            (line_z,) = ax.plot(0, 0, label="Z", color="green")
            ax.set_title(encoder_name)
            # ax.set_xlabel('Time(s)')
            ax.set_ylabel("Angle (degrees)")
            ax.set_ylim(-180, 180)
            ax.set_yticks(range(-180, 181, 20))
            ax.legend(loc="upper right")
            self.subplots_lines.append([line_x, line_y, line_z])
            self.subplots_ax.append(ax)
        self.subplots_set = real_set

    def update(self, times_np: np.ndarray, imus_dict: dict):
        if not self.subplots_set:
            self.createSubplots(list(imus_dict.keys()), True)

        for ax, line, values_np in zip(
            self.subplots_ax, self.subplots_lines, imus_dict.values()
        ):
            line[0].set_data(times_np, values_np[0])
            line[1].set_data(times_np, values_np[1])
            line[2].set_data(times_np, values_np[2])
            ax.relim()
            ax.autoscale_view()

        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.setup()


class PlotRegressionWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PlotRegressionWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.setup()

    def setup(self):
        self.ax = self.figure.add_subplot()
        self.ax.set_xlabel("Sensor values")
        self.ax.set_ylabel("Test values")
        self.ax.grid(True)
        (self.line_plot,) = self.ax.plot(0, 0, label="Linear regression", color="blue")
        self.line_scatter = self.ax.scatter(0, 0, label="Measurements", color="red")
        self.ax.legend(loc="upper right")
        self.figure.set_figheight(4)

        self.canvas.draw()

    def updateScatter(self, sensor_values_np: np.ndarray, test_values_np: np.ndarray):
        new_offsets = np.column_stack((sensor_values_np, test_values_np))
        self.line_scatter.set_offsets(new_offsets)
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw()

    def updateRegression(self, calib_values_np: np.ndarray, test_values_np: np.ndarray):
        self.line_plot.set_data(calib_values_np, test_values_np)
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.setup()
