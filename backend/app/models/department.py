from dataclasses import dataclass

@dataclass
class Department:
    """Static catalog representation for academic departments."""
    d_id: int
    name: str
    program: str

PREDEFINED_DEPARTMENTS = [
    Department(1, "Computer Science and Engineering", "BTECH"),
    Department(2, "Artificial Intelligence and Data Science", "BTECH"),
    Department(3, "Electronics and Communication Engineering", "BTECH"),
    Department(4, "Institute of Management", "BBA"),
    Department(5, "Institute of Design", "BDES"),
]
