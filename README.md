# FitCache-Project-2026
SDEV 265 Group 1 Project Management Python Application  
Group 1 Project Members: Sharon Campbell, Robert Chickadaunce, David Cruz, Blaize Fox, Kaleb Hunter, Elijah Terry
## FitCache Desktop App

FitCache is a beginner-friendly Python desktop workout tracker. It allows users to log workouts, review workout history, track total workout volume, and monitor progress through milestone-based summaries.

### Features
- Fullscreen/maximized desktop GUI
- Dashboard, Log Workout, History, and Summary tabs
- Exercise dropdown with Add Exercise option
- Automatic capitalization and exercise-name normalization
- Common typo correction through the service layer
- Delete selected workouts
- Pytest test suite

### Requirements
- Python 3.13+
- ttkbootstrap==1.12.0
- pyspellchecker==0.8.3
- pytest==9.0.2
- colorama==0.4.6
- iniconfig==2.3.0
- packaging==26.0
- pluggy==1.6.0
- Pygments==2.20.0

### Install
```bash
pip install -r requirements.txt
```

### Run the app
```bash
python gui.py
```

### Run tests
```bash
python -m pytest
```

### Project Structure
- `main.py` - business logic, repository, normalization, and service layer
- `gui.py` - desktop GUI
- `workouts.json` - saved workout data
- `tests/test_main.py` - automated tests
