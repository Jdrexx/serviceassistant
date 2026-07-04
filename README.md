# Service Business Receptionist

![Python](https://img.shields.io/badge/Python-3.11_%7C_3.12-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite)

Capture service-business leads, classify urgency, and manage receptionist intake workflows. Enter a lead's details and get a sorted callback queue — built for local businesses that need a structured alternative to sticky notes and spreadsheets.

## Features

- Lead intake form — name, contact, issue description, service vertical
- Urgency classification (low/medium/high/critical) based on issue description keywords and time sensitivity
- Receptionist summary view showing pending leads sorted by urgency
- Callback task list with notes per lead
- Preset service verticals (HVAC, plumbing, electrical, general)
- All data stays local — no external API calls

## Tech Stack

- Python 3.11+ / FastAPI / SQLite
- Vanilla HTML/CSS/JS frontend served by the API
- Pytest

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8104
```

Open: http://localhost:8104

Windows: double-click `run.bat`

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Browser demo UI |
| GET | `/api/health` | Health check |
| GET | `/docs` | Interactive API docs |

## Tests

```bash
uv run pytest -q
```
