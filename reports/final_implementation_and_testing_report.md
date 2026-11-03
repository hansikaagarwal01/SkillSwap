# SkillSwap JKLU — Real Survey Data Integration, Complete Website Cleanup & End-to-End Audit Report

**Project:** SkillSwap JKLU — University Peer Mentoring & Campus Marketplace  
**Institution:** Department of Computer Science & Engineering, JK Lakshmipat University, Jaipur  
**Course:** Relational Database Management Systems (DBMS) Capstone Project  
**Target RDBMS:** MySQL 8.0+ Community Server (InnoDB Engine, utf8mb4)  
**Execution Date:** November 3, 2026  

---

## 1. Executive Summary

This audit report documents the complete data migration, codebase sanitization, relational verification, and end-to-end testing of **SkillSwap JKLU**. 

All artificial demo profiles, fabricated skills, fake session reviews, and simulated marketplace transactions were purged from the production database. The system now runs exclusively on authentic student survey responses collected from the JKLU student community via `SkillSwap_Website_Cleaned_Data_Original_Columns.xlsx`.

### Key Achievements:
- **100% Authentic JKLU Data:** 36 survey rows processed into 34 verified student profiles, 102 normalized skills, 89 possessed skill mappings, 83 desired learning goals, and 9 authentic student marketplace listings.
- **Relational DBMS Rigor:** 8 normalized tables adhering to Boyce-Codd Normal Form (BCNF) / 3NF, plus an immutable survey audit table. `Roll_No` serves as the universal immutable Primary Key across all relations.
- **Flawless SQL Execution:** All **34 required demonstration SQL queries** (43 SQL statements) were executed on the live MySQL 8.0 database with a **100% pass rate (0 errors)**.
- **100% Automated Pytest Pass Rate:** All **24 backend integration tests** pass cleanly against an isolated test database (`skillswap_test`), proving atomic concurrency, session state machines, and RBAC security.
- **UI & Corporate Palette Alignment:** Completely stripped fake demo logins, decorative emojis, and simulated rankings. Aligned with the formal academic beige palette (`#F7F3EC`, `#EFE9DF`, `#FCFAF6`, `#2B2926`, `#6F6A63`, `#D8D1C5`, `#8A6A4A`).

---

## 2. Complete Data Quality & Survey Import Report

The source dataset `SkillSwap_Website_Cleaned_Data_Original_Columns.xlsx` contained 36 raw submissions from the JKLU student body.

```
Total Survey Rows Submitted:    36
Unique Students Identified:      34
Duplicate Submissions Merged:     2
Confirmed Roll Corrections:       2
Valid Students Imported:         34
Incomplete Records Flagged:       1 (Marketplace)
Invalid Roll Numbers:             0
Invalid Email Domains:            0
```

### A. Confirmed Roll-Number Corrections
Per instructions and student registry verification, two survey entries with irregular roll number inputs were automatically corrected:

| Original Input | Corrected `Roll_No` | Program | Student Name | Reason for Correction |
|---|---|---|---|---|
| `004` | `2026BBA004` | BBA | Agam jain | Truncated entry; verified against BBA 2026 cohort registry |
| `147btech2026` | `2026BTECH147` | BTECH | Harshit Adhikari | Inverted format normalized to standard university pattern |

### B. Duplicate Submissions Merged
Two students submitted the survey twice. They were consolidated into single authoritative student records while preserving both submissions in `survey_import_audit`:

1. **Dhruv Tyagi (`2025BTECH023`):**
   - *Submission 1 (20:45:34):* Generic non-academic skills.
   - *Submission 2 (20:54:17):* Specific skills: `Baking`, `Guitar`, desired `Communication`.
   - *Resolution:* Merged into profile `2025BTECH023` with specific skills.
2. **Dhanyashree Sen (`2025BTECH022`):**
   - *Submission 1 (20:32:21):* Listed skill `Writing`.
   - *Submission 2 (21:53:52):* Marked `Not specified`.
   - *Resolution:* Merged into profile `2025BTECH022` preserving `Writing`.

### C. Records Requiring Manual Review
One marketplace submission contained an expected price but omitted the item title and description:
- **Student:** Hiranand Nainwani (`2026BBA050`)
- **Submitted Price:** `99/-`
- **Submitted Title & Description:** *(empty)*
- **Resolution:** Student profile and skills were imported successfully; the incomplete marketplace listing was flagged and held unpublished. Exported to `reports/records_requiring_manual_review.csv`.

### D. Student Cohort Breakdown

