"""
Consolidated Auth & Verification:
Fields have been merged directly into the `student` table.
This module retains aliases for backward compatibility.
"""
from app.models.student import Student

AuthAccount = Student
