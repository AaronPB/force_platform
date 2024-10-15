import pandas as pd
import plotly.graph_objects as go


class PlatformForcesFigure:
    def __init__(
        self, title: str, y_label: str = "Force (N)", x_label: str = "Time (s)"
    ) -> None:
        self.figure = go.Figure()
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

    def getFigure(
        self, y_values: pd.Series | pd.DataFrame, x_values: pd.Series
    ) -> go.Figure:

        if isinstance(y_values, pd.Series):
            y_values = y_values.to_frame()

        self.figure.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
        )
        return self.figure


class PlatformCOPFigure:
    def __init__(self, title: str) -> None:
        self.figure = go.Figure()
        self.title = title
        self.x_label = "Medio-Lateral (mm)"
        self.y_label = "Anterior-Posterior (mm)"

    def getFigure(self, y_values: pd.Series, x_values: pd.Series) -> go.Figure:

        self.figure.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
        )
        return self.figure