| Program | Admission Year | Student Count | Percentage |
|---|---|---|---|
| **B.Tech (CSE/AI)** | 2025 | 18 | 52.9% |
| **B.Tech (CSE/AI)** | 2026 | 10 | 29.4% |
| **BBA** | 2026 | 6 | 17.6% |
| **Total** | — | **34** | **100.0%** |

---

## 3. Database Architecture & Schema Integrity

### A. Relational Schema Summary
The database utilizes 8 core entities plus 1 audit entity:

| Table Name | Primary Key | Foreign Keys | Normal Form | Purpose |
|---|---|---|---|---|
| `student` | `roll_no` | *None* | BCNF | Universal student entity. Stores roll number, name, email, program, admission year, reputation points, Argon2 password hash, and verification status. |
| `skill` | `skill_id` | *None* | BCNF | Master catalog of 102 distinct skills. `name` is unique and indexed. |
| `student_skill` | `(roll_no, skill_id)` | `student.roll_no`, `skill.skill_id` | BCNF | 89 possessed skill records. Defaults: `can_teach = FALSE`, `proficiency = 'BEGINNER'`. |
| `student_desired_skill` | `(roll_no, skill_id)` | `student.roll_no`, `skill.skill_id` | BCNF | 83 learning aspirations for bidirectional mentor-peer discovery. |
| `learning_session` | `session_id` | `student.roll_no` (mentor & learner), `skill.skill_id` | BCNF | Session lifecycle state machine (`REQUESTED` $\to$ `ACCEPTED` $\to$ `COMPLETED`). `credit_cost = 0`. |
| `review` | `(session_id, roll_no)` | `learning_session.session_id`, `student.roll_no` | BCNF | Verified session feedback (1–5 stars). CHECK: `roll_no <> reviewee_roll_no`. |
| `experience` | `(roll_no, exp_no)` | `student.roll_no` | BCNF | Student portfolio items (Internships, Projects). CHECK: `end_date >= start_date`. |
| `listing` | `listing_id` | `student.roll_no` (seller & buyer) | BCNF | Campus marketplace inventory. Concurrency-safe atomic reservation state. |
| `survey_import_audit` | `audit_id` | *None* | BCNF | Immutable audit trail storing all 36 original survey responses verbatim. |

### B. Universal PK & Relational Rules Enforced
- **Roll_No Regex Constraint:**
  `CHECK (roll_no REGEXP '^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$')`
- **Program Alignment Constraint:**
  `CHECK (program = SUBSTRING(roll_no, 5, LENGTH(program)))`
- **Permanently Free Sessions:**
  `CHECK (credit_cost = 0)`
- **Non-Negative Reputation:**
  `CHECK (reputation_points >= 0)`
- **Non-Spendable Reputation Engine:** Completed sessions increment `reputation_points` by exactly 10 points via atomic `SELECT ... FOR UPDATE` locking on `learning_session`. Points cannot be spent or transferred.

---

## 4. Skill & Category Taxonomy

A total of **102 distinct skills** were parsed, cleaned, and cataloged across 10 academic and extracurricular categories:

| Category | Skills Count | Examples |
|---|---|---|
| **Computer Science & Tech** | 32 | Python, Web Development, Java, C++, DSA, Cybersecurity, Cloud, Linux |
| **Media & Creative Arts** | 18 | Video Editing, Graphic Design, Photography, UI/UX Design, Photoshop |
| **Business & Management** | 14 | Digital Marketing, Financial Markets, Stock Trading, Entrepreneurship |
| **Soft Skills & Leadership** | 12 | Public Speaking, Communication, Debate, Critical Thinking |
| **Music & Performance** | 8 | Guitar, Music Production, Singing, Audio Engineering |
| **Hobbies & Crafts** | 6 | Baking, Cooking, Sketching, Chess |
| **Sports & Fitness** | 5 | Badminton, Table Tennis, Cricket, Fitness Training |
| **Engineering & Hardware** | 4 | Arduino, IoT, Electronics, 3D Modeling |
| **Academics & Science** | 2 | Mathematics, Physics |
| **Languages & Writing** | 1 | Technical & Creative Writing |

### Top Possessed vs Desired Skills:
- **Most Common Possessed Skills:** Video Editing (8 students), Graphic Design (7 students), Python Programming (6 students), Web Development (5 students), Public Speaking (4 students).
- **Most Requested Desired Skills:** Machine Learning & AI (9 students), Public Speaking (6 students), Fullstack Web Development (5 students), Stock Trading & Finance (4 students), Advanced DSA (4 students).

---

## 5. Authentic Campus Marketplace Listings

The survey yielded **9 authentic marketplace items** posted by verified JKLU students:

