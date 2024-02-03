import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np


def test():
    # Generate some dummy data
    df = pd.DataFrame(
        {
            "X": np.arange(10),  # X-axis values
            "Y": np.random.randn(10),  # Y-axis values: 10 random numbers
        }
    )

    # Create a line chart using Plotly Express
    fig = px.line(
        df, x="X", y="Y", title="Dummy Plotly Express Line Chart", markers=True
    )

    # Show the figure
    return fig


def show_area_plot(df, settings: dict):
    fig = px.area(
        df,
        x=settings["x"],
        y=settings["y"],
        color=settings["color"],
        title="Energieinput (kWh) für Fernwärme Wärme und Strom (WKK) über die Jahre",
    )
    return fig


def line_chart(df: pd.DataFrame, settings: dict):
    fig = go.Figure()
    for color in df[settings["color"]].unique():
        color_df = df[df[settings["color"]] == color]
        fig.add_trace(
            go.Scatter(
                x=color_df[settings["x"]],
                y=color_df[settings["y"]],
                mode="lines",
                name=color,
            )
        )
    if "h_line" in settings:
        fig.add_shape(
            type="line",
            x0=0,
            y0=settings["h_line"]["y"],
            x1=1,
            y1=settings["h_line"]["y"],
            line=dict(color="Red", width=3, dash="dot"),
            xref="paper",
            yref="y",
        )

    fig.update_layout(
        xaxis_title=settings["x_title"],
        yaxis_title=settings["y_title"],
    )
    return fig
