-- ============================================================================
-- SkillSwap JKLU - SQL Demonstration Queries (1 through 34)
-- Engine: MySQL 8.0+
-- Prerequisites: schema.sql + seed.sql loaded into database 'skillswap'
-- Usage: mysql -u skillswap -pskillswap_pass -h 127.0.0.1 -P 3306 skillswap < test_queries.sql
-- ============================================================================

USE skillswap;

-- ----------------------------------------------------------------------------
-- QUERY 1: SELECT / DISTINCT / WHERE / ORDER BY / LIMIT
-- Purpose: Find all distinct programs and admission cohorts with student counts.
-- Output Columns: program, admission_year, student_count
-- ----------------------------------------------------------------------------
SELECT DISTINCT s.program, s.admission_year, COUNT(s.roll_no) AS student_count
FROM student s
GROUP BY s.program, s.admission_year
ORDER BY s.admission_year DESC, s.program ASC;

-- ----------------------------------------------------------------------------
-- QUERY 2: INSERT / UPDATE / DELETE in Transaction with ROLLBACK (ACID Test)
-- Purpose: Verify ACID transaction safety: insert a skill, update description, verify, delete, and rollback.
-- Output Columns: status_message, skill_id, name, description
-- ----------------------------------------------------------------------------
START TRANSACTION;

INSERT INTO skill (name, category, description) 
VALUES ('Cybersecurity Fundamentals Demo', 'Computer Science', 'Network defence and ethical hacking.');

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
-- QUERY 3: Find Students by Academic Program (Filter & Sort)
-- Purpose: Retrieve all students enrolled in BTECH ordered by admission year and roll number.
-- Output Columns: roll_no, name, email, program, admission_year
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.email, s.program, s.admission_year
FROM student s
WHERE s.program = 'BTECH'
ORDER BY s.admission_year ASC, s.roll_no ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 4: INNER JOIN (Students and Their Possessed Skills)
-- Purpose: List students along with their registered current skills and proficiency levels.
-- Output Columns: roll_no, student_name, skill_name, category, proficiency_level
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name AS student_name, sk.name AS skill_name, sk.category, ss.proficiency_level
FROM student s
INNER JOIN student_skill ss ON s.roll_no = ss.roll_no
INNER JOIN skill sk ON ss.skill_id = sk.skill_id
ORDER BY s.roll_no ASC, sk.name ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 5: Find Students Who Want to Learn a Particular Skill (Desired Skills)
-- Purpose: Retrieve all students desiring to learn 'Python' or 'DSA'.
-- Output Columns: roll_no, student_name, program, desired_skill, category
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name AS student_name, s.program, sk.name AS desired_skill, sk.category
FROM student s
INNER JOIN student_desired_skill sds ON s.roll_no = sds.roll_no
INNER JOIN skill sk ON sds.skill_id = sk.skill_id
WHERE sk.name IN ('Python', 'DSA', 'Web Development')
ORDER BY sk.name ASC, s.roll_no ASC;

-- ----------------------------------------------------------------------------
-- QUERY 6: Self-Join (Find Students Sharing Common Programs and Cohorts)
-- Purpose: Identify distinct pairs of students in the same program and admission cohort.
-- Output Columns: student_1_roll, student_1_name, student_2_roll, student_2_name, shared_program, cohort_year
-- ----------------------------------------------------------------------------
SELECT s1.roll_no AS student_1_roll, s1.name AS student_1_name,
       s2.roll_no AS student_2_roll, s2.name AS student_2_name,
       s1.program AS shared_program, s1.admission_year AS cohort_year
FROM student s1
INNER JOIN student s2 ON s1.program = s2.program 
                     AND s1.admission_year = s2.admission_year 
                     AND s1.roll_no < s2.roll_no
ORDER BY shared_program, cohort_year, student_1_roll, student_2_roll
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 7: Find Students with Matching Current and Desired Skills (Skill Matching)
-- Purpose: Match students who possess skill X with students who want to learn skill X.
-- Output Columns: skill_name, mentor_roll, mentor_name, learner_roll, learner_name
-- ----------------------------------------------------------------------------
SELECT sk.name AS skill_name,
       mentor.roll_no AS mentor_roll, mentor.name AS mentor_name,
       learner.roll_no AS learner_roll, learner.name AS learner_name
