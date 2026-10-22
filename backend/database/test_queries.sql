-- ============================================================================
-- SkillSwap JKLU - SQL Demonstration Queries (1 through 34)
-- Engine: MySQL 8.0+
-- Prerequisites: schema.sql + seed.sql loaded
-- Usage: mysql -u skillswap -pskillswap_pass -h 127.0.0.1 -P 3307 skillswap < test_queries.sql
-- ============================================================================

USE skillswap;

-- ----------------------------------------------------------------------------
-- QUERY 1: SELECT / DISTINCT / WHERE / ORDER BY / LIMIT
-- Purpose: Retrieve distinct programs and admission years of top reputation students.
-- Output Columns: program, admission_year, roll_no, name, reputation_points
-- Expected Result: Top 5 non-zero reputation students ordered by year DESC and points DESC.
-- ----------------------------------------------------------------------------
SELECT DISTINCT s.program, s.admission_year, s.roll_no, s.name, s.reputation_points
FROM student s
WHERE s.reputation_points > 0
ORDER BY s.admission_year DESC, s.reputation_points DESC
LIMIT 5;

-- ----------------------------------------------------------------------------
-- QUERY 2: INSERT / UPDATE / DELETE in Transaction with ROLLBACK
-- Purpose: Verify ACID transactions: insert test skill, update it, verify, delete, and rollback.
-- Output Columns: status_message, affected_skill_id
-- Expected Result: Demonstrates clean DML execution rolled back with zero residual rows.
-- ----------------------------------------------------------------------------
START TRANSACTION;

INSERT INTO skill (name, category, description) 
VALUES ('Cybersecurity Basics Demo', 'Computer Science', 'Network defence and ethical hacking.');

SET @new_skill_id = LAST_INSERT_ID();

UPDATE skill 
SET description = 'Updated: Network defence, cryptography, and ethical hacking.' 
WHERE skill_id = @new_skill_id;

SELECT 'DML TRANSACTION VERIFIED - READY TO ROLLBACK' AS status_message, skill_id, name, description 
FROM skill 
WHERE skill_id = @new_skill_id;

DELETE FROM skill WHERE skill_id = @new_skill_id;

ROLLBACK;

-- ----------------------------------------------------------------------------
-- QUERY 3: INNER JOIN
-- Purpose: List students along with their verified academic department names.
-- Output Columns: roll_no, student_name, email, department_name, program
-- Expected Result: Active student records joined with matching department records.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name AS student_name, s.email, d.name AS department_name, s.program
FROM student s
INNER JOIN department d ON s.d_id = d.d_id
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 4: LEFT JOIN
-- Purpose: List all skills and any sessions scheduled for them (including unused skills).
-- Output Columns: skill_id, skill_name, category, session_id, topic, status
-- Expected Result: All skills shown; unused skills show NULL for session fields.
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category, ls.session_id, ls.topic, ls.status
FROM skill sk
LEFT JOIN learning_session ls ON sk.skill_id = ls.skill_id
ORDER BY sk.skill_id ASC, ls.session_id ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 5: Self-Join
-- Purpose: Find pairs of distinct students sharing the same department and program.
-- Output Columns: student_1_roll, student_1_name, student_2_roll, student_2_name, shared_department, shared_program
-- Expected Result: Ordered pairs (s1.roll_no < s2.roll_no) sharing dept & program.
-- ----------------------------------------------------------------------------
SELECT s1.roll_no AS student_1_roll, s1.name AS student_1_name,
       s2.roll_no AS student_2_roll, s2.name AS student_2_name,
       d.name AS shared_department, s1.program AS shared_program
FROM student s1
INNER JOIN student s2 ON s1.d_id = s2.d_id AND s1.program = s2.program AND s1.roll_no < s2.roll_no
INNER JOIN department d ON s1.d_id = d.d_id
ORDER BY shared_department, student_1_roll, student_2_roll
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 6: Multi-table Join
-- Purpose: Join learning sessions with mentor student, learner student, skill, and department.
-- Output Columns: session_id, topic, skill_name, mentor_name, mentor_dept, learner_name, mode, scheduled_at, status
-- Expected Result: Detailed session log linking 5 relational tables.
-- ----------------------------------------------------------------------------
SELECT ls.session_id, ls.topic, sk.name AS skill_name,
       m.name AS mentor_name, md.name AS mentor_dept,
       l.name AS learner_name,
       ls.mode, ls.scheduled_at, ls.status
