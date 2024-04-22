import pandas as pd
import numpy as np
import matplotlib.patches as patches
import math
from PySide6 import QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class PlotFigureWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PlotFigureWidget, self).__init__()

        self.figure: Figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

        # Plot style
        self.colors = ["red", "blue", "black", "orange", "purple"]
        self.linepx_main = 1.5

    def setupPlot(self, df: pd.DataFrame) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # If only 1 col, make it also a df
        if isinstance(df, pd.Series):
            df = df.to_frame()
        x_data = df.index if "times" not in df.columns else df["times"]
        i = 0
        for column in df.columns:
            if column != "times":
                color = self.colors[i % len(self.colors)]
                ax.plot(
                    x_data,
                    df[column],
                    label=column,
                    color=color,
                    linewidth=self.linepx_main,
                )
                i += 1
        ax.grid(True)
        ax.legend()
        self.canvas.draw()

    def setupRangedPlot(self, df: pd.DataFrame, idx1: int, idx2: int) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # If only 1 col, make it also a df
        if isinstance(df, pd.Series):
            df = df.to_frame()
        x_data = df.index if "times" not in df.columns else df["times"]
        i = 0
        for column in df.columns:
            if column != "times":
                color = self.colors[i % len(self.colors)]
                ax.plot(
                    x_data[idx1:idx2],
                    df[column][idx1:idx2],
                    label=column,
                    color=color,
                    linewidth=self.linepx_main,
                )
                i += 1
        ax.grid(True)
        ax.legend()
        self.canvas.draw()

    def setupRangedPreviewPlot(self, df: pd.DataFrame, idx1: int, idx2: int) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # If only 1 col, make it also a df
        if isinstance(df, pd.Series):
            df = df.to_frame()
        x_data = df.index if "times" not in df.columns else df["times"]
        i = 0
        for column in df.columns:
            if column != "times":
                color = self.colors[i % len(self.colors)]
                ax.plot(
                    x_data,
                    df[column],
                    label=column,
                    color=color,
                    linewidth=self.linepx_main,
                )
                i += 1
        ax.axvline(x=x_data[idx1], color="blue", linestyle="--")
        ax.axvline(x=x_data[idx2 - 1], color="blue", linestyle="--")
        ax.grid(True)
        ax.legend()
        self.canvas.draw()


class PlotPlatformForcesWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PlotPlatformForcesWidget, self).__init__()

        self.figure: Figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

        # Plot style
        self.sum_color = "red"
        self.colors = ["blue", "black", "orange", "purple"]
        self.linepx_main = 3
        self.linepx_second = 1

        # Setup Axes
        self.ax_fz = self.figure.add_subplot(311)
        self.ax_fx = self.figure.add_subplot(312, sharex=self.ax_fz)
        self.ax_fy = self.figure.add_subplot(313, sharex=self.ax_fz)
        self.ax_fz.set_ylabel("Forces Z (kg)")
        self.ax_fx.set_ylabel("Forces X (kg)")
        self.ax_fy.set_ylabel("Forces Y (kg)")
        self.ax_fy.set_xlabel("Time (s)")

    def setupPlot(
        self,
        times: list[float],
        df_fx: pd.DataFrame,
        df_fy: pd.DataFrame,
        df_fz: pd.DataFrame,
    ) -> None:
        self.plotAxes(self.ax_fz, times, df_fz)
        self.plotAxes(self.ax_fx, times, df_fx)
        self.plotAxes(self.ax_fy, times, df_fy)
        self.canvas.draw()

    def setupRangedPlot(
        self,
        times: list[float],
        df_fx: pd.DataFrame,
        df_fy: pd.DataFrame,
        df_fz: pd.DataFrame,
        idx1: int,
        idx2: int,
    ) -> None:
        self.plotAxes(self.ax_fz, times[idx1:idx2], df_fz[idx1:idx2])
        self.plotAxes(self.ax_fx, times[idx1:idx2], df_fx[idx1:idx2])
        self.plotAxes(self.ax_fy, times[idx1:idx2], df_fy[idx1:idx2])
        self.canvas.draw()

    def plotAxes(self, ax: Axes, times: list[float], df: pd.DataFrame) -> None:
        if df.empty:
            return
        ax.plot(
            times,
            df.sum(axis=1),
            label="Sum",
            color=self.sum_color,
            linewidth=self.linepx_main,
        )
        # If only 1 col, make it also a df
        if isinstance(df, pd.Series):
            df = df.to_frame()
        i = 0
        for column in df.columns:
            color = self.colors[i % len(self.colors)]
            ax.plot(
                times,
                df[column],
                label=column,
                color=color,
                linewidth=self.linepx_second,
            )
            i += 1
        ax.grid(True)
        ax.legend(loc="upper right")


