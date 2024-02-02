import streamlit as st
import pandas as pd
import plotly.express as px


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
        xaxis_title=settings["x_axis_title"],
        yaxis_title=settings["y_axis_title"],
        legend_title=settings["color_name"],
    )
    if "h_line" in settings:
        fig.add_hline(y=settings["h_line"], line_dash="dash", line_color="red")

    return fig
