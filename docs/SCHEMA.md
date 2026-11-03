# Database Schema & Normalization Analysis

**Project:** SkillSwap JKLU — University Peer-Mentoring & Marketplace Platform  
**Target RDBMS:** MySQL 8.0+ (InnoDB Engine, utf8mb4)  
**Architecture:** Relational Tables Normalized in 3NF / BCNF with Audit Logging  

---

## 1. Relational Entity Mapping

Redundant 1:1 and lookup tables (`department`, `auth_account`, `email_verification_token`, `reputation_history`) have been eliminated, consolidating attributes into core entities. Two dedicated entities were introduced to fully capture authentic student survey data: `student_desired_skill` (skills students wish to learn) and `survey_import_audit` (immutable audit trail of survey responses).

| Entity | SQL Table Name | Primary Key | Foreign Keys | Key Constraints & Consolidated Features |
|---|---|---|---|---|
| `STUDENT` | `student` | `roll_no` (VARCHAR(12)) | *None* | Universal PK (`20[0-9]{2}(BTECH\|BBA\|BDES)[0-9]{3}`). Holds student profile, academic program, admission year, reputation points, Argon2 password hash (nullable until account claimed), account status (`UNVERIFIED` for survey imports), email verification tokens. Scoped exclusively to enrolled students. |
| `SKILL` | `skill` | `skill_id` (INT AUTO_INCREMENT) | *None* | Categorized catalog of technical & extracurricular skills. `name` is unique and indexed. |
| `STUDENT_SKILL` | `student_skill` | (`roll_no`, `skill_id`) | `roll_no` → `student.roll_no`<br>`skill_id` → `skill.skill_id` | Skills possessed by the student. Proficiency ENUM('BEGINNER','INTERMEDIATE','ADVANCED','EXPERT'), `can_teach` BOOLEAN (defaults to FALSE for survey entries). |
| `STUDENT_DESIRED_SKILL` | `student_desired_skill` | (`roll_no`, `skill_id`) | `roll_no` → `student.roll_no`<br>`skill_id` → `skill.skill_id` | Learning aspirations captured from survey responses ("What skills would you like to learn?"). Enables bidirectional peer matching. |
| `LEARNING_SESSION` | `learning_session` | `session_id` (INT AUTO_INCREMENT) | `mentor_roll_no` → `student.roll_no`<br>`learner_roll_no` → `student.roll_no`<br>`skill_id` → `skill.skill_id` | Status ENUM('REQUESTED','ACCEPTED','REJECTED','CANCELLED','COMPLETED'). CHECK `credit_cost = 0`. CHECK `mentor_roll_no <> learner_roll_no`. Contains atomic reputation audit (`reputation_awarded`, `points_awarded`, `reputation_awarded_at`). |
| `REVIEW` | `review` | (`session_id`, `roll_no`) | `session_id` → `learning_session.session_id`<br>`roll_no` → `student.roll_no`<br>`reviewee_roll_no` → `student.roll_no` | CHECK `rating BETWEEN 1 AND 5`. CHECK `roll_no <> reviewee_roll_no`. |
| `EXPERIENCE` | `experience` | (`roll_no`, `exp_no`) | `roll_no` → `student.roll_no` (ON DELETE CASCADE) | Student portfolio: internships, projects, hackathons, achievements. CHECK `end_date IS NULL OR end_date >= start_date`. |
| `LISTING` | `listing` | `listing_id` (INT AUTO_INCREMENT) | `seller_roll_no` → `student.roll_no`<br>`buyer_roll_no` → `student.roll_no` | Campus marketplace item inventory. Item condition ENUM('NEW','LIKE_NEW','GOOD','FAIR'). CHECK `price >= 0`. CHECK `seller_roll_no <> buyer_roll_no`. Stores parsed numeric `price` alongside verbatim `original_price_text` (e.g., "₹99 per subject"). Atomic reservation consistency check. |
| `SURVEY_IMPORT_AUDIT` | `survey_import_audit` | `audit_id` (INT AUTO_INCREMENT) | *None* | Verbatim record of each survey response submission, raw and normalized fields, timestamp, and review status. |

---

## 2. Normalization Breakdown (1NF → 3NF / BCNF)

### 1. `student`
- **Attributes:** `roll_no` (PK), `name`, `email`, `phone`, `program`, `admission_year`, `reputation_points`, `password_hash`, `account_status`, `email_verified`, `last_login_at`, `token_version`, `verification_token_hash`, `verification_token_expires_at`, `created_at`, `updated_at`.
- **Candidate Keys:** $CK_1 = \{roll\_no\}$, $CK_2 = \{email\}$.
- **Functional Dependencies:**
  - $roll\_no \rightarrow name, email, phone, program, admission\_year, reputation\_points, password\_hash, account\_status, email\_verified, token\_version, verification\_token\_hash, verification\_token\_expires\_at, created\_at, updated\_at$
  - $email \rightarrow roll\_no, ...$
