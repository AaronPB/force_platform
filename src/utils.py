# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import logging
import colorlog
import pandas as pd


class TestDataFrame:
    def __init__(self, columns):
        self.log_handler = LogHandler(str(__class__.__name__))
        self.df = pd.DataFrame(columns=columns)

    def add_row(self, values):
        if len(values) != len(self.df.columns):
            raise ValueError(
                "Number of values doesn't match number of columns")
        self.df = self.df.append(
            pd.Series(values, index=self.df.columns), ignore_index=True)

    def export_to_csv(self, file_path):
        self.df.to_csv(file_path, index=False)


class LogHandler:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        self.add_color_formatter(console_handler)
        self.logger.addHandler(console_handler)

    def add_color_formatter(self, handler):
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
