import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class Database:
    def __init__(self):
        self.users: Dict[str, Any] = {}
        self.courses: Dict[str, Any] = {}
        self.load_data()

    def load_data(self):
        try:
            with open("data/users.json", "r", encoding="utf-8") as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
    
        try:
            with open("data/courses.json", "r", encoding="utf-8") as f:
                self.courses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.courses = {}

    def save_data(self):
        with open("data/users.json", "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
        with open("data/courses.json", "w", encoding="utf-8") as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)

    def get_user(self, user_id: int) -> dict:
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                "free_generations": 10,
                "subscription_until": None,
                "invited_users": [],
                "completed_lessons": [],
                "premium": False,
            }
            self.save_data()
        return self.users[str(user_id)]

    def update_user(self, user_id: int, data: dict):
        self.users[str(user_id)] = data
        self.save_data()

    def get_lesson(self, lesson_number: int) -> Optional[dict]:
        return self.courses.get(str(lesson_number))

    def get_all_lessons(self) -> dict:
        return self.courses

    def add_lesson(self, lesson_number: int, lesson_data: dict):
        self.courses[str(lesson_number)] = lesson_data
        self.save_data()
        return lesson_number

db = Database()

