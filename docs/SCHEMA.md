# Database Schema & Normalization Analysis

**Project:** SkillSwap JKLU — University Peer-Mentoring & Marketplace Platform  
**Target RDBMS:** MySQL 8.0+ (InnoDB Engine, utf8mb4)  
**Academic Source of Truth:** Normalized Relational Database Model  

---

## 1. ER Name to SQL Name Mapping

| ER Entity / Relation | SQL Table Name | Primary Key | Foreign Keys | Key Constraints & Notes |
|---|---|---|---|---|
| `DEPARTMENT` | `department` | `d_id` (INT AUTO_INCREMENT) | None | `name` UNIQUE |
| `STUDENT` | `student` | `roll_no` (VARCHAR(12)) | `d_id` → `department.d_id` | Universal PK. Regex `^(20[0-9]{2})(BTECH\|BBA\|BDES)[0-9]{3}$`. CHECK `program = SUBSTRING(roll_no, 5, LENGTH(program))`. CHECK `reputation_points >= 0`. |
| `AUTH_ACCOUNT` | `auth_account` | `roll_no` (VARCHAR(12)) | `roll_no` → `student.roll_no` (ON DELETE CASCADE) | Role ENUM('STUDENT','ADMIN'), Status ENUM('UNVERIFIED','PENDING_APPROVAL','ACTIVE','SUSPENDED'). |
| `EMAIL_VERIFICATION_TOKEN` | `email_verification_token` | `token_id` (INT AUTO_INCREMENT) | `roll_no` → `student.roll_no` (ON DELETE CASCADE) | `token_hash` UNIQUE (SHA-256), single-use `used_at`, 24h expiry. |
| `SKILL` | `skill` | `skill_id` (INT AUTO_INCREMENT) | None | `name` UNIQUE. Categorized. |
| `STUDENT_SKILL` | `student_skill` | (`roll_no`, `skill_id`) | `roll_no` → `student.roll_no`, `skill_id` → `skill.skill_id` | Proficiency ENUM('BEGINNER','INTERMEDIATE','ADVANCED','EXPERT'), `can_teach` BOOLEAN. |
| `SESSION` | `learning_session` | `session_id` (INT AUTO_INCREMENT) | `mentor_roll_no` → `student.roll_no`, `learner_roll_no` → `student.roll_no`, `skill_id` → `skill.skill_id` | Renamed from reserved keyword `SESSION`. Status ENUM('REQUESTED','ACCEPTED','REJECTED','CANCELLED','COMPLETED'). CHECK `credit_cost = 0`. CHECK `mentor_roll_no <> learner_roll_no`. |
| `REPUTATION_HISTORY` | `reputation_history` | `history_id` (INT AUTO_INCREMENT) | `roll_no` → `student.roll_no`, `session_id` → `learning_session.session_id` | `session_id` UNIQUE prevents duplicate rewards per session. Points default 10. |
| `REVIEW` | `review` | (`session_id`, `roll_no`) | `session_id` → `learning_session.session_id`, `roll_no` → `student.roll_no`, `reviewee_roll_no` → `student.roll_no` | CHECK `rating BETWEEN 1 AND 5`. CHECK `roll_no <> reviewee_roll_no`. |
| `EXPERIENCE` | `experience` | (`roll_no`, `exp_no`) | `roll_no` → `student.roll_no` (ON DELETE CASCADE) | Renamed `role` → `role_title`, `type` → `exp_type` ENUM('INTERNSHIP','PROJECT','HACKATHON','ACHIEVEMENT','OTHER'). CHECK `end_date IS NULL OR end_date >= start_date`. |
| `LISTING` | `listing` | `listing_id` (INT AUTO_INCREMENT) | `seller_roll_no` → `student.roll_no`, `buyer_roll_no` → `student.roll_no` | Renamed `condition` → `item_condition` ENUM('NEW','LIKE_NEW','GOOD','FAIR'). CHECK `price >= 0`. CHECK `seller_roll_no <> buyer_roll_no`. CHECK `(status = 'SOLD' AND buyer_roll_no IS NOT NULL AND sold_at IS NOT NULL) OR (status <> 'SOLD')`. |

---

## 2. Normalization Breakdown (1NF → 3NF / BCNF)

### 1. `department`
- **1NF:** All column values are atomic (scalar INT, VARCHAR, ENUM, TIMESTAMP). No repeating groups.
- **2NF:** In 1NF and the primary key is single-attribute (`d_id`). Therefore, no partial functional dependencies exist.
- **3NF:** Non-key attribute `name` depends directly on `d_id`. `program` depends directly on `d_id`. No transitive dependencies exist.
- **BCNF:** For all functional dependencies $X \rightarrow Y$ (`d_id` $\rightarrow$ `name, program` and `name` $\rightarrow$ `d_id, program`), the determinant $X$ is a superkey. **Table is in BCNF.**

### 2. `student`
- **Functional Dependencies:**
  - `roll_no` $\rightarrow$ `name, email, phone, d_id, program, admission_year, reputation_points, created_at`
  - `email` $\rightarrow$ `roll_no, ...` (Candidate key)