FROM learning_session ls
INNER JOIN student m ON ls.mentor_roll_no = m.roll_no
INNER JOIN department md ON m.d_id = md.d_id
INNER JOIN student l ON ls.learner_roll_no = l.roll_no
INNER JOIN skill sk ON ls.skill_id = sk.skill_id
ORDER BY ls.session_id ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 7: COUNT / SUM / AVG / MIN / MAX Aggregate Functions
-- Purpose: Compute platform-wide summary statistics for student reputation.
-- Output Columns: total_students, total_reputation, avg_reputation, min_reputation, max_reputation
-- Expected Result: Summary metrics across all 34 enrolled students.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(s.roll_no) AS total_students,
    SUM(s.reputation_points) AS total_reputation,
    ROUND(AVG(s.reputation_points), 2) AS avg_reputation,
    MIN(s.reputation_points) AS min_reputation,
    MAX(s.reputation_points) AS max_reputation
FROM student s;

-- ----------------------------------------------------------------------------
-- QUERY 8: GROUP BY + HAVING
-- Purpose: Find departments with at least 5 enrolled students and their average reputation.
-- Output Columns: d_id, department_name, program, student_count, avg_reputation
-- Expected Result: Large departments (CSE, AIML, Management, Design) meeting HAVING count >= 5.
-- ----------------------------------------------------------------------------
SELECT d.d_id, d.name AS department_name, d.program,
       COUNT(s.roll_no) AS student_count,
       ROUND(AVG(s.reputation_points), 1) AS avg_reputation
FROM department d
INNER JOIN student s ON d.d_id = s.d_id
GROUP BY d.d_id, d.name, d.program
HAVING COUNT(s.roll_no) >= 5
ORDER BY student_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 9: Nested Subquery
-- Purpose: Find students whose reputation exceeds the university-wide average.
-- Output Columns: roll_no, name, program, reputation_points
-- Expected Result: Students with reputation > overall average (~8.8 points).
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.reputation_points
FROM student s
WHERE s.reputation_points > (
    SELECT AVG(reputation_points) FROM student
)
ORDER BY s.reputation_points DESC;

-- ----------------------------------------------------------------------------
-- QUERY 10: Correlated Subquery
-- Purpose: Find students with reputation higher than their OWN program's average.
-- Output Columns: roll_no, name, program, reputation_points, program_avg_reputation
-- Expected Result: Top performing students within each of BTECH, BBA, and BDES programs.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.reputation_points,
       ROUND((SELECT AVG(s2.reputation_points) FROM student s2 WHERE s2.program = s.program), 2) AS program_avg_reputation
FROM student s
WHERE s.reputation_points > (
    SELECT AVG(s2.reputation_points)
    FROM student s2
    WHERE s2.program = s.program
)
ORDER BY s.program, s.reputation_points DESC;

-- ----------------------------------------------------------------------------
-- QUERY 11: EXISTS / NOT EXISTS
-- Purpose: Filter students who have listed marketplace items vs those who have not.
-- Output Columns: roll_no, name, program, has_marketplace_listings
-- Expected Result: Demonstrates EXISTS and NOT EXISTS subquery predicates.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, 'YES' AS has_marketplace_listings
FROM student s
WHERE EXISTS (
    SELECT 1 FROM listing l WHERE l.seller_roll_no = s.roll_no
)
UNION ALL
SELECT s.roll_no, s.name, s.program, 'NO' AS has_marketplace_listings
FROM student s
WHERE NOT EXISTS (
    SELECT 1 FROM listing l WHERE l.seller_roll_no = s.roll_no
)
ORDER BY has_marketplace_listings DESC, roll_no ASC
LIMIT 12;

-- ----------------------------------------------------------------------------
-- QUERY 12: IN and NOT EXISTS as a NULL-safe NOT IN alternative
-- Purpose: Find students who have never purchased an item using NULL-safe NOT EXISTS.
-- Output Columns: roll_no, name, program
-- Expected Result: Students without any recorded purchases (safe against NULL buyer_roll_no).
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program
FROM student s
WHERE NOT EXISTS (
    SELECT 1 FROM listing l WHERE l.buyer_roll_no = s.roll_no
)
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 13: CASE Statement
-- Purpose: Classify students into mentorship tiers based on non-spendable reputation.
-- Output Columns: roll_no, name, program, reputation_points, mentorship_tier
-- Expected Result: Students categorized into 'Master Mentor', 'Senior Mentor', 'Peer Mentor', 'Learner'.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.reputation_points,
       CASE 
           WHEN s.reputation_points >= 40 THEN 'Master Mentor'
           WHEN s.reputation_points >= 20 THEN 'Senior Mentor'
           WHEN s.reputation_points >= 10 THEN 'Peer Mentor'
           ELSE 'Learner'
       END AS mentorship_tier
