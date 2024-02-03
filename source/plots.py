import streamlit as st
import pandas as pd
import plotly.express as px
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


def line_chart(df, settings: dict):
    fig = px.line(
        df, x=settings["x"], y=settings["y"], color=settings["color"], markers=False
    )
    fig.update_layout(
        xaxis_title=settings["xaxis_title"],
        yaxis_title=settings["yaxis_title"],
        legend_title=settings["color_name"],
    )
    if "h_line" in settings:
        fig.add_hline(y=settings["h_line"], line_dash="dash", line_color="red")

    return fig
