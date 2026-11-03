# SkillSwap JKLU — University Peer Mentoring & Campus Marketplace

**A Full-Stack Relational DBMS Capstone Project**  
*Department of Computer Science & Engineering, JK Lakshmipat University, Jaipur*

---

## 1. Project Overview & Academic Integrity
**SkillSwap JKLU** is an authentic academic peer-to-peer mentoring and campus marketplace platform engineered specifically for **JK Lakshmipat University (JKLU), Jaipur**. It represents real JKLU students across B.Tech, BBA, and B.Des programs, enabling students to discover peers by possessed and desired skills, request 1-on-1 peer learning sessions, and buy/sell university course materials.

### Core Academic Rules Enforced at Database Level:
1. **Universal Primary Key (`Roll_No`):** Every student is uniquely identified by their immutable roll number matching regex `^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$`.
2. **Strict Academic Domain Emails:** Only official `@jklu.edu.in` addresses are allowed. Subdomain lookalikes (`evil-jklu.edu.in`, `jklu.edu.in.evil.com`) are strictly rejected.
3. **100% Free Mentorship Sessions:** Sessions are permanently free (`CHECK (credit_cost = 0)`).
4. **Non-Spendable Reputation Engine:** Mentors earn exactly **+10 reputation points** per completed session. Reputation points represent academic merit and cannot be spent, transferred, or deducted.
5. **ACID Concurrency Safety:**
   - **Session Completion:** Protected via `SELECT ... FOR UPDATE` row-level locking + reputation audit flag checking.
   - **Marketplace Purchases:** Atomically executed via conditional update `UPDATE listing SET status='SOLD', buyer_roll_no=:buyer, sold_at=NOW() WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer`.
6. **Zero Fabricated Demo Data in Production:** All 34 student profiles, 102 distinct skills, and 9 marketplace listings originate directly from the authentic JKLU student survey (`SkillSwap_Website_Cleaned_Data_Original_Columns.xlsx`). No fake reviews or artificial sessions exist in the production database.

---

## 2. Technology Stack

- **Backend:** Python 3.12+, FastAPI 0.115+, SQLAlchemy 2.0 (modern 2.0 syntax), Pydantic v2, Alembic, PyMySQL, Argon2 (`argon2-cffi`), PyJWT, SlowAPI, Pytest + TestClient.
- **Frontend:** React 18+, Vite, Tailwind CSS, React Router v6, Axios, Lucide React, Recharts.
- **Database:** MySQL 8.0+ Community Server, InnoDB storage engine, `utf8mb4` encoding. Primary dev/evaluation database `skillswap`, automated test database `skillswap_test`.

---

## 3. Relational Schema & Normalization (BCNF / 3NF)

| Table | Primary Key | Description & Integrity Constraints |
|---|---|---|
| `student` | `roll_no` (VARCHAR(12)) | Universal PK. Format regex CHECK, program CHECK, non-negative reputation CHECK. Holds authentic survey profiles, Argon2 password hash (claimed on first login), account status, and email verification tokens. Strictly normalized in BCNF. |
| `skill` | `skill_id` (INT AUTO_INCREMENT) | Accredited competencies catalog (102 distinct skills). Unique indexed `name`. |
| `student_skill` | `(roll_no, skill_id)` | Composite PK. Possessed skills captured from survey responses. Defaults to `can_teach = FALSE` until student enables mentorship. |
| `student_desired_skill` | `(roll_no, skill_id)` | Composite PK. Learning goals captured from survey responses ("What skills would you like to learn?"). |
| `learning_session` | `session_id` (INT) | Explicit state machine (`REQUESTED`, `ACCEPTED`, `COMPLETED`, `CANCELLED`, `REJECTED`). `credit_cost = 0`. Embedded atomic reputation award audit (`points_awarded`, `reputation_awarded`, `reputation_awarded_at`). |
| `review` | `(session_id, roll_no)` | 1 to 5 star rating + feedback. Check constraint `roll_no <> reviewee_roll_no`. Populates dynamically upon session completions. |
| `experience` | `(roll_no, exp_no)` | Weak entity portfolio items (Internships, Projects, Hackathons). Date consistency CHECK (`end_date >= start_date`). |
| `listing` | `listing_id` (INT) | Authentic survey marketplace items. Concurrency-safe atomic purchasing state. Stores numeric `price` alongside verbatim `original_price_text` (e.g., "₹99 per subject"). |
| `survey_import_audit` | `audit_id` (INT AUTO_INCREMENT) | Immutable audit log of all 36 original survey submissions, records normalization decisions and duplicate resolutions. |

