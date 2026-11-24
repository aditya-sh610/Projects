# VAY Travels - Tour Management System

A modular Tkinter-based application for managing tour bookings, with admin and user roles.

> Originally built as a 12th grade project, this application reflects a learning-stage approach rather than an industry-grade production system.

## Features
- User authentication (login/signup)
- Admin: Search, modify, view reviews, generate reports
- User: Make bookings, view history, write reviews
- Price calculation based on distance
- Animated background

## Project Structure
- `main.py`: Entry point
- `config.py`: Configuration constants
- `database.py`: Database operations
- `logic.py`: Business logic (validations, calculations)
- `ui.py`: UI components and windows
- `requirements.txt`: Dependencies

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Ensure MySQL is running with the database 'barry' and tables: passcheck, travels, hotels, coordinates
3. Optional database overrides: set `VAY_DB_HOST`, `VAY_DB_USER`, `VAY_DB_PASSWORD`, and `VAY_DB_NAME`
4. Run: `python main.py`


## Modularization
The original monolithic `FinalProject.py` has been split into:
- **Config**: Centralized constants for the project
- **Database**: All DB interactions in a class
- **Logic**: Reusable functions for calculations and validations
- **UI**: Window classes for better organization
- **Main**: Simple entry point

This improves maintainability, testability, and scalability.
