# Smart Task Analyzer

A Django-based intelligent task management system that scores and prioritizes tasks based on urgency, importance, effort, and dependencies.

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1.  **Clone or Navigate to the project directory**:
    ```bash
    cd c:/dev/SmartTaskAnalyzer
    ```

2.  **Install Dependencies**:
    ```bash
    pip install django djangorestframework
    ```

3.  **Apply Database Migrations**:
    ```bash
    python manage.py migrate
    ```

## Running the Application

1.  **Start the Development Server**:
    ```bash
    python manage.py runserver
    ```

2.  **Access the Application**:
    Open your web browser and go to:
    [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Features

- **Task Analysis**: Prioritize tasks using different strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven).
- **Suggestions**: Get the top 3 tasks to focus on today.
- **Bulk Import**: Paste a JSON list of tasks to analyze them in bulk.
- **Dependency Detection**: Automatically detects and warns about circular dependencies.

## API Endpoints

- `POST /api/tasks/analyze/`: Analyze and sort a list of tasks.
- `POST /api/tasks/suggest/`: Get top 3 suggestions.