FROM student_skill ss
INNER JOIN student_desired_skill sds ON ss.skill_id = sds.skill_id AND ss.roll_no <> sds.roll_no
INNER JOIN skill sk ON ss.skill_id = sk.skill_id
INNER JOIN student mentor ON ss.roll_no = mentor.roll_no
INNER JOIN student learner ON sds.roll_no = learner.roll_no
ORDER BY sk.name ASC, mentor_roll ASC, learner_roll ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 8: LEFT JOIN / NOT EXISTS (Students Who Have Never Mentored Anyone)
-- Purpose: Find students who have not yet conducted any mentorship sessions.
-- Output Columns: roll_no, name, program, session_count
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, COUNT(ls.session_id) AS sessions_mentored
FROM student s
LEFT JOIN learning_session ls ON s.roll_no = ls.mentor_roll_no
GROUP BY s.roll_no, s.name, s.program
HAVING COUNT(ls.session_id) = 0
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 9: Find Students Without Experience Records (NOT EXISTS Subquery)
-- Purpose: Retrieve registered students who currently have zero portfolio/experience entries.
-- Output Columns: roll_no, name, email, program
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.email, s.program
FROM student s
WHERE NOT EXISTS (
    SELECT 1 FROM experience e WHERE e.roll_no = s.roll_no
)
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 10: COUNT / SUM / AVG / MIN / MAX Aggregate Functions
-- Purpose: Aggregate metrics on student reputation and admission cohort years.
-- Output Columns: total_students, min_year, max_year, avg_reputation, total_reputation
-- ----------------------------------------------------------------------------
SELECT COUNT(s.roll_no) AS total_students,
       MIN(s.admission_year) AS earliest_cohort,
       MAX(s.admission_year) AS latest_cohort,
       ROUND(AVG(s.reputation_points), 2) AS avg_reputation,
       SUM(s.reputation_points) AS total_reputation
FROM student s;

-- ----------------------------------------------------------------------------
-- QUERY 11: GROUP BY + HAVING (Skills Possessed by Multiple Students)
-- Purpose: Identify popular skills possessed by at least 2 students.
-- Output Columns: skill_id, skill_name, category, student_count
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category, COUNT(ss.roll_no) AS student_count
FROM skill sk
INNER JOIN student_skill ss ON sk.skill_id = ss.skill_id
GROUP BY sk.skill_id, sk.name, sk.category
HAVING COUNT(ss.roll_no) >= 2
ORDER BY student_count DESC, sk.name ASC;

-- ----------------------------------------------------------------------------
-- QUERY 12: Nested Subquery (Students Possessing Above-Average Number of Skills)
-- Purpose: Find students whose total registered skill count exceeds the student average.
-- Output Columns: roll_no, name, skill_count
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, COUNT(ss.skill_id) AS skill_count
FROM student s
INNER JOIN student_skill ss ON s.roll_no = ss.roll_no
GROUP BY s.roll_no, s.name
HAVING COUNT(ss.skill_id) > (
    SELECT AVG(skill_count) FROM (
        SELECT COUNT(skill_id) AS skill_count
        FROM student_skill
        GROUP BY roll_no
    ) AS avg_tbl
)
ORDER BY skill_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 13: Correlated Subquery
-- Purpose: List students along with count of skills they want to learn.
-- Output Columns: roll_no, name, program, desired_skill_count
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program,
       (SELECT COUNT(*) FROM student_desired_skill sds WHERE sds.roll_no = s.roll_no) AS desired_skill_count
FROM student s
ORDER BY desired_skill_count DESC, s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 14: Available Marketplace Listings (Preserving Original Submitted Price)
-- Purpose: Retrieve available items with seller information and submitted price text.
-- Output Columns: listing_id, title, category, price, original_price_text, seller_roll, seller_name
-- ----------------------------------------------------------------------------
SELECT l.listing_id, l.title, l.category, l.price, l.original_price_text,
       s.roll_no AS seller_roll, s.name AS seller_name
FROM listing l
INNER JOIN student s ON l.seller_roll_no = s.roll_no
WHERE l.status = 'AVAILABLE'
ORDER BY l.price ASC;

-- ----------------------------------------------------------------------------
-- QUERY 15: Count Students by Program (Cohort Distribution)
-- Purpose: Academic distribution of students enrolled across programs.
-- Output Columns: program, student_count, percentage_share
-- ----------------------------------------------------------------------------
SELECT s.program,
       COUNT(s.roll_no) AS student_count,
       ROUND(COUNT(s.roll_no) * 100.0 / (SELECT COUNT(*) FROM student), 1) AS percentage_share
FROM student s
GROUP BY s.program
ORDER BY student_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 16: Top 10 by Reputation (Window Function DENSE_RANK)
-- Purpose: Rank students by reputation points using MySQL window function.
-- Output Columns: rank_pos, roll_no, name, program, reputation_points
-- ----------------------------------------------------------------------------
SELECT DENSE_RANK() OVER (ORDER BY s.reputation_points DESC, s.roll_no ASC) AS rank_pos,
       s.roll_no, s.name, s.program, s.reputation_points
