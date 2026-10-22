# SkillSwap JKLU — University Peer Mentoring & Campus Marketplace

**A Full-Stack Relational DBMS Capstone Project**  
*Department of Computer Science & Engineering, JK Lakshmipat University, Jaipur*

---

## 1. Project Overview & Academic Integrity
**SkillSwap JKLU** is an academic peer-to-peer mentoring and campus marketplace platform engineered specifically for **JK Lakshmipat University (JKLU), Jaipur**. It enables B.Tech, BBA, and B.Des students to discover peer mentors for 1-on-1 tutoring, build verified academic reputation, and securely buy and sell course supplies (textbooks, lab hardware, calculators).

### Core Academic Rules Enforced at Database Level:
1. **Universal Primary Key (`Roll_No`):** Every student is uniquely identified by their immutable roll number matching regex `^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$`.
2. **Strict Academic Domain Emails:** Only `@jklu.edu.in` addresses are allowed. Subdomain lookalikes (`evil-jklu.edu.in`) are strictly rejected.
3. **100% Free Mentorship Sessions:** Sessions are permanently free (`CHECK (credit_cost = 0)`).
4. **Non-Spendable Reputation Engine:** Mentors earn exactly **+10 reputation points** per completed session. Reputation points represent academic merit and cannot be spent, transferred, or deducted.
5. **ACID Concurrency Safety:**
   - **Session Completion:** Protected via `SELECT ... FOR UPDATE` row-level locking + unique `reputation_history(session_id)` constraint.
   - **Marketplace Purchases:** Atomically executed via conditional update `UPDATE listing SET status='SOLD', buyer_roll_no=:buyer WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer`.

---

## 2. Technology Stack

- **Backend:** Python 3.12+, FastAPI 0.115+, SQLAlchemy 2.0 (modern 2.0 syntax), Pydantic v2, Alembic, PyMySQL, Argon2 (`argon2-cffi`), PyJWT, SlowAPI, Pytest + TestClient.
- **Frontend:** React 18+, Vite, Tailwind CSS, React Router v6, Axios, Lucide React, Recharts.
- **Database:** MySQL 8.0+ Community Server, InnoDB storage engine, `utf8mb4` encoding. Primary dev database `skillswap`, test database `skillswap_test`.

---

## 3. Relational Schema & Normalization (BCNF / 3NF)

| Table | Primary Key | Description & Integrity Constraints |
|---|---|---|
| `department` | `d_id` (INT AUTO_INCREMENT) | University academic departments. Unique constraint on `name`. |
| `student` | `roll_no` (VARCHAR(12)) | Universal PK. Format regex CHECK, program CHECK, non-negative reputation CHECK. |
| `auth_account` | `roll_no` (VARCHAR(12)) | 1-to-1 extension of student. Argon2 password hash, token version invalidation, role ENUM. |
| `email_verification_token` | `token_id` (INT) | SHA-256 hashed 24-hour verification token lifecycle. |
| `skill` | `skill_id` (INT AUTO_INCREMENT) | Accredited competencies catalog across CS, AI, Management, Design, and Hardware. |
| `student_skill` | `(roll_no, skill_id)` | Composite PK. Many-to-many relationship with proficiency levels and `can_teach` flag. |
| `learning_session` | `session_id` (INT) | Explicit state machine (`REQUESTED`, `ACCEPTED`, `COMPLETED`, `CANCELLED`, `REJECTED`). `credit_cost = 0`. |
| `reputation_history` | `history_id` (INT) | Audit ledger of reputation awards. Unique on `session_id` preventing double rewards. |
| `review` | `(session_id, roll_no)` | 1 to 5 star rating + feedback. Check constraint `roll_no <> reviewee_roll_no`. |
| `experience` | `(roll_no, exp_no)` | Weak entity portfolio items (Internships, Projects, Hackathons). Date consistency CHECK. |
| `listing` | `listing_id` (INT) | Student marketplace items. Concurrency-safe atomic purchasing state. |

---

## 4. 34 Required Demonstration SQL Queries

