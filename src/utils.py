# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import logging
import colorlog
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt


class TestDataFrame:
    def __init__(self, columns):
        self.log_handler = LogHandler(str(__class__.__name__))
        self.df = pd.DataFrame(columns=columns)

    def addRow(self, values):
        if len(values) != len(self.df.columns):
            self.log_handler.logger.error(
                "Number of values doesn't match number of columns! Expected " + str(len(self.df.columns)) + " got " + str(len(values)))
            return
        self.df.loc[len(self.df)] = values

    def exportToCSV(self, file_path):
        self.df.to_csv(file_path, index=False)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        self.log_handler.logger.info(
            "Test file saved in: " + str(file_path) + " (" + str(round(file_size, 2)) + " MB)")

    def exportToBinary(self, file_path):
        self.df.to_pickle(file_path, index=False)
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        self.log_handler.logger.info(
            "Test file saved in: " + str(file_path) + " (" + str(round(file_size, 2)) + " MB)")

    def getDataFrame(self):
        return self.df.copy()

    def getIntervalMeanData(self, timestamp_init, timestamp_end):
        copy_df = self.getDataFrame()
        filtered_df = copy_df[(copy_df['timestamp'] >= timestamp_init) & (
            copy_df['timestamp'] <= timestamp_end)]
        mean_values = np.mean(filtered_df.drop('timestamp', axis=1), axis=0)
        return mean_values.to_dict()


class DataFramePlotter:
    def __init__(self, data_frame: pd.DataFrame):
        data_frame['timestamp'] = pd.to_datetime(
            data_frame['timestamp'], unit='ms')
        relative_time = data_frame['timestamp'] - \
            data_frame['timestamp'].iloc[0]
        relative_time = relative_time.dt.total_seconds()
        self.df = pd.DataFrame({'time': relative_time})
        self.df = pd.concat([self.df, data_frame.iloc[:, 1:]], axis=1)

    def plot_line(self, x_col, y_cols):
        fig, ax = plt.subplots()
        for y_col in y_cols:
            ax.plot(self.df[x_col], self.df[y_col], label=y_col)
        ax.legend()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Force (N)')
        # ax.set_ylim(0, 40)
        # ax.set_yticks(range(0, 41, 2))
        ax.grid(True)
        ax.minorticks_on()
        plt.show()


class StabilogramPlotter:
    def __init__(self, data_frame: pd.DataFrame):
        self.log_handler = LogHandler(str(__class__.__name__))

        data_frame['timestamp'] = pd.to_datetime(
            data_frame['timestamp'], unit='ms')
        relative_time = data_frame['timestamp'] - \
            data_frame['timestamp'].iloc[0]
        relative_time = relative_time.dt.total_seconds()
        self.df = pd.DataFrame({'time': relative_time})
        self.df = pd.concat([self.df, data_frame.iloc[:, 1:]], axis=1)
        # Default XY values
        self.cop_x_dif = None
        self.cop_y_dif = None
        # Calculate COP Values
        self.calculateCOPValues()

    def calculateCOPValues(self):
        # TODO load l_x, l_y, h from config maybe
        # Check first if df has the correct number of columns needed
        if self.df.shape[1] != 13:
            self.log_handler.logger.error(
                "Cannot calculate COP values because the loaded dataframe has "
                + str(self.df.shape[1]) + " instead of 13.")
            return
        # Set distances
        l_x = 600   # (mm) x distance between sensors
        l_y = 400   # (mm) y distance between sensors
        h = 20      # (mm) z distance between sensors and upper platform
        # Get forces
        f_z = self.df.iloc[:, 1:5].to_numpy().sum(axis=1)
        f_x = self.df.iloc[:, 5:9].to_numpy().sum(axis=1)
        f_y = self.df.iloc[:, 9:13].to_numpy().sum(axis=1)
        # Get moments
        m_x = l_y/2 * (-self.df.iloc[:, 1:5].to_numpy()
                       [:, [0, 1, 2, 3]]).sum(axis=1)
        m_y = l_x/2 * (-self.df.iloc[:, 1:5].to_numpy()
                       [:, [0, 1, 2, 3]]).sum(axis=1)
        m_z = l_y/2 * (-self.df.iloc[:, 5:9].to_numpy()[:, [0, 1, 2, 3]]).sum(axis=1) + \
            l_x/2 * (self.df.iloc[:, 9:13].to_numpy()
                     [:, [0, 1, 2, 3]]).sum(axis=1)
        # Get location of the center of pressure (COP)
        cop_x = (-h * f_x - m_y)/f_z
        cop_y = (-h * f_y + m_x)/f_z
        # Center COP and get realtive COP from mean center of pressure position
        self.cop_x_dif = cop_x - np.mean(cop_x)
        self.cop_y_dif = cop_y - np.mean(cop_y)

    def getPlotValues(self):
        return [self.cop_x_dif, self.cop_y_dif]


class LogHandler:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        self.addColorFormatter(console_handler)
        if (self.logger.hasHandlers()):
            self.logger.handlers.clear()
        self.logger.addHandler(console_handler)

    def addColorFormatter(self, handler):
        color_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s [%(name)s] [%(levelname)s] - %(message)s%(reset)s (%(codeline_log_color)s%(filename)s:%(lineno)d%(reset)s)',
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red'
            },
            secondary_log_colors={
                'codeline': {
                    'DEBUG': 'thin_white',
                    'INFO': 'thin_white',
                    'WARNING': 'thin_white',
                    'ERROR': 'thin_white',
                    'CRITICAL': 'thin_white'
                }
            }
        )
        handler.setFormatter(color_formatter)
