from typing import List, Dict
import plotly.graph_objects as go
from .logging_config import get_logger

logger = get_logger(__name__)


def plot_daily_stats(daily_stats: List[Dict]) -> go.Figure:
    """
    Create a line chart for daily average, min, and max temperatures.

    Args:
        daily_stats (List[Dict]): List of dicts with keys:
            - date (datetime.date)
            - avg_temp_c (float)
            - min_temp_c (float)
            - max_temp_c (float)
            - count (int)

    Returns:
        go.Figure: Plotly figure object
    """
    if not daily_stats:
        logger.warning("No daily stats provided for plotting")
        return go.Figure()

    # Filter to only valid stats that have all required keys
    required_keys = ["date", "avg_temp_c", "min_temp_c", "max_temp_c"]
    valid_stats = [d for d in daily_stats if all(k in d for k in required_keys)]

    if not valid_stats:
        logger.warning("No valid daily stats found for plotting after filtering")
        return go.Figure()

    dates = [d["date"] for d in valid_stats]
    avg_temps = [d["avg_temp_c"] for d in valid_stats]
    min_temps = [d["min_temp_c"] for d in valid_stats]
    max_temps = [d["max_temp_c"] for d in valid_stats]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=avg_temps, mode="lines+markers", name="Avg Temp"))
    fig.add_trace(go.Scatter(x=dates, y=min_temps, mode="lines+markers", name="Min Temp"))
    fig.add_trace(go.Scatter(x=dates, y=max_temps, mode="lines+markers", name="Max Temp"))

    fig.update_layout(
        title="Daily Weather Statistics",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        template="plotly_white"
    )

    return fig


def plot_weekly_high_low(high: float, low: float) -> go.Figure:
    """
    Create a bar chart showing weekly high and low temperatures.

    Args:
        high (float): Weekly high temperature
        low (float): Weekly low temperature

    Returns:
        go.Figure: Plotly figure object
    """
    if high is None or low is None:
        logger.warning("High or Low value is None for weekly plot")
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=["High", "Low"], y=[high, low], text=[high, low], textposition="auto"))

    fig.update_layout(
        title="Weekly High / Low Temperatures",
        yaxis_title="Temperature (°C)",
        template="plotly_white"
    )

    return fig