FROM student s
ORDER BY rank_pos ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 17: Multi-table Join Across Session Lifecycle
-- Purpose: Full relational join of sessions, mentor, learner, and skill catalog.
-- Output Columns: session_id, topic, skill_name, mentor_name, learner_name, mode, status
-- ----------------------------------------------------------------------------
SELECT ls.session_id, ls.topic, sk.name AS skill_name,
       m.name AS mentor_name, l.name AS learner_name,
       ls.mode, ls.status
FROM learning_session ls
INNER JOIN student m ON ls.mentor_roll_no = m.roll_no
INNER JOIN student l ON ls.learner_roll_no = l.roll_no
INNER JOIN skill sk ON ls.skill_id = sk.skill_id
ORDER BY ls.session_id ASC;

-- ----------------------------------------------------------------------------
-- QUERY 18: Calculate Average Review Ratings per Mentor
-- Purpose: Compute average rating and review volume received by mentors.
-- Output Columns: mentor_roll_no, mentor_name, review_count, avg_rating
-- ----------------------------------------------------------------------------
SELECT s.roll_no AS mentor_roll_no, s.name AS mentor_name,
       COUNT(r.session_id) AS review_count,
       ROUND(COALESCE(AVG(r.rating), 0), 2) AS avg_rating
FROM student s
LEFT JOIN review r ON s.roll_no = r.reviewee_roll_no
GROUP BY s.roll_no, s.name
ORDER BY avg_rating DESC, review_count DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 19: Count Completed Sessions per Skill
-- Purpose: Measure campus learning demand by counting completed sessions per subject.
-- Output Columns: skill_id, skill_name, category, completed_count
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category,
       COUNT(ls.session_id) AS completed_session_count
FROM skill sk
LEFT JOIN learning_session ls ON sk.skill_id = ls.skill_id AND ls.status = 'COMPLETED'
GROUP BY sk.skill_id, sk.name, sk.category
ORDER BY completed_session_count DESC, sk.name ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 20: Upcoming Sessions (Parameterized with Collation-Safe Variable)
-- Purpose: Retrieve future scheduled sessions for a student.
-- Output Columns: session_id, topic, skill_name, mode, scheduled_at, status
-- ----------------------------------------------------------------------------
SET @target_roll = _utf8mb4'2025BTECH027' COLLATE utf8mb4_unicode_ci;

SELECT ls.session_id, ls.topic, sk.name AS skill_name, ls.mode,
       ls.scheduled_at, ls.status
FROM learning_session ls
INNER JOIN skill sk ON ls.skill_id = sk.skill_id
WHERE (ls.mentor_roll_no = @target_roll OR ls.learner_roll_no = @target_roll)
  AND ls.scheduled_at >= NOW()
ORDER BY ls.scheduled_at ASC;

-- ----------------------------------------------------------------------------
-- QUERY 21: CASE Statement (Cohort Seniority Classification)
-- Purpose: Classify students into academic cohorts using CASE expressions.
-- Output Columns: roll_no, name, program, admission_year, cohort_stage
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.admission_year,
       CASE 
           WHEN s.admission_year = 2024 THEN 'Senior Cohort (3rd/4th Year)'
           WHEN s.admission_year = 2025 THEN 'Sophomore Cohort (2nd Year)'
           WHEN s.admission_year = 2026 THEN 'Freshman Cohort (1st Year)'
           ELSE 'Other Cohort'
       END AS cohort_stage
FROM student s
ORDER BY s.admission_year ASC, s.roll_no ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 22: Marketplace Volume and Status Aggregation
-- Purpose: Aggregate listings count and sales volume across available and sold items.
-- Output Columns: status, item_count, total_value, avg_price
-- ----------------------------------------------------------------------------
SELECT l.status,
       COUNT(l.listing_id) AS item_count,
       COALESCE(SUM(l.price), 0.00) AS total_value,
       ROUND(COALESCE(AVG(l.price), 0.00), 2) AS avg_price
FROM listing l
GROUP BY l.status;

-- ----------------------------------------------------------------------------
-- QUERY 23: Students Sharing Same Skills (Self-Join on student_skill)
-- Purpose: Find distinct student pairs possessing the exact same skill.
-- Output Columns: shared_skill, student_1, student_2
-- ----------------------------------------------------------------------------
SELECT sk.name AS shared_skill,
       s1.name AS student_1_name, s1.roll_no AS student_1_roll,
       s2.name AS student_2_name, s2.roll_no AS student_2_roll