# TODO Test
class PlotPlatformCOPWidget(QtWidgets.QWidget):
    def __init__(self):
        self.figure: Figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

        # Plot style
        self.ellipse_color = "red"
        self.ellipse_linepx = 3
        self.cop_color = "blue"
        self.cop_line_px = 1

        self.setup()

    def setupPlot(
        self,
        cop: tuple[pd.Series, pd.Series],
        ellipse: tuple[np.array, np.array, float],
    ) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlabel("Medio-Lateral Motion (mm)")
        ax.set_ylabel("Anterior-Posterior Motion (mm)")
        ax.grid(True)

        # Platform patch
        x_len = 600
        y_len = 400
        rectangle = patches.Rectangle(
            (-x_len / 2, -y_len / 2), x_len, y_len, edgecolor="blue", facecolor="none"
        )
        ax.add_patch(rectangle)

        # TODO WIP Ellipse patch
        # ellipse = patches.Ellipse(
        #     (-x_len / 2, -y_len / 2), x_len, y_len, edgecolor="blue", facecolor="none"
        # )
        # ax.add_patch(ellipse)

        # Plot COP and draw
        ax.plot(cop[0], cop[1])
        self.canvas.draw()


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
        (self.line_plot,) = self.ax.plot(0, 0, label="Regression", color="blue")
        self.line_scatter = self.ax.scatter(0, 0, label="Measurements", color="red")
        self.ax.legend()
        self.figure.set_figheight(4)

        self.canvas.draw()

    def updateScatter(self, sensor_values_np: np.ndarray, test_values_np: np.ndarray):
        new_offsets = np.column_stack((sensor_values_np, test_values_np))
        self.line_scatter.set_offsets(new_offsets)
        # Update plot scales
        x_margin = 0.1 * (np.max(sensor_values_np) - np.min(sensor_values_np))
        y_margin = 0.1 * (np.max(test_values_np) - np.min(test_values_np))
        if sensor_values_np.size == 1:
            x_margin = 0.1 * np.max(sensor_values_np)
            y_margin = 0.1 * np.max(test_values_np)
        self.ax.set_xlim(
            np.min(sensor_values_np) - x_margin, np.max(sensor_values_np) + x_margin
        )
        self.ax.set_ylim(
            np.min(test_values_np) - y_margin, np.max(test_values_np) + y_margin
        )
        self.canvas.draw()

    def updateRegression(self, calib_values_np: np.ndarray, test_values_np: np.ndarray):
        self.line_plot.set_data(calib_values_np, test_values_np)
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.setup()


class PlotResultsForcesWidget(QtWidgets.QWidget):
    def __init__(self, test_name: str):
        super(PlotResultsForcesWidget, self).__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.test_name = test_name
        self.data_index_start = 0
        self.data_index_end = 1

        self.setup()

    def setup(self):
        self.ax = self.figure.add_subplot()
        self.ax.set_title(f"Z axis platform forces sum - {self.test_name}")
        self.ax.set_xlabel("Data values")
        self.ax.set_ylabel("Weight (kg)")
        self.ax.grid(True)
        self.ax.axvline(x=self.data_index_start, color="blue", linestyle="--")
        self.ax.axvline(x=self.data_index_end, color="blue", linestyle="--")
        self.canvas.draw()

    def update(self, forces_z: np.ndarray, index_start: int, index_end: int):
        self.data_index_start = index_start
        self.data_index_end = index_end
        self.clear()
        # TODO plot forces_z
        self.ax.plot(0, 0, color="black")
        self.canvas.draw()

    def clear(self):
        self.figure.clear()
        self.setup()