FROM student s
ORDER BY s.reputation_points DESC, s.roll_no ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 14: Date Filtering
-- Purpose: Retrieve sessions scheduled during the month of September 2026.
-- Output Columns: session_id, topic, scheduled_at, mode, status, mentor_name, learner_name
-- Expected Result: Sessions falling strictly between 2026-09-01 and 2026-10-01.
-- ----------------------------------------------------------------------------
SELECT ls.session_id, ls.topic, ls.scheduled_at, ls.mode, ls.status,
       m.name AS mentor_name, l.name AS learner_name
FROM learning_session ls
INNER JOIN student m ON ls.mentor_roll_no = m.roll_no
INNER JOIN student l ON ls.learner_roll_no = l.roll_no
WHERE ls.scheduled_at >= '2026-09-01 00:00:00' 
  AND ls.scheduled_at < '2026-10-01 00:00:00'
ORDER BY ls.scheduled_at ASC;

-- ----------------------------------------------------------------------------
-- QUERY 15: Mentor Discovery by Skill + Proficiency
-- Purpose: Discover mentors who can teach 'Python Programming' at ADVANCED or EXPERT level.
-- Output Columns: roll_no, name, program, email, proficiency_level, reputation_points
-- Expected Result: Verified Python mentors ordered by reputation points descending.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.email, ss.proficiency_level, s.reputation_points
FROM student s
INNER JOIN student_skill ss ON s.roll_no = ss.roll_no
INNER JOIN skill sk ON ss.skill_id = sk.skill_id
WHERE sk.name = 'Python Programming'
  AND ss.can_teach = TRUE
  AND ss.proficiency_level IN ('ADVANCED', 'EXPERT')
ORDER BY s.reputation_points DESC, ss.proficiency_level DESC;

-- ----------------------------------------------------------------------------
-- QUERY 16: Never-mentored Students
-- Purpose: Find students who have never conducted a completed mentoring session as mentor.
-- Output Columns: roll_no, name, program, admission_year
-- Expected Result: Junior and freshman students who have 0 completed mentoring sessions.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.admission_year
FROM student s
WHERE NOT EXISTS (
    SELECT 1 FROM learning_session ls 
    WHERE ls.mentor_roll_no = s.roll_no AND ls.status = 'COMPLETED'
)
ORDER BY s.admission_year DESC, s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 17: Students with No Experience
-- Purpose: Find students who have no logged internship, project, or hackathon experience.
-- Output Columns: roll_no, name, program, admission_year
-- Expected Result: Students with zero records in experience table.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.admission_year
FROM student s
LEFT JOIN experience e ON s.roll_no = e.roll_no
WHERE e.roll_no IS NULL
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 18: Avg Rating per Mentor
-- Purpose: Calculate average review rating and total review count received per mentor.
-- Output Columns: mentor_roll_no, mentor_name, program, avg_rating, total_reviews_received
-- Expected Result: Mentors with their aggregated ratings on completed sessions.
-- ----------------------------------------------------------------------------
SELECT m.roll_no AS mentor_roll_no, m.name AS mentor_name, m.program,
       ROUND(AVG(r.rating), 2) AS avg_rating,
       COUNT(r.rating) AS total_reviews_received
FROM review r
INNER JOIN student m ON r.reviewee_roll_no = m.roll_no
INNER JOIN learning_session ls ON r.session_id = ls.session_id AND ls.mentor_roll_no = m.roll_no
GROUP BY m.roll_no, m.name, m.program
ORDER BY avg_rating DESC, total_reviews_received DESC;

-- ----------------------------------------------------------------------------
-- QUERY 19: Completed Sessions per Skill
-- Purpose: Count total completed learning sessions categorized by skill.
-- Output Columns: skill_id, skill_name, category, completed_session_count
-- Expected Result: Skills ranked by completed session volume (Python, React, etc. at top).
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category,
       COUNT(ls.session_id) AS completed_session_count
