import pandas as pd
import numpy as np

from src.utils import LogHandler


class SensorDataFrame:
    def __init__(self, group_name: str, columns: list) -> None:
        self.log_handler = LogHandler(
            str(__class__.__name__ + '-' + group_name))
        self.df = pd.DataFrame(columns=columns)

    def addRow(self, values: list):
        if len(values) != len(self.df.columns):
            self.log_handler.logger.error(
                "Number of values doesn't match number of columns! Expected "
                + str(len(self.df.columns)) + " got " + str(len(values)))
            return
        self.df.loc[len(self.df)] = values

    def getDataFrame(self, slope_values: list = None, intercept_values: list = None):
        df = self.df.copy()
        if not slope_values:
            return df
        if len(slope_values) != len(self.df.columns):
            self.log_handler.logger.error(
                "Number of slope_values doesn't match number of columns! Expected "
                + str(len(self.df.columns)) + " got " + str(len(slope_values)))
            return df
        if len(intercept_values) != len(self.df.columns):
            self.log_handler.logger.error(
                "Number of intercept_values doesn't match number of columns! Expected "
                + str(len(self.df.columns)) + " got " + str(len(intercept_values)))
            return df
        return df * slope_values + intercept_values

    def getIntervalMeans(self, slope_values: list, intercept_values: list, first_index: int, last_index: int):
        df = self.getDataFrame(slope_values, intercept_values)
        df_interval = df.iloc[first_index:last_index+1]
        return np.mean(df_interval)
