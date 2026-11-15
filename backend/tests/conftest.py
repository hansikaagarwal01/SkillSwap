import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.config import settings
from app.db.base import Base
from app.core.dependencies import get_db, limiter
import app.db.session as db_session
from app.main import app
from app.core.security import get_password_hash
from app.models.student import Student
from app.models.department import Department, PREDEFINED_DEPARTMENTS
from app.models.skill import Skill, StudentSkill
from app.models.listing import Listing
from app.models.session import LearningSession
from app.models.review import Review

test_engine = create_engine(
    settings.TEST_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Monkeypatch SessionLocal in app.db.session so all tests and services connect to skillswap_test
db_session.SessionLocal = TestingSessionLocal
db_session.engine = test_engine

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
limiter.enabled = False

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Seed test fixtures into skillswap_test database."""
    # Ensure tables exist in skillswap_test
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        # Clear previous test data in child-first order
        if "notification" in Base.metadata.tables:
            db.execute(Base.metadata.tables["notification"].delete())
        if "marketplace_inquiry" in Base.metadata.tables:
            db.execute(Base.metadata.tables["marketplace_inquiry"].delete())
        db.execute(Base.metadata.tables["review"].delete())
        db.execute(Base.metadata.tables["learning_session"].delete())
        db.execute(Base.metadata.tables["listing"].delete())
        db.execute(Base.metadata.tables["experience"].delete())
        db.execute(Base.metadata.tables["student_skill"].delete())
        db.execute(Base.metadata.tables["student_desired_skill"].delete())
        if "survey_import_audit" in Base.metadata.tables:
            db.execute(Base.metadata.tables["survey_import_audit"].delete())
        db.execute(Base.metadata.tables["skill"].delete())
        db.execute(Base.metadata.tables["student"].delete())
        db.commit()

        # Seed canonical departments
        for dept_spec in PREDEFINED_DEPARTMENTS:
            db.merge(Department(d_id=dept_spec.d_id, name=dept_spec.name, program=dept_spec.program))
        db.commit()

        default_pw = get_password_hash("Student@JKLU2026")
        admin_pw = get_password_hash("Admin@JKLU2026")

        # 1. Seed Core Test Students
        core_students = [
            Student(
                roll_no="2024BTECH001",
                name="Aarav Sharma",
                email="aarav.sharma@jklu.edu.in",
                program="BTECH",
                admission_year=2024,
                reputation_points=50,
                password_hash=admin_pw,
                role="ADMIN",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BTECH002",
                name="Bhavya Patel",
                email="bhavya.patel@jklu.edu.in",
                program="BTECH",
                admission_year=2024,
                reputation_points=30,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BTECH003",
                name="Chirag Singhal",
                email="chirag.singhal@jklu.edu.in",
                program="BTECH",
                admission_year=2024,
                reputation_points=20,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BTECH004",
                name="Divyansh Joshi",
                email="divyansh.joshi@jklu.edu.in",
                program="BTECH",
                admission_year=2024,
                reputation_points=10,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BTECH005",
                name="Eshan Verma",
                email="eshan.verma@jklu.edu.in",
                program="BTECH",
                admission_year=2024,
                reputation_points=15,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BTECH006",
                name="Farhan Ali",
                email="farhan.ali@jklu.edu.in",
                program="BTECH",
                admission_year=2024,
                reputation_points=10,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2025BTECH007",
                name="Gauri Mittal",
                email="gauri.mittal@jklu.edu.in",
                program="BTECH",
                admission_year=2025,
                reputation_points=25,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BBA001",
                name="Sneha Agarwal",
                email="sneha.agarwal@jklu.edu.in",
                program="BBA",
                admission_year=2024,
                reputation_points=20,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2024BBA002",
                name="Rohan Mehta",
                email="rohan.mehta@jklu.edu.in",
                program="BBA",
                admission_year=2024,
                reputation_points=10,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2025BDES001",
                name="Tanvi Jain",
                email="tanvi.jain@jklu.edu.in",
                program="BDES",
                admission_year=2025,
                reputation_points=15,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2025BDES002",
                name="Ananya Rao",
                email="ananya.rao@jklu.edu.in",
                program="BDES",
                admission_year=2025,
                reputation_points=10,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2026BTECH016",
                name="Kavya Mathur",
                email="kavya.mathur@jklu.edu.in",
                program="BTECH",
                admission_year=2026,
                reputation_points=0,
                password_hash=default_pw,
                role="STUDENT",
                account_status="UNVERIFIED",
                email_verified=False
            ),
            Student(
                roll_no="2026BTECH017",
                name="Lakshay Gupta",
                email="lakshay.gupta@jklu.edu.in",
                program="BTECH",
                admission_year=2026,
                reputation_points=0,
                password_hash=default_pw,
                role="STUDENT",
                account_status="ACTIVE",
                email_verified=True
            ),
            Student(
                roll_no="2026BTECH018",
                name="Manan Sharma",
                email="manan.sharma@jklu.edu.in",
                program="BTECH",
                admission_year=2026,
                reputation_points=0,
                password_hash=default_pw,
                role="STUDENT",
                account_status="SUSPENDED",
                email_verified=True
            ),
        ]

        # Additional cohort students to guarantee total >= 30
        cohort_students = []
        for i in range(20, 45):
            cohort_students.append(
                Student(
                    roll_no=f"2024BTECH{i:03d}",
                    name=f"Cohort Student {i}",
                    email=f"cohort.student{i}@jklu.edu.in",
                    program="BTECH",
                    admission_year=2024,
                    reputation_points=5,
                    password_hash=default_pw,
                    role="STUDENT",
                    account_status="ACTIVE",
                    email_verified=True
                )
            )

        db.add_all(core_students + cohort_students)
        db.commit()

        # 2. Seed Skills (>= 18 skills)
        skills_data = [
            (1, "Python Programming", "Computer Science", "Core Python programming and scripting"),
            (2, "Web Development", "Computer Science", "Fullstack web development"),
            (3, "React", "Computer Science", "Modern frontend with React"),
            (4, "Machine Learning", "Data Science", "Supervised and unsupervised learning"),
            (5, "Data Structures & Algorithms", "Computer Science", "Problem solving in C++ and Java"),
            (6, "Database Management Systems", "Computer Science", "Relational database design and SQL"),
            (7, "Cloud Computing", "Computer Science", "AWS, GCP and serverless deployment"),
            (8, "UI/UX Design", "Design", "User interface wireframing and prototyping with Figma"),
            (9, "Graphic Design", "Design", "Vector illustration and visual identity"),
            (10, "Digital Marketing", "Business", "SEO, content strategy and paid advertising"),
            (11, "Financial Accounting", "Business", "Balance sheets, ledger accounting and financial analysis"),
            (12, "Public Speaking", "Soft Skills", "Presentation skills, debate and leadership communication"),
            (13, "Guitar", "Music", "Acoustic and electric guitar fundamentals"),
            (14, "Cybersecurity", "Computer Science", "Network security and ethical hacking"),
            (15, "Photography", "Media", "Digital camera handling and photo editing"),
            (16, "Embedded Systems", "Electronics", "Microcontrollers, Arduino and IoT"),
            (17, "AutoCAD", "Engineering", "2D and 3D computer aided drafting"),
            (18, "Business Communication", "Business", "Corporate correspondence and report writing")
        ]
        skills_objs = [
            Skill(skill_id=s_id, name=s_name, category=s_cat, description=s_desc)
            for s_id, s_name, s_cat, s_desc in skills_data
        ]
        db.add_all(skills_objs)
        db.commit()

        # 3. Seed Mentors (StudentSkill with can_teach = True, total >= 10)
        mentor_skills = [
            StudentSkill(roll_no="2024BTECH001", skill_id=1, proficiency_level="EXPERT", can_teach=True),
            StudentSkill(roll_no="2024BTECH002", skill_id=1, proficiency_level="ADVANCED", can_teach=True),
            StudentSkill(roll_no="2024BTECH002", skill_id=2, proficiency_level="INTERMEDIATE", can_teach=True),
            StudentSkill(roll_no="2024BTECH003", skill_id=4, proficiency_level="ADVANCED", can_teach=True),
            StudentSkill(roll_no="2024BTECH004", skill_id=5, proficiency_level="ADVANCED", can_teach=True),
            StudentSkill(roll_no="2024BTECH005", skill_id=16, proficiency_level="EXPERT", can_teach=True),
            StudentSkill(roll_no="2024BTECH006", skill_id=7, proficiency_level="ADVANCED", can_teach=True),
            StudentSkill(roll_no="2025BTECH007", skill_id=8, proficiency_level="EXPERT", can_teach=True),
            StudentSkill(roll_no="2024BBA001", skill_id=10, proficiency_level="EXPERT", can_teach=True),
            StudentSkill(roll_no="2024BBA002", skill_id=11, proficiency_level="ADVANCED", can_teach=True),
            StudentSkill(roll_no="2025BDES001", skill_id=9, proficiency_level="EXPERT", can_teach=True),
            StudentSkill(roll_no="2025BDES002", skill_id=15, proficiency_level="ADVANCED", can_teach=True),
        ]
        db.add_all(mentor_skills)
        db.commit()

        # 4. Seed Learning Sessions (>= 30 sessions)
        past_time = datetime.now(timezone.utc) - timedelta(days=2)
        sessions = [
            # Session 1: COMPLETED, mentor 2024BTECH001, learner 2025BTECH007
            LearningSession(
                session_id=1,
                mentor_roll_no="2024BTECH001",
                learner_roll_no="2025BTECH007",
                skill_id=1,
                topic="Advanced Python Metaprogramming",
                mode="ONLINE",
                scheduled_at=past_time,
                status="COMPLETED",
                credit_cost=0,
                reputation_awarded=True,
                points_awarded=10,
                reputation_awarded_at=past_time
            ),
            # Session 31: ACCEPTED
            LearningSession(
                session_id=31,
                mentor_roll_no="2024BTECH001",
                learner_roll_no="2024BTECH002",
                skill_id=1,
                topic="FastAPI Asynchronous Microservices",
                mode="ONLINE",
                scheduled_at=past_time,
                status="ACCEPTED",
                credit_cost=0
            )
        ]
        # Sessions 2-30 and 32
        for sid in range(2, 31):
            sessions.append(
                LearningSession(
                    session_id=sid,
                    mentor_roll_no="2024BTECH002",
                    learner_roll_no="2024BTECH003",
                    skill_id=1,
                    topic=f"Peer Learning Session {sid}",
                    mode="ONLINE",
                    scheduled_at=past_time,
                    status="COMPLETED",
                    credit_cost=0,
                    reputation_awarded=True,
                    points_awarded=10,
                    reputation_awarded_at=past_time
                )
            )
        sessions.append(
            LearningSession(
                session_id=32,
                mentor_roll_no="2024BTECH001",
                learner_roll_no="2024BTECH004",
                skill_id=1,
                topic="Python Testing Frameworks",
                mode="ONLINE",
                scheduled_at=past_time,
                status="COMPLETED",
                credit_cost=0,
                reputation_awarded=True,
                points_awarded=10,
                reputation_awarded_at=past_time
            )
        )
        db.add_all(sessions)
        db.commit()

        # 5. Seed Reviews (including Session 1 review by Gauri for Aarav)
        reviews = [
            Review(
                session_id=1,
                roll_no="2025BTECH007",
                reviewee_roll_no="2024BTECH001",
                rating=5,
                comment="Aarav is an outstanding mentor with deep Python knowledge!"
            ),
            Review(
                session_id=2,
                roll_no="2024BTECH003",
                reviewee_roll_no="2024BTECH002",
                rating=5,
                comment="Bhavya explained web development clearly and patiently."
            )
        ]
        db.add_all(reviews)
        db.commit()

        # 6. Seed Listings (>= 10 listings, including Textbooks, Calculator, AVAILABLE, SOLD)
        listings_data = [
            Listing(
                listing_id=1,
                seller_roll_no="2024BTECH001",
                title="Data Structures and Algorithms in C++",
                description="Comprehensive reference textbook in excellent condition.",
                price=350.00,
                original_price_text="350",
                category="Textbooks",
                item_condition="GOOD",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=2,
                seller_roll_no="2024BTECH002",
                title="Casio fx-991ES Plus Scientific Calculator",
                description="Essential scientific calculator for engineering mathematics.",
                price=650.00,
                original_price_text="650",
                category="Campus Essentials",
                item_condition="LIKE_NEW",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=3,
                seller_roll_no="2024BTECH003",
                title="Database System Concepts 7th Edition Silberschatz",
                description="Prescribed textbook for DBMS course, minimal highlighting.",
                price=450.00,
                original_price_text="450",
                category="Textbooks",
                item_condition="GOOD",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=4,
                seller_roll_no="2024BTECH004",
                title="Arduino Uno R3 Starter Kit with Sensors",
                description="Complete electronics development kit with jumper wires and breadboard.",
                price=850.00,
                original_price_text="850",
                category="Electronics",
                item_condition="LIKE_NEW",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=5,
                seller_roll_no="2024BTECH005",
                title="Engineering Drawing Board with Mini Drafter",
                description="Standard university drawing board with T-square and clips.",
                price=500.00,
                original_price_text="500",
                category="Stationery",
                item_condition="GOOD",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=6,
                seller_roll_no="2024BBA001",
                title="Financial Accounting Principles Textbook",
                description="Core reference book for introductory accounting.",
                price=300.00,
                original_price_text="300",
                category="Textbooks",
                item_condition="GOOD",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=7,
                seller_roll_no="2025BDES001",
                title="A3 Sketchbook and Professional Charcoal Set",
                description="Brand new sketchpad with assorted charcoal pencils.",
                price=220.00,
                original_price_text="220",
                category="Stationery",
                item_condition="NEW",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=8,
                seller_roll_no="2024BTECH006",
                title="Computer Networking Top-Down Approach",
                description="Kurose and Ross 8th Edition textbook in mint condition.",
                price=400.00,
                original_price_text="400",
                category="Textbooks",
                item_condition="LIKE_NEW",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=9,
                seller_roll_no="2025BTECH007",
                title="Rechargeable LED Desk Study Lamp",
                description="Three color temperature settings with flexible neck.",
                price=320.00,
                original_price_text="320",
                category="Campus Essentials",
                item_condition="LIKE_NEW",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=10,
                seller_roll_no="2024BTECH001",
                title="STM32 Nucleo Development Board",
                description="ARM Cortex-M4 microcontroller evaluation board.",
                price=750.00,
                original_price_text="750",
                category="Electronics",
                item_condition="LIKE_NEW",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=11,
                seller_roll_no="2024BTECH002",
                title="Digital Logic and Computer Design Morris Mano",
                description="Essential hardware design book.",
                price=280.00,
                original_price_text="280",
                category="Textbooks",
                item_condition="GOOD",
                status="AVAILABLE"
            ),
            Listing(
                listing_id=12,
                seller_roll_no="2024BTECH001",
                buyer_roll_no="2024BTECH003",
                title="Sold Engineering Mathematics Textbook",
                description="Previous semester textbook successfully sold.",
                price=250.00,
                original_price_text="250",
                category="Textbooks",
                item_condition="GOOD",
                status="SOLD",
                sold_at=past_time
            ),
        ]
        db.add_all(listings_data)
        db.commit()

    finally:
        db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