FROM skill sk
INNER JOIN learning_session ls ON sk.skill_id = ls.skill_id
WHERE ls.status = 'COMPLETED'
GROUP BY sk.skill_id, sk.name, sk.category
ORDER BY completed_session_count DESC, sk.name ASC;

-- ----------------------------------------------------------------------------
-- QUERY 20: Upcoming Sessions for a Student (Parameterized with @roll)
-- Purpose: Retrieve future scheduled sessions for a student (@roll) as mentor or learner.
-- Output Columns: session_id, topic, skill_name, mode, scheduled_at, meeting_link, student_role, counterpart_name
-- Expected Result: Future ACCEPTED sessions for 2024BTECH001 showing counterpart.
-- ----------------------------------------------------------------------------
SET @roll = '2024BTECH001';

SELECT ls.session_id, ls.topic, sk.name AS skill_name, ls.mode,
       ls.scheduled_at, ls.meeting_link, ls.status,
       CASE 
           WHEN ls.mentor_roll_no = @roll THEN 'MENTOR'
           ELSE 'LEARNER'
       END AS student_role,
       CASE 
           WHEN ls.mentor_roll_no = @roll THEN l.name
           ELSE m.name
       END AS counterpart_name
FROM learning_session ls
INNER JOIN skill sk ON ls.skill_id = sk.skill_id
INNER JOIN student m ON ls.mentor_roll_no = m.roll_no
INNER JOIN student l ON ls.learner_roll_no = l.roll_no
WHERE (ls.mentor_roll_no = @roll OR ls.learner_roll_no = @roll)
  AND ls.status IN ('REQUESTED', 'ACCEPTED')
  AND ls.scheduled_at >= NOW()
ORDER BY ls.scheduled_at ASC;

-- ----------------------------------------------------------------------------
-- QUERY 21: Top 10 by Reputation
-- Purpose: University-wide peer-mentorship leaderboard showing top 10 students.
-- Output Columns: rank, roll_no, name, program, department_name, reputation_points
-- Expected Result: Top 10 ranked students (Bhavya Patel 50, Aarav Sharma 40, etc.).
-- ----------------------------------------------------------------------------
SELECT DENSE_RANK() OVER (ORDER BY s.reputation_points DESC) AS `rank`,
       s.roll_no, s.name, s.program, d.name AS department_name, s.reputation_points
FROM student s
INNER JOIN department d ON s.d_id = d.d_id
ORDER BY s.reputation_points DESC, s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 22: Available vs Sold Listings
-- Purpose: Aggregate marketplace listings by status showing counts, total volume, and average price.
-- Output Columns: status, total_listings, total_value, avg_price
-- Expected Result: Volume and price breakdown across AVAILABLE, SOLD, and REMOVED items.
-- ----------------------------------------------------------------------------
SELECT l.status,
       COUNT(l.listing_id) AS total_listings,
       ROUND(SUM(l.price), 2) AS total_value,
       ROUND(AVG(l.price), 2) AS avg_price
FROM listing l
GROUP BY l.status
ORDER BY total_listings DESC;

-- ----------------------------------------------------------------------------
-- QUERY 23: Most Completed Mentoring Sessions
-- Purpose: Mentors with the highest count of successfully conducted sessions.
-- Output Columns: roll_no, name, program, completed_mentoring_sessions, reputation_points
-- Expected Result: Bhavya Patel (5), Aarav Sharma (4), Sneha Agarwal (3), Chirag Singhal (3).
-- ----------------------------------------------------------------------------
SELECT m.roll_no, m.name, m.program,
       COUNT(ls.session_id) AS completed_mentoring_sessions,
       m.reputation_points
FROM student m
INNER JOIN learning_session ls ON m.roll_no = ls.mentor_roll_no
WHERE ls.status = 'COMPLETED'
GROUP BY m.roll_no, m.name, m.program, m.reputation_points
ORDER BY completed_mentoring_sessions DESC, m.reputation_points DESC
LIMIT 5;

