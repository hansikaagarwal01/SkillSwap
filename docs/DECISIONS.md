# Architectural Decision Records (ADR) - SkillSwap JKLU

## Decision 1: Primary Key for Students (`roll_no`)
- **Context:** Standard student ID vs JKLU academic Roll Number.
- **Decision:** Use `roll_no` (VARCHAR(12)) as the universal primary key for `student`. No generic `student_id` is permitted.
- **Validation:** Regex `^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$`.
- **Derived Fields:** `program` ('BTECH','BBA','BDES') and `admission_year` (SMALLINT) are derived from the roll number. MySQL 8 CHECK constraint: `program = SUBSTRING(roll_no, 5, LENGTH(program))` and `roll_no REGEXP '^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$'`.

## Decision 2: Domain Email Validation and Real Verification
- **Context:** Only authentic JKLU community members should join.
- **Decision:** Emails must end strictly with `@jklu.edu.in`. Lookalike domains (`evil-jklu.edu.in`, `jklu.edu.in.evil.com`) are rejected both on frontend and in backend Pydantic validator using normalized host check.
- **Verification:** Cryptographically secure `secrets.token_urlsafe(32)` generated at registration. Only its SHA-256 hash is persisted in `email_verification_token` with 24-hour expiry and single-use `used_at` flag. In development (`APP_ENV=development`), links are logged to console with `[DEV-ONLY]` banner if SMTP is unset; this fallback is strictly disabled in production.

## Decision 3: Department Table and Foreign Key (`d_id`)
- **Context:** Academic structure requirement.
- **Decision:** `d_id` in `student` references an explicit `department` table with fields `(d_id, name, program)`. Initial departments include Computer Science & Engineering (CSE), AI & Machine Learning (AIML), Electronics & Communication (ECE), Business Administration (BBA), and Design (BDES).

## Decision 4: SQL Naming Conventions and Reserved Keyword Resolution
- **Context:** MySQL reserved keyword collisions.
- **Decision:**
  - `SESSION` -> `learning_session` (avoiding MySQL `SESSION` keyword).
  - `condition` -> `item_condition` ENUM('NEW','LIKE_NEW','GOOD','FAIR') in `listing`.
  - `role` -> `role_title`, `type` -> `exp_type` ENUM('INTERNSHIP','PROJECT','HACKATHON','ACHIEVEMENT','OTHER') in `experience`.

## Decision 5: Non-Spendable Reputation System
- **Context:** Incentivizing peer learning without monetary speculation.
- **Decision:** Sessions are completely free (`credit_cost = 0`). Completing a session awards `REPUTATION_PER_SESSION` (default 10) to the mentor.
- **Anti-Duplication:** Handled in a single ACID transaction locking the session row (`SELECT ... FOR UPDATE`), setting status `COMPLETED`, inserting into `reputation_history(session_id, roll_no, points, reason)` with a `UNIQUE(session_id)` constraint, and incrementing `student.reputation_points`. Retries fail safely on the unique constraint.

## Decision 6: Atomic Marketplace Purchase
- **Context:** Concurrency safety when students claim/reserve marketplace items.
- **Decision:** No payment gateway is integrated. Purchase is a reservation claim executed via an atomic conditional query inside a transaction:
  `UPDATE listing SET status='SOLD', buyer_roll_no=:buyer, sold_at=NOW() WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer`.
  If rowcount is 0, transaction aborts with 409 Conflict. This guarantees exactly one buyer succeeds under concurrent requests.

## Decision 7: Multi-Environment Database Support
- **Context:** Development environment options on local host vs Docker.
- **Decision:**
  - Provide `docker-compose.yml` configured for port 3306 (primary `skillswap` + `skillswap_test`).
  - Support running against local native MySQL 8.0 Server (running on port 3307 or 3306) via `.env` configuration.

## Decision 8: Schema Consolidation (Elimination of Redundant Tables)
- **Context:** Initial design used 11 tables including several 1:1 entities (`auth_account`), transient token single-use tables (`email_verification_token`), lookup tables (`department`), and duplicate logging tables (`reputation_history`).
- **Decision:**
  - Consolidate `auth_account` directly into `student` (merging `password_hash`, `account_status`, `email_verified`, `token_version`).
  - Consolidate `email_verification_token` directly into `student` (`verification_token_hash`, `verification_token_expires_at`).
  - Consolidate `reputation_history` into `learning_session` (`points_awarded`, `reputation_awarded`, `reputation_awarded_at`).
  - Results in a streamlined, highly cohesive schema with zero unnecessary JOIN overhead.

## Decision 9: Strict BCNF Normalization on Student Entity
- **Context:** In normalization analysis, having both `department` and `program` on `student` created a transitive functional dependency ($roll\_no \rightarrow department \rightarrow program$) where `department` is not a superkey.
- **Decision:**
  - Retain `program ENUM('BTECH', 'BBA', 'BDES')` on `student`, which matches the student's immutable roll number (`chk_student_program_matches_roll`).
  - Remove `department` from the database table. Provide a backward-compatible `@property` helper on the `Student` model that dynamically derives academic affiliation from `program`.
  - With every determinant in `student` being a candidate key (`roll_no` or `email`), the entity strictly satisfies Boyce-Codd Normal Form (BCNF) and Third Normal Form (3NF).

## Decision 10: Authentic Survey Data Integration & Desired Skills Association
- **Context:** The platform must reflect the actual 36 JKLU student survey responses without fabricated demo students or skills. The survey collected both possessed skills ("What skills do you currently possess?") and desired skills ("What skills would you like to learn?").
- **Decision:**
  - Introduce `student_desired_skill` (composite PK `roll_no`, `skill_id`) to capture learning goals separately from possessed abilities.
  - Set `can_teach = FALSE` and `proficiency = 'BEGINNER'` for survey-imported skills until students explicitly enable mentoring.
  - Survey imported students start with `account_status = 'UNVERIFIED'` and `password_hash = NULL`, allowing authentic students to claim their profiles upon registration with their verified `@jklu.edu.in` email.

## Decision 11: Survey Submission Audit Trail (`survey_import_audit`)
- **Context:** Academic evaluation requires full reproducibility and accountability for how survey rows were mapped into normalized relational entities.
- **Decision:**
  - Retain all 36 survey responses verbatim in `survey_import_audit`, recording raw inputs, normalized roll numbers, duplicate merging decisions, and flagged listings.
  - Two manual roll-number corrections were applied based on verified survey entries: `004` $\to$ `2026BBA004` and `147btech2026` $\to$ `2026BTECH147`.
  - Duplicate entries were merged by timestamp recency (`2025BTECH023` Dhruv Tyagi, `2025BTECH022` Dhanyashree Sen).

## Decision 12: Test Database Isolation (`skillswap_test`) vs Survey Database (`skillswap`)
- **Context:** Running automated test suites must never mutate, delete, or inject mock data into the production survey database.
- **Decision:**
  - Configure `skillswap` strictly for live student survey data (34 students, 102 skills, 9 listings, 0 mock reviews/sessions).
  - Configure `skillswap_test` as an ephemeral test fixture database for pytest execution, populated by `conftest.py` with multi-user concurrency cohorts.
