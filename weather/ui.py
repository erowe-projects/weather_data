from .plots import plot_daily_stats, plot_weekly_high_low
from .analyzer import weekly_high_low, compute_daily_stats
from .db import init_db, insert_location, upsert_weather_readings, fetch_readings
import datetime as dt
import gradio as gr
from .ui_core import get_daily_summary, get_weekly_high_low, add_location_and_fetch_weather # core logic functions
import sqlite3

DB_PATH = "weather_demo.db"

# -----------------------------
# Database setup
# -----------------------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
init_db(conn)
# -----------------------------
# Gradio Interface
# -----------------------------
with gr.Blocks() as demo:
    gr.Markdown("## Weather Demo UI with Plots")
    
    # -----------------------------
    # Tab 1: Add Location & Fetch Weather
    # -----------------------------
    with gr.Tab("Add Location & Fetch Weather"):
        name_input = gr.Textbox(label="Location Name", placeholder="Enter city or label")
        lat_input = gr.Number(label="Latitude")
        lon_input = gr.Number(label="Longitude")
        start_input = gr.Textbox(label="Start Date (YYYY-MM-DD)")
        end_input = gr.Textbox(label="End Date (YYYY-MM-DD)")
        fetch_button = gr.Button("Fetch & Save")
        fetch_output = gr.Textbox(label="Result")
        
        fetch_button.click(
            add_location_and_fetch_weather,
            inputs=[name_input, lat_input, lon_input, start_input, end_input],
            outputs=fetch_output
        )
    
    # -----------------------------
    # Tab 2: Daily Summary Plot
    # -----------------------------
    with gr.Tab("Daily Summary"):
        name_input2 = gr.Textbox(label="Location Name")
        start_input2 = gr.Textbox(label="Start Date (YYYY-MM-DD)")
        end_input2 = gr.Textbox(label="End Date (YYYY-MM-DD)")
        summary_button = gr.Button("Get Daily Summary")
        summary_plot = gr.Plot(label="Daily Temp Plot")
        
        def daily_plot_ui(name, start, end):
            stats = get_daily_summary(name, start, end)
            return plot_daily_stats(stats)
        
        summary_button.click(
            daily_plot_ui,
            inputs=[name_input2, start_input2, end_input2],
            outputs=summary_plot
        )

    # -----------------------------
    # Tab 3: Weekly High/Low Plot
    # -----------------------------
    with gr.Tab("Weekly High/Low"):
        name_input3 = gr.Textbox(label="Location Name")
        start_input3 = gr.Textbox(label="Start Date (YYYY-MM-DD)")
        end_input3 = gr.Textbox(label="End Date (YYYY-MM-DD)")
        highlow_button = gr.Button("Get Weekly High/Low")
        highlow_plot = gr.Plot(label="Weekly High/Low Plot")
        
        def weekly_plot_ui(name, start, end):
            # Fetch readings from DB
            loc = conn.execute("SELECT id FROM locations WHERE name = ?", (name,)).fetchone()
            if not loc:
                return plot_weekly_high_low(None, None)
            readings = fetch_readings(conn, loc["id"], dt.datetime.fromisoformat(start), dt.datetime.fromisoformat(end))
            high, low = weekly_high_low(readings)
            return plot_weekly_high_low(high, low)
        
        highlow_button.click(
            weekly_plot_ui,
            inputs=[name_input3, start_input3, end_input3],
            outputs=highlow_plot
        )

if __name__ == "__main__":
    demo.launch()