-- ----------------------------------------------------------------------------
-- QUERY 24: Skills Never Used in Sessions
-- Purpose: Identify skills that have zero requested or completed sessions.
-- Output Columns: skill_id, skill_name, category
-- Expected Result: Skills 17 (Rust) and 18 (Quantitative Aptitude).
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category
FROM skill sk
LEFT JOIN learning_session ls ON sk.skill_id = ls.skill_id
WHERE ls.session_id IS NULL
ORDER BY sk.skill_id ASC;

-- ----------------------------------------------------------------------------
-- QUERY 25: Students with No Reviews
-- Purpose: Find students who have neither given nor received any review.
-- Output Columns: roll_no, name, program
-- Expected Result: Active students who have not yet participated in reviews.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program
FROM student s
WHERE NOT EXISTS (
    SELECT 1 FROM review r WHERE r.roll_no = s.roll_no OR r.reviewee_roll_no = s.roll_no
)
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 26: Listings by Seller + Purchase History
-- Purpose: Comprehensive audit of marketplace listings with seller, buyer, price, and status.
-- Output Columns: listing_id, title, category, price, item_condition, status, seller_name, buyer_name, posted_date, sold_at
-- Expected Result: Full inventory with buyers populated for SOLD items and NULL for others.
-- ----------------------------------------------------------------------------
SELECT l.listing_id, l.title, l.category, l.price, l.item_condition, l.status,
       seller.name AS seller_name, seller.roll_no AS seller_roll,
       buyer.name AS buyer_name, buyer.roll_no AS buyer_roll,
       l.posted_date, l.sold_at
FROM listing l
INNER JOIN student seller ON l.seller_roll_no = seller.roll_no
LEFT JOIN student buyer ON l.buyer_roll_no = buyer.roll_no
ORDER BY l.status ASC, l.posted_date DESC;

-- ----------------------------------------------------------------------------
-- QUERY 27: Program-wise Counts (BTECH / BBA / BDES)
-- Purpose: Summary breakdown of enrolled students and total reputation by academic program.
-- Output Columns: program, student_count, total_reputation, avg_reputation
-- Expected Result: 18 BTECH, 8 BBA, 8 BDES with accurate totals.
-- ----------------------------------------------------------------------------
SELECT s.program,
       COUNT(s.roll_no) AS student_count,
       SUM(s.reputation_points) AS total_reputation,
       ROUND(AVG(s.reputation_points), 2) AS avg_reputation
FROM student s
GROUP BY s.program
ORDER BY student_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 28: Sessions by Status
-- Purpose: Percentage distribution of sessions across all 5 possible lifecycle statuses.
-- Output Columns: status, session_count, percentage_share
-- Expected Result: Breakdown across COMPLETED, ACCEPTED, REQUESTED, REJECTED, CANCELLED.
-- ----------------------------------------------------------------------------
SELECT ls.status,
       COUNT(ls.session_id) AS session_count,
       ROUND(COUNT(ls.session_id) * 100.0 / (SELECT COUNT(*) FROM learning_session), 1) AS percentage_share
FROM learning_session ls
GROUP BY ls.status
ORDER BY session_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 29: Mentors with Avg Rating >= Threshold (@min_rating)
-- Purpose: Parameterized query to filter high-rated mentors using threshold variable.
-- Output Columns: roll_no, name, program, avg_rating, review_count
-- Expected Result: Mentors with average rating >= 4.5.
-- ----------------------------------------------------------------------------
SET @min_rating = 4.5;

SELECT m.roll_no, m.name, m.program,
       ROUND(AVG(r.rating), 2) AS avg_rating,
       COUNT(r.rating) AS review_count
FROM review r
INNER JOIN student m ON r.reviewee_roll_no = m.roll_no
INNER JOIN learning_session ls ON r.session_id = ls.session_id AND ls.mentor_roll_no = m.roll_no
GROUP BY m.roll_no, m.name, m.program
HAVING AVG(r.rating) >= @min_rating
ORDER BY avg_rating DESC, review_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 30: Students Sharing Skills
-- Purpose: Find pairs of students who both possess the same skill at ADVANCED or EXPERT level.
-- Output Columns: shared_skill, student_1_name, s1_level, student_2_name, s2_level
-- Expected Result: Distinct student pairs sharing advanced technical proficiencies.
-- ----------------------------------------------------------------------------
SELECT sk.name AS shared_skill,
       s1.roll_no AS student_1_roll, s1.name AS student_1_name, ss1.proficiency_level AS s1_level,
       s2.roll_no AS student_2_roll, s2.name AS student_2_name, ss2.proficiency_level AS s2_level
