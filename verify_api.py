import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_analyze_tasks():
    print("Testing /api/tasks/analyze/...")
    tasks = [
        {"id": 1, "title": "Task A", "estimated_hours": 2, "importance": 8, "due_date": "2025-12-01"},
        {"id": 2, "title": "Task B", "estimated_hours": 10, "importance": 5, "due_date": "2025-12-05"},
        {"id": 3, "title": "Task C", "estimated_hours": 1, "importance": 9, "due_date": "2025-11-29", "dependencies": [1]}
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/api/tasks/analyze/?strategy=smart_balance", json=tasks)
        if response.status_code == 200:
            results = response.json()
            print("SUCCESS: Analyze endpoint returned 200")
            print(f"Returned {len(results)} tasks.")
            print(f"Top task: {results[0]['title']} (Score: {results[0]['score']})")
        else:
            print(f"FAILURE: Analyze endpoint returned {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")

def test_suggest_tasks():
    print("\nTesting /api/tasks/suggest/...")
    tasks = [
        {"id": 1, "title": "Task A", "estimated_hours": 2, "importance": 8},
        {"id": 2, "title": "Task B", "estimated_hours": 10, "importance": 5},
        {"id": 3, "title": "Task C", "estimated_hours": 1, "importance": 9},
        {"id": 4, "title": "Task D", "estimated_hours": 5, "importance": 7}
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/api/tasks/suggest/", json=tasks)
        if response.status_code == 200:
            results = response.json()
            print("SUCCESS: Suggest endpoint returned 200")
            print(f"Returned {len(results)} suggestions (expected 3).")
        else:
            print(f"FAILURE: Suggest endpoint returned {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Ensure server is running before running this script
    test_analyze_tasks()
    test_suggest_tasks()
