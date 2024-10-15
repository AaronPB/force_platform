import pandas as pd
import numpy as np
import plotly.graph_objects as go


class GeneralFigure:
    def __init__(self, title: str, y_label: str, x_label: str = "Time (s)") -> None:
        self.figure = go.Figure()
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

        # Plot style variables
        self.colors = [
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#ffffff",
            "#ff00cc",
            "#ffcc00",
        ]
        self.markers = [
            "circle",
            "square",
            "diamond",
            "triangle-up",
            "hexagon",
            "y-down",
        ]
        self.line_width = 2

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

        for i, column in enumerate(y_values.columns):
            self.figure.add_trace(
                go.Scatter(
                    x=x_values,
                    y=y_values[column],
                    mode="lines",
                    line=dict(
                        color=self.colors[i % len(self.colors)], width=self.line_width
                    ),
                    name=column,
                )
            )
            if marker_indexes:
                self.figure.add_trace(
                    go.Scatter(
                        x=x_values.iloc[marker_indexes],
                        y=y_values[column].iloc[marker_indexes],
                        mode="markers",
                        marker=dict(
                            symbol=self.markers[i % len(self.markers)],
                            color=self.colors[i % len(self.colors)],
                            size=10,
                        ),
                        name=column,
                    )
                )

        self.figure.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
        )
        return self.figure