FROM student_skill ss1
INNER JOIN student_skill ss2 ON ss1.skill_id = ss2.skill_id AND ss1.roll_no < ss2.roll_no
INNER JOIN skill sk ON ss1.skill_id = sk.skill_id
INNER JOIN student s1 ON ss1.roll_no = s1.roll_no
INNER JOIN student s2 ON ss2.roll_no = s2.roll_no
WHERE ss1.proficiency_level IN ('ADVANCED', 'EXPERT')
  AND ss2.proficiency_level IN ('ADVANCED', 'EXPERT')
ORDER BY shared_skill, student_1_roll
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 31: Admission-Year Filter
-- Purpose: Retrieve students admitted in 2024 (Senior cohort) and their registered skill counts.
-- Output Columns: roll_no, name, program, admission_year, reputation_points, total_skills_listed
-- Expected Result: Senior students admitted in 2024 sorted by reputation points descending.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.admission_year, s.reputation_points,
       COUNT(ss.skill_id) AS total_skills_listed
FROM student s
LEFT JOIN student_skill ss ON s.roll_no = ss.roll_no
WHERE s.admission_year = 2024
GROUP BY s.roll_no, s.name, s.program, s.admission_year, s.reputation_points
ORDER BY s.reputation_points DESC, s.roll_no ASC;

-- ----------------------------------------------------------------------------
-- QUERY 32: Counts by Program and Year Extracted from roll_no via SUBSTRING
-- Purpose: Extract year and program directly from roll_no string and aggregate student counts.
-- Output Columns: extracted_year, extracted_program, enrolled_student_count
-- Expected Result: Aggregated matrix matching stored admission_year and program.
-- ----------------------------------------------------------------------------
SELECT 
    SUBSTRING(s.roll_no, 1, 4) AS extracted_year,
    CASE 
        WHEN s.roll_no LIKE '____BTECH%' THEN 'BTECH'
        WHEN s.roll_no LIKE '____BBA%'   THEN 'BBA'
        WHEN s.roll_no LIKE '____BDES%'  THEN 'BDES'
    END AS extracted_program,
    COUNT(*) AS enrolled_student_count
FROM student s
GROUP BY extracted_year, extracted_program
ORDER BY extracted_year ASC, extracted_program ASC;

-- ----------------------------------------------------------------------------
-- QUERY 33: Students Teaching Multiple Skills
-- Purpose: Identify versatile mentors who have marked can_teach = TRUE for 2 or more skills.
-- Output Columns: roll_no, name, program, teachable_skill_count, teachable_skills
-- Expected Result: Mentors with 2+ teachable skills and concatenated skill names.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program,
       COUNT(ss.skill_id) AS teachable_skill_count,
       GROUP_CONCAT(sk.name ORDER BY sk.name SEPARATOR ', ') AS teachable_skills
FROM student s
INNER JOIN student_skill ss ON s.roll_no = ss.roll_no
INNER JOIN skill sk ON ss.skill_id = sk.skill_id
WHERE ss.can_teach = TRUE
GROUP BY s.roll_no, s.name, s.program
HAVING COUNT(ss.skill_id) >= 2
ORDER BY teachable_skill_count DESC, s.name ASC;

-- ----------------------------------------------------------------------------
-- QUERY 34: Students who were BOTH Mentor and Learner in COMPLETED Sessions
-- Purpose: Identify well-rounded students who have both mentored others and learned from peers.
-- Output Columns: roll_no, name, program, email, completed_as_mentor, completed_as_learner
-- Expected Result: Gauri Khandelwal (2025BTECH007) with 2 sessions as mentor and 1 as learner.
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.email,
       (SELECT COUNT(*) FROM learning_session ls1 WHERE ls1.mentor_roll_no = s.roll_no AND ls1.status = 'COMPLETED') AS completed_as_mentor,
       (SELECT COUNT(*) FROM learning_session ls2 WHERE ls2.learner_roll_no = s.roll_no AND ls2.status = 'COMPLETED') AS completed_as_learner
FROM student s
WHERE s.roll_no IN (
    SELECT mentor_roll_no FROM learning_session WHERE status = 'COMPLETED'
)
AND s.roll_no IN (
    SELECT learner_roll_no FROM learning_session WHERE status = 'COMPLETED'
)
ORDER BY s.roll_no ASC;