| ID | Seller Roll | Item Title | Category | Price (₹) | Original Text | Status |
|---|---|---|---|---|---|---|
| 1 | `2025BTECH017` | Stainless steel water bottle | Campus Essentials | ₹150.00 | `150` | AVAILABLE |
| 2 | `2025BTECH025` | Pack of playing cards | Hobbies & Games | ₹200.00 | `200` | AVAILABLE |
| 3 | `2025BTECH035` | Reference book / semester notes | Books & Notes | ₹100.00 | `100` | AVAILABLE |
| 4 | `2025BTECH027` | Acrylic colours | Art & Design | ₹120.00 | `120` | AVAILABLE |
| 5 | `2025BTECH105` | Exam Prep Kit – notes, PYQs, solutions | Books & Notes | ₹99.00 | `₹99 per subject` | AVAILABLE |
| 6 | `2025BTECH116` | Programming First Principles Crash Course | Courses & Tutoring | ₹11,999.00 | `11999` | AVAILABLE |
| 7 | `2026BTECH286` | Small canvas paintings | Art & Design | ₹100.00 | `100-150` | AVAILABLE |
| 8 | `2026BBA079` | AI model training guide & prompts | Digital Resources | ₹29.00 | `29₹` | AVAILABLE |
| 9 | `2026BTECH147` | PowerPoint presentation design | Academic Services | ₹100.00 | `₹100 for 10 slides.` | AVAILABLE |

- **Price Statistics:** Minimum: ₹29.00 | Median: ₹100.00 | Average: ₹1,435.33 | Maximum: ₹11,999.00
- **Verbatim Price Preservation:** The `original_price_text` column preserves context like `"₹99 per subject"` and `"₹100 for 10 slides."` directly on the listing cards.

---

## 6. SQL Demonstration Queries Verification (1 to 34)

All 34 queries in `backend/database/test_queries.sql` were executed against the live MySQL `skillswap` database:

```powershell
$env:PYTHONPATH='backend'
backend\.venv\Scripts\python backend/verify_test_queries.py
```

### Execution Outcome:
- **Total Statements Executed:** 43 (including transactions, savepoints, and rollbacks)
- **Errors Encountered:** **0 (100% Pass Rate)**
- **Collation Consistency:** All session variables utilize `_utf8mb4'...' COLLATE utf8mb4_unicode_ci` preventing MySQL Error 1267 collation conflicts.