FROM student_skill ss1
INNER JOIN student_skill ss2 ON ss1.skill_id = ss2.skill_id AND ss1.roll_no < ss2.roll_no
INNER JOIN skill sk ON ss1.skill_id = sk.skill_id
INNER JOIN student s1 ON ss1.roll_no = s1.roll_no
INNER JOIN student s2 ON ss2.roll_no = s2.roll_no
ORDER BY shared_skill ASC, student_1_roll ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 24: Skills Never Requested in Learning Sessions (EXISTS / NOT EXISTS)
-- Purpose: Identify skills in catalog that have not been scheduled in any session.
-- Output Columns: skill_id, skill_name, category
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category
FROM skill sk
WHERE NOT EXISTS (
    SELECT 1 FROM learning_session ls WHERE ls.skill_id = sk.skill_id
)
ORDER BY sk.name ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 25: Students with No Reviews (LEFT JOIN / IS NULL)
-- Purpose: Identify students who have received no peer reviews.
-- Output Columns: roll_no, name, program, reputation_points
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.reputation_points
FROM student s
LEFT JOIN review r ON s.roll_no = r.reviewee_roll_no
WHERE r.session_id IS NULL
ORDER BY s.roll_no ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 26: Marketplace Listings by Seller + Pricing Transparency
-- Purpose: List campus marketplace items along with seller email and original text note.
-- Output Columns: listing_id, title, price, original_price_text, seller_name, seller_email
-- ----------------------------------------------------------------------------
SELECT l.listing_id, l.title, l.price, l.original_price_text,
       s.name AS seller_name, s.email AS seller_email
FROM listing l
INNER JOIN student s ON l.seller_roll_no = s.roll_no
ORDER BY l.price DESC;

-- ----------------------------------------------------------------------------
-- QUERY 27: Program-wise Student Count and Reputation Distribution
-- Purpose: Aggregate student count, total reputation, and average reputation by program.
-- Output Columns: program, student_count, total_reputation, avg_reputation
-- ----------------------------------------------------------------------------
SELECT s.program,
       COUNT(s.roll_no) AS student_count,
       COALESCE(SUM(s.reputation_points), 0) AS total_reputation,
       ROUND(COALESCE(AVG(s.reputation_points), 0), 2) AS avg_reputation
FROM student s
GROUP BY s.program
ORDER BY student_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 28: Sessions by Status Lifecycle (State Machine Audit)
-- Purpose: Count sessions across all 5 states (REQUESTED, ACCEPTED, REJECTED, CANCELLED, COMPLETED).
-- Output Columns: status, session_count, percentage_share
-- ----------------------------------------------------------------------------
SELECT ls.status,
       COUNT(ls.session_id) AS session_count,
       ROUND(COUNT(ls.session_id) * 100.0 / GREATEST((SELECT COUNT(*) FROM learning_session), 1), 1) AS percentage_share
FROM learning_session ls
GROUP BY ls.status
ORDER BY session_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 29: Mentors with Average Rating Above Threshold
-- Purpose: Find mentors maintaining average rating above parameter threshold.
-- Output Columns: roll_no, name, review_count, avg_rating
-- ----------------------------------------------------------------------------
SET @min_rating = 4.0;

SELECT s.roll_no, s.name,
       COUNT(r.session_id) AS review_count,
       ROUND(AVG(r.rating), 2) AS avg_rating
FROM student s
INNER JOIN review r ON s.roll_no = r.reviewee_roll_no
GROUP BY s.roll_no, s.name
HAVING AVG(r.rating) >= @min_rating
ORDER BY avg_rating DESC;

-- ----------------------------------------------------------------------------
-- QUERY 30: Find Students Possessing Multiple Registered Skills
-- Purpose: Identify versatile students possessing 3 or more registered skills.
-- Output Columns: roll_no, student_name, program, skill_count
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name AS student_name, s.program, COUNT(ss.skill_id) AS skill_count
FROM student s
INNER JOIN student_skill ss ON s.roll_no = ss.roll_no
GROUP BY s.roll_no, s.name, s.program
HAVING COUNT(ss.skill_id) >= 3
ORDER BY skill_count DESC, s.name ASC;

-- ----------------------------------------------------------------------------
-- QUERY 31: Filter by Cohort Admission Year
-- Purpose: Retrieve students belonging to the 2025 cohort and count their skills.
-- Output Columns: roll_no, name, program, admission_year, total_skills
-- ----------------------------------------------------------------------------
SELECT s.roll_no, s.name, s.program, s.admission_year,
       COUNT(ss.skill_id) AS total_skills