The file [`backend/database/test_queries.sql`](file:///c:/Users/hansi/OneDrive/Documents/Desktop/JKLU%20SKILLSWAP/backend/database/test_queries.sql) contains **34 comprehensive, verified SQL queries** demonstrating the complete spectrum of DBMS techniques:

- **Queries 1–5:** `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`, `START TRANSACTION` / `ROLLBACK`, multi-table `INNER JOIN`, self-joins, window functions (`DENSE_RANK()`).
- **Queries 6–10:** Correlated subqueries, `HAVING`, pattern matching with `REGEXP`, set operations (`UNION`), `CASE` expressions.
- **Queries 11–15:** Aggregations (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`), date-time arithmetic, `LEFT JOIN` detecting nulls, `EXISTS`, nested queries in `FROM`.
- **Queries 16–20:** String functions (`SUBSTRING`, `LENGTH`, `CONCAT`), `NOT IN` outer joins, `COALESCE`, running totals via window functions (`SUM() OVER`), parameterized queries (`@roll`).
- **Queries 21–25:** Multi-table joins with 4+ entities, `GROUP_CONCAT`, `COUNT(DISTINCT)`, nested aggregations.
- **Queries 26–34:** Full inventory left join, program cohort breakdowns, session status percentage distributions, rating threshold filters (`@min_rating`), skill sharing matrix, roll_no year extraction, versatile mentor detection, and bilateral mentor/learner analysis.

To execute all 34 queries in native MySQL 8.0:
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u skillswap -pskillswap_pass -h 127.0.0.1 -P 3307 skillswap -e "source backend/database/test_queries.sql"
```

---

## 5. Automated Pytest Verification Suite (100% Pass Rate)

The test suite contains **24 comprehensive automated integration tests**:

```powershell
backend\.venv\Scripts\pytest -v
```

### Verified Test Gates:
1. `test_auth.py` (6 tests): Universal roll regex, lookalike domain rejection (`evil-jklu.edu.in`), token lifecycle, JWT invalidation, admin approval.
2. `test_health.py` (3 tests): `/health` endpoint returning database connected status, `/docs` Swagger UI, `/api/v1/openapi.json`.
3. `test_students_skills.py` (5 tests): Profile CRUD, roll_no immutability, skills catalog, mentor discovery filters.
4. `test_learning.py` (5 tests): Explicit session state machine, review constraints, portfolio CRUD, **safe multi-threaded concurrent session completion (SELECT FOR UPDATE)**.
5. `test_marketplace.py` (5 tests): Inventory filtering, self-purchase prevention, **multi-threaded atomic purchase concurrency test (5 threads, exactly 1 success, 4 HTTP 409 conflicts)**, leaderboard `DENSE_RANK`, and campus analytics.

---

## 6. How to Run Locally

### Prerequisites
- Python 3.12+
- Node.js v20+ / v24+
- MySQL 8.0+ (running on port 3306 or 3307)

### 1. Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and load seed data
alembic upgrade head
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u skillswap -pskillswap_pass -h 127.0.0.1 -P 3307 skillswap < database/seed.sql

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
Swagger UI interactive docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 7. Demonstration Personas & Demo Logins

The application features **One-Click Quick Demo Login** buttons on the login page:

| Persona | Roll Number | Role | Reputation | Teachable Specialties |
|---|---|---|---|---|
| **Aarav Sharma (Admin)** | `2024BTECH001` | `ADMIN` | 40 pts | Python, Data Structures, DBMS |
| **Bhavya Patel (Student)** | `2024BTECH002` | `STUDENT` | 50 pts (Top Mentor) | React, Machine Learning, Python |
| **Sneha Agarwal (Student)** | `2024BBA001` | `STUDENT` | 30 pts | Financial Accounting, Business Valuation |
| **Bharat Bhushan (Student)** | `2024BDES001` | `STUDENT` | 30 pts | UI/UX Wireframing, Graphic Design |

*Default Demo Password for all seed students:* `Student@JKLU2026`  
*Admin Password:* `Admin@JKLU2026`