### Techniques Demonstrated:
- **Queries 1–5:** `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`, `START TRANSACTION` / `ROLLBACK`, multi-table `INNER JOIN`, self-joins, window ranking (`DENSE_RANK()`).
- **Queries 6–10:** Correlated subqueries, `HAVING`, pattern matching (`REGEXP`), set operations (`UNION`), `CASE` conditional transformations.
- **Queries 11–15:** Aggregations (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`), date-time arithmetic, `LEFT JOIN` detecting nulls, `EXISTS`, derived tables in `FROM`.
- **Queries 16–20:** String manipulation (`SUBSTRING`, `LENGTH`, `CONCAT`), `NOT IN` outer joins, `COALESCE`, running totals (`SUM() OVER`), parameterized queries (`@roll`).
- **Queries 21–25:** Multi-table joins across 4+ entities, `GROUP_CONCAT`, `COUNT(DISTINCT)`, nested sub-queries.
- **Queries 26–34:** Full inventory left join, program cohort breakdowns, session distributions, threshold filters, skill exchange matrix, admission year extraction, and bilateral peer analysis.

---

## 7. Automated Test Suite Execution (24 Passed / 0 Failed)

The automated test suite runs against the dedicated test database `skillswap_test`:

```powershell
backend\.venv\Scripts\pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.4.2, pluggy-1.7.0
rootdir: C:\Users\hansi\OneDrive\Documents\Desktop\JKLU SKILLSWAP
collected 24 items

backend\tests\test_auth.py ......                                        [ 25%]
backend\tests\test_health.py ...                                         [ 37%]
backend\tests\test_learning.py .....                                     [ 58%]
backend\tests\test_marketplace.py .....                                  [ 79%]
backend\tests\test_students_skills.py .....                              [100%]

======================== 24 passed, 1 warning in 2.67s ========================
```

### Concurrency Test Outcomes:
1. **Concurrent Marketplace Purchase (`test_concurrent_marketplace_purchases`):**
   - 5 threads concurrently attempt to purchase the exact same available listing.
   - Result: Exactly 1 thread received HTTP 200 (Success); 4 threads received HTTP 409 (Conflict).
   - Zero overselling or race conditions.
2. **Concurrent Session Completion (`test_concurrent_session_completion`):**
   - 4 threads concurrently attempt to complete the exact same session.
   - Result: Exactly 1 thread received HTTP 200 (Success); 3 threads received HTTP 409 (Already Completed).
   - Mentor awarded exactly 10 reputation points; zero double-crediting.

---

## 8. Frontend Cleanup & UI Verification

The frontend was completely refactored to align with university standards:

1. **Purged Fabricated Demo Content:**
   - Removed the "Quick Demo Login" dropdown with simulated personas (Aarav, Bhavya, Sneha).
   - Replaced fake hardcoded homepage statistics with dynamic database analytics.
   - Removed trophy emojis (🥇, 🥈, 🥉) from the Leaderboard. Added a formal university empty state explaining that academic rankings populate dynamically as verified sessions complete.
2. **Student Directory & Mentors Tab:**
   - Upgraded `Mentors.jsx` to a dual-tab **"JKLU Student Directory & Mentors"** interface.
   - Students can browse all 34 real classmates, filter by Program (`BTECH`, `BBA`), and filter by both **Possessed Skills** and **Desired Learning Goals**.
3. **Marketplace Card Display:**
   - Updated cards to display original survey pricing strings alongside standard currency formats.
4. **Corporate Beige Palette Compliance:**
   - Backgrounds: `#F7F3EC`, `#EFE9DF`, `#FCFAF6`
   - Text & Headers: `#2B2926`, `#6F6A63`
   - Borders & Accents: `#D8D1C5`, `#8A6A4A`
5. **Vite Production Build:**
   - `npm run build` succeeds cleanly in 2.84s with 0 syntax or JSX errors.

---

## 9. Security & Data Protection Controls

- **Domain Restriction:** Strict Pydantic validator rejecting all non-`@jklu.edu.in` domains, including lookalikes (`evil-jklu.edu.in`, `jklu.edu.in.evil.com`).
- **Cryptographic Hashing:** Argon2id password hashing with custom salt generation.
- **Universal Roll Format:** Regex validation enforced at both Pydantic schema and MySQL `CHECK` constraint levels.
- **Profile Claiming Flow:** Survey-imported students start with `password_hash = NULL` and `account_status = 'UNVERIFIED'`. Students claim their account via `/register` using their verified official email.

---

## 10. Evaluation Guide for the Professor

### Step 1: Inspect the Database in MySQL Workbench
1. Connect to MySQL Server:
   - **Host:** `127.0.0.1` | **Port:** `3306`
   - **User:** `skillswap` | **Password:** `skillswap_pass`
   - **Database:** `skillswap`
2. Run queries to inspect the authentic survey data:
   ```sql
   -- View all 34 authentic students
   SELECT roll_no, name, email, program, reputation_points, account_status FROM student ORDER BY roll_no;

   -- View student possessed skills
   SELECT ss.roll_no, s.name, ss.proficiency_level, ss.can_teach 
   FROM student_skill ss JOIN skill s ON ss.skill_id = s.skill_id;

   -- View student desired skills (learning goals)
   SELECT sds.roll_no, s.name 
   FROM student_desired_skill sds JOIN skill s ON sds.skill_id = s.skill_id;

   -- View authentic marketplace listings
   SELECT listing_id, seller_roll_no, title, price, original_price_text, category, status FROM listing;

   -- View survey import audit trail (all 36 submissions)
   SELECT audit_id, raw_name, raw_roll_number, normalized_roll_no, import_status FROM survey_import_audit;
   ```

### Step 2: Execute the 34 Demonstration SQL Queries
Open `backend/database/test_queries.sql` in MySQL Workbench and execute the script (or run via terminal):
```powershell
$env:PYTHONPATH='backend'
backend\.venv\Scripts\python backend/verify_test_queries.py
```
*Expected: 43 statements executed, 0 errors.*

### Step 3: Run the Automated Pytest Suite
```powershell
backend\.venv\Scripts\pytest -v
```
*Expected: 24 passed in ~2.7s.*

### Step 4: Run the Application Locally
1. **Start Backend Server:**
   ```powershell
   cd backend
   .\.venv\Scripts\activate
   uvicorn app.main:app --reload --port 8000
   ```
   Interactive Swagger docs available at `http://localhost:8000/docs`.
2. **Start Frontend Client:**
   ```powershell
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173/` in your browser.
3. **Claim an Account:**
   Navigate to `http://localhost:5173/register` and register with a real student roll number (e.g., `2025BTECH027`, `2025BTECH017`, or `2026BBA004`) to claim the profile and view existing survey skills on the dashboard.

