from dataclasses import dataclass
from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Department(Base):
    __tablename__ = "department"

    d_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    program: Mapped[str] = mapped_column(
        Enum("BTECH", "BBA", "BDES", name="dept_program_enum"),
        nullable=False
    )


@dataclass(frozen=True)
class DepartmentSpec:
    d_id: int
    name: str
    program: str


PREDEFINED_DEPARTMENTS = [
    DepartmentSpec(1, "Computer Science and Engineering", "BTECH"),
    DepartmentSpec(2, "Artificial Intelligence and Data Science", "BTECH"),
    DepartmentSpec(3, "Electronics and Communication Engineering", "BTECH"),
    DepartmentSpec(4, "Institute of Management", "BBA"),
    DepartmentSpec(5, "Institute of Design", "BDES"),
]

DEFAULT_DEPT_ID_BY_PROGRAM = {
    "BTECH": 1,
    "BBA": 4,
    "BDES": 5,
}