FROM student s
LEFT JOIN student_skill ss ON s.roll_no = ss.roll_no
WHERE s.admission_year = 2025
GROUP BY s.roll_no, s.name, s.program, s.admission_year
ORDER BY total_skills DESC, s.roll_no ASC;

-- ----------------------------------------------------------------------------
-- QUERY 32: Counts by Program and Year Extracted from roll_no via SUBSTRING
-- Purpose: Verify consistency between roll_no prefix and program/year columns.
-- Output Columns: extracted_year, extracted_prog, student_count
-- ----------------------------------------------------------------------------
SELECT SUBSTRING(s.roll_no, 1, 4) AS extracted_year,
       SUBSTRING(s.roll_no, 5, LENGTH(s.program)) AS extracted_prog,
       COUNT(s.roll_no) AS student_count
FROM student s
GROUP BY extracted_year, extracted_prog
ORDER BY extracted_year ASC, extracted_prog ASC;

-- ----------------------------------------------------------------------------
-- QUERY 33: Survey Import Audit Provenance Verification
-- Purpose: Verify survey import status breakdown and total submissions processed.
-- Output Columns: import_status, submission_count, percentage
-- ----------------------------------------------------------------------------
SELECT sia.import_status,
       COUNT(sia.submission_id) AS submission_count,
       ROUND(COUNT(sia.submission_id) * 100.0 / (SELECT COUNT(*) FROM survey_import_audit), 1) AS percentage
FROM survey_import_audit sia
GROUP BY sia.import_status
ORDER BY submission_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 34: Desired Skills Demand Ranking
-- Purpose: Rank skills by the number of students who desire to learn them.
-- Output Columns: skill_id, skill_name, category, students_seeking
-- ----------------------------------------------------------------------------
SELECT sk.skill_id, sk.name AS skill_name, sk.category,
       COUNT(sds.roll_no) AS students_seeking
FROM skill sk
INNER JOIN student_desired_skill sds ON sk.skill_id = sds.skill_id
GROUP BY sk.skill_id, sk.name, sk.category
ORDER BY students_seeking DESC, sk.name ASC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- QUERY 35: Marketplace Inquiries Received by Seller with Relational Details
-- Purpose: Retrieve all student inquiries received by sellers, joining buyer profile, listing, and inquiry status.
-- Output Columns: inquiry_id, listing_title, buyer_roll, buyer_name, buyer_email, inquiry_status, created_at
-- ----------------------------------------------------------------------------
SELECT mi.inquiry_id,
       l.title AS listing_title,
       mi.buyer_roll_no AS buyer_roll,
       b.name AS buyer_name,
       b.email AS buyer_email,
       mi.inquiry_status,
       mi.created_at
FROM marketplace_inquiry mi
INNER JOIN listing l ON mi.listing_id = l.listing_id
INNER JOIN student b ON mi.buyer_roll_no = b.roll_no
ORDER BY mi.created_at DESC;

-- ----------------------------------------------------------------------------
-- QUERY 36: Unread Notifications for Students (Recipient Count and Message Details)
-- Purpose: Identify active unread notifications per student to power UI notification badges.
-- Output Columns: recipient_roll_no, recipient_name, unread_count, latest_notification
-- ----------------------------------------------------------------------------
SELECT n.recipient_roll_no,
       s.name AS recipient_name,
       COUNT(n.notification_id) AS unread_count,
       MAX(n.created_at) AS latest_notification_time
FROM notification n
INNER JOIN student s ON n.recipient_roll_no = s.roll_no
WHERE n.is_read = FALSE
GROUP BY n.recipient_roll_no, s.name
ORDER BY unread_count DESC;

-- ----------------------------------------------------------------------------
-- QUERY 37: Marketplace Listing Demand (Inquiry Volume per Available Listing)
-- Purpose: Aggregate buyer interest per listing to identify high-demand student items.
-- Output Columns: listing_id, title, seller_name, price, inquiry_count
-- ----------------------------------------------------------------------------
SELECT l.listing_id,
       l.title,
       s.name AS seller_name,
       l.price,
       COUNT(mi.inquiry_id) AS total_inquiries
FROM listing l
INNER JOIN student s ON l.seller_roll_no = s.roll_no
LEFT JOIN marketplace_inquiry mi ON l.listing_id = mi.listing_id
GROUP BY l.listing_id, l.title, s.name, l.price
ORDER BY total_inquiries DESC, l.price ASC;

