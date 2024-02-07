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


def scatter_plot(df, settings: dict):
    fig = px.scatter(
        df, x=settings["x"], y=settings["y"]
    )

    fig.add_shape(type="line", 
              x0=2019, y0=0, x1=2040, y1=10,  # Coordinates of the line's start and end points
              line=dict(color="orange", width=2, dash="dash")
    )
    fig.add_vline(x=2037, line_dash="dot", line_color="red")
    fig.add_vline(x=2023, line_dash="dot", line_color="rgba(255, 0, 0, 0.5)")
    
    light_grey = "rgba(200, 200, 200, 0.3)"
    fig.update_layout(
        xaxis_title=settings["xaxis_title"],
        yaxis_title=settings["yaxis_title"],
        width=settings["width"],
        height=settings["height"],
        xaxis=dict(
            showline=True,
            linewidth=1,
            linecolor=light_grey,
            mirror=True,
            showgrid=True,
            showticklabels=True,
            tickmode='auto',
            ticklen=5
        ),
        yaxis=dict(
            showline=True,
            linewidth=1,
            linecolor=light_grey,
            mirror=True,
            showgrid=True,
            showticklabels=True,
            tickmode='auto',
            ticklen=5,
            
        )
    )

    return fig
