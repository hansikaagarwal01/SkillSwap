-- ============================================================================
-- SkillSwap JKLU - Database Schema Definition (DDL)
-- Engine: MySQL 8.0+ / InnoDB / utf8mb4
-- Tables:
--   1. student (Profile, Academic Dept, Auth Credentials, Verification)
--   2. skill (Catalog of technical & extracurricular skills)
--   3. student_skill (Student proficiencies & mentor availability)
--   4. student_desired_skill (Skills student wishes to learn)
--   5. learning_session (Peer mentorship sessions & reputation audit)
--   6. review (Ratings and feedback)
--   7. experience (Portfolio, internships, hackathons, projects)
--   8. listing (Campus marketplace items)
--   9. survey_import_audit (Complete audit trail of real survey responses)
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS survey_import_audit;
DROP TABLE IF EXISTS student_desired_skill;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS learning_session;
DROP TABLE IF EXISTS listing;
DROP TABLE IF EXISTS experience;
DROP TABLE IF EXISTS student_skill;
DROP TABLE IF EXISTS skill;
DROP TABLE IF EXISTS student;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. STUDENT (Student profile, academic program, authentication, and verification)
CREATE TABLE student (
    roll_no VARCHAR(12) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NULL,
    program ENUM('BTECH', 'BBA', 'BDES') NOT NULL,
    admission_year SMALLINT NOT NULL,
    reputation_points INT NOT NULL DEFAULT 0,
    password_hash VARCHAR(255) NULL,
    account_status ENUM('UNVERIFIED', 'PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED') NOT NULL DEFAULT 'UNVERIFIED',
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at DATETIME NULL,
    token_version INT NOT NULL DEFAULT 1,
    verification_token_hash VARCHAR(64) NULL,
    verification_token_expires_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (roll_no),
    UNIQUE KEY uq_student_email (email),
    UNIQUE KEY uq_student_verification_token (verification_token_hash),
    KEY idx_student_reputation (reputation_points),
    KEY idx_student_program_year (program, admission_year),
    CONSTRAINT chk_student_roll_no_format CHECK (roll_no REGEXP '^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$'),
    CONSTRAINT chk_student_program_matches_roll CHECK (program = SUBSTRING(roll_no, 5, LENGTH(program))),
    CONSTRAINT chk_student_reputation_positive CHECK (reputation_points >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. SKILL
CREATE TABLE skill (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_skill_name (name),
    KEY idx_skill_name (name),
    KEY idx_skill_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. STUDENT_SKILL (Current Skills)
CREATE TABLE student_skill (
    roll_no VARCHAR(12) NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT') NOT NULL DEFAULT 'BEGINNER',
    can_teach BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (roll_no, skill_id),
    KEY idx_student_skill_skill (skill_id),
    KEY idx_student_skill_teach (can_teach, skill_id),
    CONSTRAINT fk_student_skill_student FOREIGN KEY (roll_no) REFERENCES student (roll_no) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_student_skill_skill FOREIGN KEY (skill_id) REFERENCES skill (skill_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. STUDENT_DESIRED_SKILL (Desired Skills)
CREATE TABLE student_desired_skill (
    roll_no VARCHAR(12) NOT NULL,
    skill_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (roll_no, skill_id),
    KEY idx_desired_skill_skill (skill_id),
    CONSTRAINT fk_desired_skill_student FOREIGN KEY (roll_no) REFERENCES student (roll_no) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_desired_skill_skill FOREIGN KEY (skill_id) REFERENCES skill (skill_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. LEARNING_SESSION (Consolidated sessions and reputation awarding audit)
CREATE TABLE learning_session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    mentor_roll_no VARCHAR(12) NOT NULL,
    learner_roll_no VARCHAR(12) NOT NULL,
    skill_id INT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    mode ENUM('ONLINE', 'OFFLINE') NOT NULL DEFAULT 'ONLINE',
    scheduled_at DATETIME NOT NULL,
    meeting_link VARCHAR(255) NULL,
    status ENUM('REQUESTED', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'REQUESTED',
    credit_cost INT NOT NULL DEFAULT 0,
    points_awarded INT NOT NULL DEFAULT 0,
    reputation_awarded BOOLEAN NOT NULL DEFAULT FALSE,
    reputation_awarded_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_session_mentor (mentor_roll_no),
    KEY idx_session_learner (learner_roll_no),
    KEY idx_session_skill (skill_id),
    KEY idx_session_status_scheduled (status, scheduled_at),
    CONSTRAINT fk_session_mentor FOREIGN KEY (mentor_roll_no) REFERENCES student (roll_no) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_session_learner FOREIGN KEY (learner_roll_no) REFERENCES student (roll_no) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_session_skill FOREIGN KEY (skill_id) REFERENCES skill (skill_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_session_distinct_participants CHECK (mentor_roll_no <> learner_roll_no),
    CONSTRAINT chk_session_free_credit_cost CHECK (credit_cost = 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. REVIEW
CREATE TABLE review (
    session_id INT NOT NULL,
    roll_no VARCHAR(12) NOT NULL,
    reviewee_roll_no VARCHAR(12) NOT NULL,
    rating TINYINT NOT NULL,
    comment TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, roll_no),
    KEY idx_review_roll (roll_no),
    KEY idx_review_reviewee (reviewee_roll_no),
    CONSTRAINT fk_review_session FOREIGN KEY (session_id) REFERENCES learning_session (session_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_review_reviewer FOREIGN KEY (roll_no) REFERENCES student (roll_no) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_review_reviewee FOREIGN KEY (reviewee_roll_no) REFERENCES student (roll_no) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_review_rating_range CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT chk_review_distinct_parties CHECK (roll_no <> reviewee_roll_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. EXPERIENCE
CREATE TABLE experience (
    roll_no VARCHAR(12) NOT NULL,
    exp_no INT NOT NULL,
    role_title VARCHAR(150) NOT NULL,
    organization VARCHAR(150) NOT NULL,
    exp_type ENUM('INTERNSHIP', 'PROJECT', 'HACKATHON', 'ACHIEVEMENT', 'OTHER') NOT NULL DEFAULT 'PROJECT',
    start_date DATE NOT NULL,
    end_date DATE NULL,
    description TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (roll_no, exp_no),
    CONSTRAINT fk_experience_student FOREIGN KEY (roll_no) REFERENCES student (roll_no) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_experience_dates CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. LISTING
CREATE TABLE listing (
    listing_id INT AUTO_INCREMENT PRIMARY KEY,
    seller_roll_no VARCHAR(12) NOT NULL,
    buyer_roll_no VARCHAR(12) NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('AVAILABLE', 'IN_PROGRESS', 'SOLD', 'REMOVED', 'PENDING_REVIEW') NOT NULL DEFAULT 'AVAILABLE',
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    original_price_text VARCHAR(150) NULL,
    category VARCHAR(50) NOT NULL,
    item_condition ENUM('NEW', 'LIKE_NEW', 'GOOD', 'FAIR') NOT NULL DEFAULT 'GOOD',
    posted_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sold_at DATETIME NULL,
    KEY idx_listing_seller (seller_roll_no),
    KEY idx_listing_buyer (buyer_roll_no),
    KEY idx_listing_status_category (status, category),
    CONSTRAINT fk_listing_seller FOREIGN KEY (seller_roll_no) REFERENCES student (roll_no) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_listing_buyer FOREIGN KEY (buyer_roll_no) REFERENCES student (roll_no) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT chk_listing_price_positive CHECK (price >= 0),
    CONSTRAINT chk_listing_seller_buyer_distinct CHECK (buyer_roll_no IS NULL OR seller_roll_no <> buyer_roll_no),
    CONSTRAINT chk_listing_sold_consistency CHECK (
        (status = 'SOLD' AND buyer_roll_no IS NOT NULL AND sold_at IS NOT NULL) OR
        (status <> 'SOLD')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. SURVEY_IMPORT_AUDIT (Full provenance and audit log for survey data)
CREATE TABLE survey_import_audit (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    survey_timestamp DATETIME NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    raw_roll_no VARCHAR(50) NOT NULL,
    normalized_roll_no VARCHAR(12) NULL,
    raw_email VARCHAR(100) NOT NULL,
    raw_current_skills TEXT NULL,
    raw_desired_skills TEXT NULL,
    raw_sell_flag VARCHAR(10) NULL,
    raw_item VARCHAR(255) NULL,
    raw_price VARCHAR(100) NULL,
    raw_description TEXT NULL,
    import_status ENUM('IMPORTED', 'MERGED_DUPLICATE', 'REQUIRES_REVIEW', 'REJECTED') NOT NULL,
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_audit_roll (normalized_roll_no),
    KEY idx_audit_status (import_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
