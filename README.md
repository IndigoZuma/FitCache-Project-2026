# FitCache-Project-2026

SDEV 365 Group 1 Project Management Python Application

Group 1 Project Members: Sharon Campbell, Elijah Terry, Kaleb Hunter, Blaize Fox,Da vid Cruz and Robert Chickadaunce.

## FitCache Desktop App

FitCache is a beginner-friendly Python desktop workout tracker. It allows users to log workouts, review workout history, track total workout volume, and monitor progress through milestone-based summaries.

## Features

- Fullscreen/maximized desktop GUI
- Dashboard, Log Workout, History, and Summary tabs
- Exercise dropdown with Add Exercise option
- Automatic capitalization and exercise-name normalization
- Common typo correction through the service layer
- Stable record IDs for safer selection and deletion
- JSON-backed persistence with stricter validation
- Explicit corrupted-data error handling
- Pytest automated test suite

## Requirements

- Python 3.13
- ttkbootstrap
- pyspellchecker
- pytest

## Install

```bash
pip install -r requirements.txt
```

## Run the app

```bash
python gui.py
```

## Run tests

If your test file is in the project root:

```bash
python -m pytest test_main.py
```

Or run the whole suite:

```bash
python -m pytest
```

## Project Structure

