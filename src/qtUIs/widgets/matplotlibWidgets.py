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
        self.markers = ["x", "o", "^", "s", "D"]
        self.markers_amount = 10
        self.linepx_main = 1.5

    def setupPlot(self, df: pd.DataFrame, axis_labels: tuple[str, str] = None) -> None:
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
                marker = self.markers[i % len(self.markers)]
                ax.plot(
                    x_data,
                    df[column],
                    label=column,
                    color=color,
                    linewidth=self.linepx_main,
                    marker=marker,
                    markevery=len(df) // self.markers_amount,
                )
                i += 1
        ax.grid(True)
        if axis_labels:
            ax.set_xlabel(axis_labels[0])
            ax.set_ylabel(axis_labels[1])
        ax.legend()
        self.canvas.draw()

    def setupRangedPlot(
        self,
        df: pd.DataFrame,
        idx1: int,
        idx2: int,
        axis_labels: tuple[str, str] = None,
    ) -> None:
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
                marker = self.markers[i % len(self.markers)]
                ax.plot(
                    x_data[idx1:idx2],
                    df[column][idx1:idx2],
                    label=column,
                    color=color,
                    linewidth=self.linepx_main,
                    marker=marker,
                    markevery=(idx2 - idx1) // self.markers_amount,
                )
                i += 1
        ax.grid(True)
        if axis_labels:
            ax.set_xlabel(axis_labels[0])
            ax.set_ylabel(axis_labels[1])
        ax.legend()
        self.canvas.draw()

    def setupRangedPreviewPlot(self, df: pd.DataFrame, idx1: int, idx2: int, axis_labels: tuple[str, str] = None) -> None:
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
                marker = self.markers[i % len(self.markers)]
                ax.plot(
                    x_data,
                    df[column],
                    label=column,
                    color=color,
                    linewidth=self.linepx_main,
                    marker=marker,
                    markevery=len(df) // self.markers_amount,
                )
                i += 1
        ax.axvline(x=x_data[idx1], color="blue", linestyle="--")
        ax.axvline(x=x_data[idx2 - 1], color="blue", linestyle="--")
        ax.grid(True)
        if axis_labels:
            ax.set_xlabel(axis_labels[0])
            ax.set_ylabel(axis_labels[1])
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
        self.markers = ["o", "^", "s", "D"]
        self.markers_amount = 10
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
            marker = self.markers[i % len(self.markers)]
            ax.plot(
                times,
                df[column],
                label=column,
                color=color,
                linewidth=self.linepx_second,
                marker=marker,
                markevery=len(df) // self.markers_amount,
            )
            i += 1
        ax.grid(True)
        ax.legend(loc="upper right")


# TODO Test
class PlotPlatformCOPWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PlotPlatformCOPWidget, self).__init__()

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

    def setupPlot(
        self,
        cop: tuple[pd.Series, pd.Series],
        ellipse_params: tuple[float, float, float, float],
    ) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlabel("Medio-Lateral Motion (mm)")
        ax.set_ylabel("Anterior-Posterior Motion (mm)")
        ax.grid(True)

        # Platform patch
        x_len = 400
        y_len = 600
        rectangle = patches.Rectangle(
            (-x_len / 2, -y_len / 2), x_len, y_len, edgecolor="blue", facecolor="none"
        )
        ax.add_patch(rectangle)

        # Ellipse patch
        ellipse = patches.Ellipse(
            xy=(np.mean(cop[1]), np.mean(cop[0])),
            width=2 * ellipse_params[0],  # a
            height=2 * ellipse_params[1],  # b
            angle=np.degrees(ellipse_params[2]),  # phi
            edgecolor="red",
            facecolor="red",
            alpha=0.3,
        )
        ax.add_patch(ellipse)
        area = ellipse_params[3] / 100  # From mm2 to cm2
        ax.text(
            0,
            0,
            f"Area: {area:.2f} cm2",
            ha="center",
            va="center",
            color="black",
            fontsize=12,
        )

        # Plot COP and draw
        ax.plot(cop[1], cop[0])
        self.canvas.draw()


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