---

## 4. Evaluation Guide for MySQL Workbench & 34 Demonstration SQL Queries

The file [`backend/database/test_queries.sql`](file:///c:/Users/hansi/OneDrive/Documents/Desktop/JKLU%20SKILLSWAP/backend/database/test_queries.sql) contains **34 comprehensive, verified SQL queries** demonstrating the complete spectrum of relational DBMS techniques:

- **Queries 1–5:** `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`, `START TRANSACTION` / `ROLLBACK`, multi-table `INNER JOIN`, self-joins, window functions (`DENSE_RANK()`).
- **Queries 6–10:** Correlated subqueries, `HAVING`, pattern matching with `REGEXP`, set operations (`UNION`), `CASE` expressions.
- **Queries 11–15:** Aggregations (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`), date-time arithmetic, `LEFT JOIN` detecting nulls, `EXISTS`, nested queries in `FROM`.
- **Queries 16–20:** String functions (`SUBSTRING`, `LENGTH`, `CONCAT`), `NOT IN` outer joins, `COALESCE`, running totals via window functions (`SUM() OVER`), parameterized queries (`@roll`).
- **Queries 21–25:** Multi-table joins with 4+ entities, `GROUP_CONCAT`, `COUNT(DISTINCT)`, nested aggregations.
- **Queries 26–34:** Full inventory left join, program cohort breakdowns, session status percentage distributions, rating threshold filters, skill sharing matrix, roll_no year extraction, versatile mentor detection, and bilateral mentor/learner analysis.

### Connecting via MySQL Workbench:
1. Open MySQL Workbench and create a new connection:
   - **Hostname:** `127.0.0.1`
   - **Port:** `3306`
   - **Username:** `skillswap` (or `root`)
   - **Password:** `skillswap_pass` (or root password)
   - **Default Schema:** `skillswap`
2. Open `backend/database/test_queries.sql` in Workbench (`File` $\to$ `Open SQL Script...`).
3. Click the Execute button (lightning bolt) to run all 34 queries. All 43 statements execute with 0 errors.

### Verifying via Command Line:
```powershell
$env:PYTHONPATH='backend'
backend\.venv\Scripts\python backend/verify_test_queries.py
```
*Expected Output: `Total statements executed: 43 | Errors encountered: 0`*

---

## 5. Automated Pytest Verification Suite (100% Pass Rate)

The automated test suite runs against the isolated `skillswap_test` database, guaranteeing zero side effects on the production survey database:

```powershell
backend\.venv\Scripts\pytest -v
```

### Verified Test Gates (24 Passed / 0 Failed):
1. `backend/tests/test_auth.py` (6 tests): Universal roll regex, lookalike domain rejection (`evil-jklu.edu.in`), token lifecycle, JWT invalidation, admin approval.
2. `backend/tests/test_health.py` (3 tests): `/health` endpoint returning database connected status, `/docs` Swagger UI, `/api/v1/openapi.json`.
3. `backend/tests/test_students_skills.py` (5 tests): Profile CRUD, roll_no immutability, skills catalog, mentor discovery filters.
4. `backend/tests/test_learning.py` (5 tests): Explicit session state machine, review constraints, portfolio CRUD, **safe multi-threaded concurrent session completion (SELECT FOR UPDATE)**.
5. `backend/tests/test_marketplace.py` (5 tests): Inventory filtering, self-purchase prevention, **multi-threaded atomic purchase concurrency test (5 threads, exactly 1 success, 4 HTTP 409 conflicts)**, leaderboard `DENSE_RANK`, and campus analytics.

---

## 6. How to Run Locally

### Prerequisites
- Python 3.12+
- Node.js v20+ / v24+
- MySQL 8.0+ (running on port 3306)

### 1. Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

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

## 7. Account Claiming Workflow for Survey Students

Imported survey students start in an unverified state (`account_status = 'UNVERIFIED'`, `password_hash = NULL`) for security. Real students claim their profile by registering with their official `@jklu.edu.in` email:

1. Navigate to `http://localhost:5173/register`.
2. Enter your valid JKLU Roll Number (e.g., `2025BTECH027`), Name, official JKLU Email, and secure password.
3. The platform matches your roll number to the survey entry, links your possessed and desired skills, securely hashes your password using Argon2id, and sends an email verification link.
4. Once verified, log in to access your dashboard, customize your profile, and enable mentoring.
