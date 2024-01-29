import streamlit as st
import pandas as pd
import plotly.express as px


def show_area_plot(df, settings: dict):
    fig = px.area(
        df,
        x=settings['x'], y=settings['y'],
        color=settings['color'],
        title='Energieinput (kWh) für Fernwärme Wärme und Strom (WKK) über die Jahre'
    )
    return fig