- **1NF:** Every attribute holds atomic (indivisible) scalar values. No repeating groups or nested arrays.
- **2NF:** The primary key is single-attribute (`roll_no`). Therefore, no partial functional dependencies ($X \subset CK \rightarrow Y$) can possibly exist.
- **3NF & BCNF:** 
  - Storing only `program` (`BTECH`, `BBA`, `BDES`) and omitting `department` completely removes the transitive dependency $roll\_no \rightarrow department \rightarrow program$ where `department` would not be a superkey.
  - In every valid non-trivial functional dependency $X \rightarrow Y$, the determinant $X$ is a superkey ($roll\_no$ or $email$).
  - **Verdict:** Strictly in **BCNF** (and automatically satisfies **3NF**).

### 2. `skill`
- **Attributes:** `skill_id` (PK), `name` (UK), `category`, `description`, `created_at`.
- **Candidate Keys:** $CK_1 = \{skill\_id\}$, $CK_2 = \{name\}$.
- **Functional Dependencies:**
  - $skill\_id \rightarrow name, category, description, created\_at$
  - $name \rightarrow skill\_id, category, description, created\_at$
- **1NF, 2NF, 3NF, BCNF:** Both determinants are candidate keys. No partial or transitive dependencies exist. **Table is strictly in BCNF.**

### 3. `student_skill`
- **Primary Key:** (`roll_no`, `skill_id`)
- **Functional Dependencies:**
  - (`roll_no`, `skill_id`) $\rightarrow$ `proficiency_level, can_teach, created_at`
- **1NF:** Atomic scalar values.
- **2NF:** `proficiency_level` and `can_teach` depend on the composite key (`roll_no`, `skill_id`). Neither depends on `roll_no` alone or `skill_id` alone.
- **3NF / BCNF:** No transitive dependencies between non-prime attributes. Determinant is a candidate key. **Table is in BCNF.**

### 4. `student_desired_skill`
- **Primary Key:** (`roll_no`, `skill_id`)
- **Functional Dependencies:**
  - (`roll_no`, `skill_id`) $\rightarrow$ `created_at`
- **1NF, 2NF, 3NF, BCNF:** Pure associative entity linking a student to a desired skill. Key is minimal and irreducible. Determinant is the candidate key. **Table is in BCNF.**

### 5. `learning_session`
- **Primary Key:** `session_id`
- **Functional Dependencies:**
  - `session_id` $\rightarrow$ `mentor_roll_no, learner_roll_no, skill_id, topic, mode, scheduled_at, meeting_link, status, credit_cost, points_awarded, reputation_awarded, reputation_awarded_at, created_at, updated_at`
- **1NF:** Single-valued fields.
- **2NF:** Single primary key; no partial dependencies.
- **3NF / BCNF:** Participant details and skill names are referenced solely by FKs. Non-key attributes depend only on `session_id`. **Table is in BCNF.**

### 6. `review`
- **Primary Key:** (`session_id`, `roll_no`)
- **Functional Dependencies:**
  - (`session_id`, `roll_no`) $\rightarrow$ `reviewee_roll_no, rating, comment, created_at`
- **1NF, 2NF, 3NF, BCNF:** The rating and comment are unique to the review submitted by reviewer `roll_no` for `session_id`. Determinant is the candidate key. **Table is in BCNF.**

### 7. `experience`
- **Primary Key:** (`roll_no`, `exp_no`)
- **Functional Dependencies:**
  - (`roll_no`, `exp_no`) $\rightarrow$ `role_title, organization, exp_type, start_date, end_date, description, created_at`
- **1NF, 2NF, 3NF, BCNF:** Sequence number `exp_no` is scoped per student. All non-key attributes directly depend on the composite primary key. **Table is in BCNF.**

### 8. `listing`
- **Primary Key:** `listing_id`
- **Functional Dependencies:**
  - `listing_id` $\rightarrow$ `seller_roll_no, buyer_roll_no, title, description, status, price, original_price_text, category, item_condition, posted_date, sold_at`
- **1NF, 2NF, 3NF, BCNF:** Single primary key. Sellers and buyers are referenced by `roll_no`. All attributes directly describe the listed item. Determinant is the candidate key. **Table is in BCNF.**

### 9. `survey_import_audit`
- **Primary Key:** `audit_id`
- **Functional Dependencies:**
  - `audit_id` $\rightarrow$ `submission_timestamp, raw_name, raw_roll_number, normalized_roll_no, raw_email, raw_current_skills, raw_desired_skills, raw_marketplace_item, raw_price, raw_item_description, import_status, error_notes, created_at`
- **1NF, 2NF, 3NF, BCNF:** Single primary key audit record with no partial or transitive dependencies. **Table is in BCNF.**
