import pandas as pd
import numpy as np
import plotly.graph_objects as go


class GeneralFigure:
    def __init__(self, title: str, y_label: str, x_label: str = "Time (s)") -> None:
        self.figure = go.Figure()
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

    def getFigure(
        self, y_values: pd.Series | pd.DataFrame, x_values: pd.Series
    ) -> go.Figure:

        mark_every = 10

        if isinstance(y_values, pd.Series):
            y_values = y_values.to_frame()

        # Get indexes for even markers in figure
        marker_indexes = np.array([])
        if mark_every > 1 and len(x_values) > mark_every:
            marker_indexes = np.arange(0, len(x_values), mark_every)

        for column in y_values.columns:
            # TODO Change colors and markers styles
            self.figure.add_trace(
                go.Scatter(
                    x=x_values,
                    y=y_values[column],
                    mode="lines",
                    line=dict(color="#e70f67", width=2),
                    name=column,
                )
            )
            if marker_indexes:
                self.figure.add_trace(
                    go.Scatter(
                        x=x_values.iloc[marker_indexes],
                        y=y_values[column].iloc[marker_indexes],
                        mode="markers",
                        marker=dict(symbol="triangle-up", color="#e70f67", size=10),
                        name=column,
                    )
                )

        self.figure.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
        )
        return self.figure