- **1NF:** Attributes are atomic. Single phone string (or NULL), single email, scalar reputation integer.
- **2NF:** The primary key is single-attribute (`roll_no`). No partial dependency can exist.
- **3NF / BCNF:** Department details (e.g. department name, building) are intentionally not stored in `student`; only the foreign key `d_id` is maintained, preventing transitive dependency $\text{student} \rightarrow \text{department\_name}$. `program` and `admission_year` are functionally determined by `roll_no` and verified by DB CHECK. Every determinant is a candidate key. **Table is in BCNF.**

### 3. `auth_account`
- **Functional Dependencies:**
  - `roll_no` $\rightarrow$ `password_hash, role, account_status, email_verified, last_login_at, token_version, created_at, updated_at`
- **1NF:** Atomic attributes.
- **2NF:** Single-attribute primary key (`roll_no`). No partial dependencies.
- **3NF / BCNF:** Every non-key attribute directly depends on `roll_no`. No transitive dependencies. **Table is in BCNF.**

### 4. `email_verification_token`
- **Functional Dependencies:**
  - `token_id` $\rightarrow$ `roll_no, token_hash, expires_at, used_at, created_at`
  - `token_hash` $\rightarrow$ `token_id, roll_no, expires_at, used_at, created_at` (Candidate key)
- **1NF:** Atomic strings, timestamps.
- **2NF:** Single primary key.
- **3NF / BCNF:** All determinants are candidate keys. **Table is in BCNF.**

### 5. `skill`
- **Functional Dependencies:**
  - `skill_id` $\rightarrow$ `name, category, description, created_at`
  - `name` $\rightarrow$ `skill_id, category, description, created_at` (Candidate key)
- **1NF:** Single scalar fields.
- **2NF & 3NF:** Single-attribute key; no transitive dependency. Determinants are superkeys. **Table is in BCNF.**

### 6. `student_skill`
- **Primary Key:** (`roll_no`, `skill_id`)
- **Functional Dependencies:**
  - (`roll_no`, `skill_id`) $\rightarrow$ `proficiency_level, can_teach, created_at`
- **1NF:** Atomic values.
- **2NF:** Neither `proficiency_level` nor `can_teach` depends solely on `roll_no` or solely on `skill_id`. Both attributes characterize the specific relationship between a student and a skill. No partial dependency exists.
- **3NF / BCNF:** No transitive dependencies between non-prime attributes. Determinant (`roll_no`, `skill_id`) is a superkey. **Table is in BCNF.**

### 7. `learning_session`
- **Primary Key:** `session_id`
- **Functional Dependencies:**
  - `session_id` $\rightarrow$ `mentor_roll_no, learner_roll_no, skill_id, topic, mode, scheduled_at, meeting_link, status, credit_cost, created_at, updated_at`
- **1NF:** Single-valued fields.
- **2NF:** Single primary key; no partial dependencies.
- **3NF / BCNF:** All foreign keys (`mentor_roll_no`, `learner_roll_no`, `skill_id`) are kept normalized without repeating student names, ratings, or skill descriptions. Non-key attributes depend only on `session_id`. **Table is in BCNF.**

### 8. `reputation_history`
- **Primary Key:** `history_id`
- **Candidate Key:** `session_id` (UNIQUE constraint enforces one award per session)
- **Functional Dependencies:**
  - `history_id` $\rightarrow$ `roll_no, session_id, points, reason, created_at`
  - `session_id` $\rightarrow$ `history_id, roll_no, points, reason, created_at`
- **1NF, 2NF, 3NF, BCNF:** Both determinants are candidate keys. **Table is in BCNF.**

### 9. `review`
- **Primary Key:** (`session_id`, `roll_no`)
- **Functional Dependencies:**
  - (`session_id`, `roll_no`) $\rightarrow$ `reviewee_roll_no, rating, comment, created_at`
- **1NF:** Atomic rating integer (1–5), comment text, and timestamp.
- **2NF:** The rating and comment are specific to the unique review submitted by `roll_no` for `session_id`. No partial dependency exists.
- **3NF / BCNF:** No non-prime attribute determines another non-prime attribute. **Table is in BCNF.**

### 10. `experience`
- **Primary Key:** (`roll_no`, `exp_no`)
- **Functional Dependencies:**
  - (`roll_no`, `exp_no`) $\rightarrow$ `role_title, organization, exp_type, start_date, end_date, description, created_at`
- **1NF:** Atomic attributes.
- **2NF:** Role title, organization, and dates are unique to that particular experience sequence number for that student; neither depends on `roll_no` alone.
- **3NF / BCNF:** No transitive dependencies. **Table is in BCNF.**

### 11. `listing`
- **Primary Key:** `listing_id`
- **Functional Dependencies:**
  - `listing_id` $\rightarrow$ `seller_roll_no, buyer_roll_no, title, description, status, price, category, item_condition, posted_date, sold_at`
- **1NF, 2NF, 3NF, BCNF:** Single primary key. Student profiles are referenced purely by FK `roll_no`. All non-prime attributes directly depend on `listing_id`. **Table is in BCNF.**
