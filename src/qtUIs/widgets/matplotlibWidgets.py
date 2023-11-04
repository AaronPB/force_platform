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

        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312, sharex=self.ax1)
        self.ax3 = self.figure.add_subplot(313, sharex=self.ax1)

        self.lines_ax1 = []
        self.lines_ax2 = []
        self.lines_ax3 = []

        self.setup()

    def setup(self):
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
        ax.legend()
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

        self.ax = self.figure.add_subplot()

        self.setup()

    def setup(self):
        self.ax.clear()
        self.ax.set_title(f"COP - {self.group_name}")
        self.ax.set_xlabel("Medio-Lateral Motion (mm)")
        self.ax.set_ylabel("Anterior-Posterior Motion (mm)")
        self.ax.grid(True)
        (self.line_total,) = self.ax.plot(0, 0, label="Recorded values", color="blue")
        (self.line_last,) = self.ax.plot(
            0, 0, label=f"Last {self.last_indexes} values", color="red"
        )
        self.ax.legend()

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
        self.line_total.set_data(
            cop_x_np[-self.last_indexes :], cop_y_np[-self.last_indexes :]
        )
        self.circle.set_center(cop_x_np[-1:], cop_y_np[-1:])

        self.canvas.draw()

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
            ax.set_ylabel("Distance (mm)")
            self.subplots.append(ax)

    def update(self, times_np: np.ndarray, encoders_dict: dict):
        # TODO

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

    def update(self, times_np: np.ndarray, imus_dict: dict):
        # TODO

        pass

    def clear(self):
        self.setup()
