# -*- coding: utf-8 -*-

import time
from PySide6 import QtWidgets, QtCore
from src.managers.testDataManager import TestDataManager


class PlotterThread(QtCore.QThread):
    def __init__(
        self,
        tab_widget: QtWidgets.QTabWidget,
        data_mngr: TestDataManager,
        interval_ms: int = 100,
    ) -> None:
        super().__init__()
        self.tab_widget = tab_widget
        self.data_mngr = data_mngr
        self.plot_interval_ms = interval_ms

    def run(self) -> None:
        self.request_stop = False
        while not self.request_stop:
            self.plot()
            time.sleep(self.plot_interval_ms / 1000)

    def plot(self) -> None:
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:
            return
        self.data_mngr.updatePlotWidgetDraw(current_index)

    def stopTimer(self) -> None:
        self.request_stop = True
