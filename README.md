# Weather Demo with Gradio & Plotly

A simple, modular Python project demonstrating **data fetching, processing, plotting, and interactive UI**.  
Designed with **TDD, logging, error handling, and maintainability** in mind.

---

## Features

- Add a location and fetch weather readings (mock or API)
- View **daily statistics** (min, avg, max temperatures) with interactive Plotly line charts
- View **weekly high/low temperatures** with interactive Plotly bar charts
- Modular architecture: DB, core logic, plotting, and UI separated
- Fully tested functions (TDD approach)
- Logging and error handling for reliability

---

## Project Structure
```bash
weather_demo/
│
├── weather/
│ ├── init.py
│ ├── db.py # DB connection & fetch/insert functions
│ ├── ui_core.py # Core functions: daily/weekly summaries, add location
│ ├── plots.py # Plotly plotting functions
│ ├── analyzer.py
│ ├── api.py
│ ├── logging_config.py # Logging setup
│ └── ui.py # Gradio interface
│
├── tests/
│ ├── conftest.py
│ ├── test_analyzer.py
│ ├── test_api.py
│ ├── test_db.py
│ ├── test_ui.py # Core function tests
│ └── test_plots.py # Plotting tests
│
├── requirements.txt # Python dependencies
├── init_db.py # Checks, updates, and intializes db on program start
└── README.md # This file
```

---

## Installation

1. Clone the repo:

```bash
git clone <repo_url>
cd weather_demo
```
Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create the SQLite database:

It will be initialized on run now. Below serves as a reference.
```SQL
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    lat REAL,
    lon REAL
);

CREATE TABLE readings (
    id INTEGER PRIMARY KEY,
    location_id INTEGER,
    time TIMESTAMP,
    temp_c REAL,
    source TEXT,
    FOREIGN KEY(location_id) REFERENCES locations(id)
);
```
## Running the App
```bash
python -m weather.ui
```

Open the Gradio interface in your browser.

Use the tabs to:

Add a location & fetch weather

View daily statistics (interactive line chart)

View weekly high/low temperatures (interactive bar chart)

## Testing

Run all tests with:
```bash
pytest tests/
```

Core functions: validate input/output, handle missing data

Plotting functions: ensure Figure objects, correct traces, handles empty/None data

## Development Workflow

Write Tests → Define expected behavior for core functions or plots.

Implement Function → Minimal code to pass tests (Red → Green).

Refactor → Improve modularity, logging, and error handling.

Integrate with UI → Wrap function in Gradio callback.

Run Tests → Confirm everything still works.

Document & Log → Maintain clarity and maintainability.

## Best Practices Demonstrated

Modular architecture (DB, core logic, plotting, UI)

Logging and error handling

Test-Driven Development (TDD)

Gradio for rapid, interactive frontend

Reusable and maintainable code

## Notes

Designed as a learning/demo project.

Plots are interactive via Plotly and easily extendable.

Core logic can be replaced or extended for other weather API integrations or ML predictions.
