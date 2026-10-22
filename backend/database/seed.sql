-- ============================================================================
-- SkillSwap JKLU - Realistic Seed Data
-- 34 Students (BTECH, BBA, BDES across 2024, 2025, 2026)
-- 18 Skills, Sessions in all 5 statuses, Reviews, Experiences, Listings
-- Passwords:
--   Admin:   Admin@JKLU2026
--   Student: Student@JKLU2026
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE review;
TRUNCATE TABLE reputation_history;
TRUNCATE TABLE learning_session;
TRUNCATE TABLE listing;
TRUNCATE TABLE experience;
TRUNCATE TABLE student_skill;
TRUNCATE TABLE skill;
TRUNCATE TABLE email_verification_token;
TRUNCATE TABLE auth_account;
TRUNCATE TABLE student;
TRUNCATE TABLE department;
SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. DEPARTMENTS
-- ----------------------------------------------------------------------------
INSERT INTO department (d_id, name, program) VALUES
(1, 'Computer Science and Engineering', 'BTECH'),
(2, 'Artificial Intelligence and Data Science', 'BTECH'),
(3, 'Electronics and Communication Engineering', 'BTECH'),
(4, 'Institute of Management', 'BBA'),
(5, 'Institute of Design', 'BDES');

-- ----------------------------------------------------------------------------
-- 2. STUDENTS (34 Students: 18 BTECH, 8 BBA, 8 BDES)
-- ----------------------------------------------------------------------------
INSERT INTO student (roll_no, name, email, phone, d_id, program, admission_year, reputation_points, created_at) VALUES
-- BTECH 2024 (Seniors)
('2024BTECH001', 'Aarav Sharma',     'aarav.sharma@jklu.edu.in',     '9829011001', 1, 'BTECH', 2024, 40, '2024-08-01 10:00:00'),
('2024BTECH002', 'Bhavya Patel',     'bhavya.patel@jklu.edu.in',     '9829011002', 1, 'BTECH', 2024, 50, '2024-08-01 10:05:00'),
('2024BTECH003', 'Chirag Singhal',   'chirag.singhal@jklu.edu.in',   '9829011003', 2, 'BTECH', 2024, 30, '2024-08-01 10:10:00'),
('2024BTECH004', 'Divya Jain',       'divya.jain@jklu.edu.in',       NULL,         2, 'BTECH', 2024, 20, '2024-08-01 10:15:00'),
('2024BTECH005', 'Eshan Verma',      'eshan.verma@jklu.edu.in',      '9829011005', 3, 'BTECH', 2024, 10, '2024-08-01 10:20:00'),
('2024BTECH006', 'Farhan Ali',       'farhan.ali@jklu.edu.in',       '9829011006', 1, 'BTECH', 2024,  0, '2024-08-01 10:25:00'),

-- BTECH 2025 (Juniors)
('2025BTECH007', 'Gauri Khandelwal', 'gauri.khandelwal@jklu.edu.in', '9829011007', 1, 'BTECH', 2025, 20, '2025-08-01 10:00:00'),
('2025BTECH008', 'Harsh Vardhan',    'harsh.vardhan@jklu.edu.in',    '9829011008', 2, 'BTECH', 2025, 10, '2025-08-01 10:05:00'),
('2025BTECH009', 'Isha Meena',       'isha.meena@jklu.edu.in',       NULL,         1, 'BTECH', 2025, 10, '2025-08-01 10:10:00'),
('2025BTECH010', 'Jayesh Mathur',    'jayesh.mathur@jklu.edu.in',    '9829011010', 3, 'BTECH', 2025,  0, '2025-08-01 10:15:00'),
('2025BTECH011', 'Kavya Soni',       'kavya.soni@jklu.edu.in',       '9829011011', 1, 'BTECH', 2025,  0, '2025-08-01 10:20:00'),
('2025BTECH012', 'Lakshya Gupta',    'lakshya.gupta@jklu.edu.in',    '9829011012', 2, 'BTECH', 2025,  0, '2025-08-01 10:25:00'),

-- BTECH 2026 (Freshmen)
('2026BTECH013', 'Manish Purohit',   'manish.purohit@jklu.edu.in',   '9829011013', 1, 'BTECH', 2026,  0, '2026-08-01 10:00:00'),
('2026BTECH014', 'Nandini Rathore',  'nandini.rathore@jklu.edu.in',  '9829011014', 2, 'BTECH', 2026,  0, '2026-08-01 10:05:00'),
('2026BTECH015', 'Omkar Joshi',      'omkar.joshi@jklu.edu.in',      '9829011015', 3, 'BTECH', 2026,  0, '2026-08-01 10:10:00'),
('2026BTECH016', 'Priya Tanwar',     'priya.tanwar@jklu.edu.in',     NULL,         1, 'BTECH', 2026,  0, '2026-08-01 10:15:00'),
('2026BTECH017', 'Qasim Khan',       'qasim.khan@jklu.edu.in',       '9829011017', 2, 'BTECH', 2026,  0, '2026-08-01 10:20:00'),
('2026BTECH018', 'Rohit Sen',        'rohit.sen@jklu.edu.in',        NULL,         1, 'BTECH', 2026,  0, '2026-08-01 10:25:00'),

-- BBA 2024, 2025, 2026
('2024BBA001',   'Sneha Agarwal',    'sneha.agarwal@jklu.edu.in',    '9829012001', 4, 'BBA',   2024, 30, '2024-08-01 11:00:00'),
('2024BBA002',   'Tanmay Tiwari',    'tanmay.tiwari@jklu.edu.in',    '9829012002', 4, 'BBA',   2024, 20, '2024-08-01 11:05:00'),
('2025BBA003',   'Urvi Saxena',      'urvi.saxena@jklu.edu.in',      '9829012003', 4, 'BBA',   2025, 10, '2025-08-01 11:00:00'),
('2025BBA004',   'Varun Chopra',     'varun.chopra@jklu.edu.in',     NULL,         4, 'BBA',   2025,  0, '2025-08-01 11:05:00'),
('2025BBA005',   'Vidhi Mittal',     'vidhi.mittal@jklu.edu.in',     '9829012005', 4, 'BBA',   2025,  0, '2025-08-01 11:10:00'),
('2026BBA006',   'Yash Shekhawat',   'yash.shekhawat@jklu.edu.in',   '9829012006', 4, 'BBA',   2026,  0, '2026-08-01 11:00:00'),
('2026BBA007',   'Zoya Siddiqui',    'zoya.siddiqui@jklu.edu.in',    '9829012007', 4, 'BBA',   2026,  0, '2026-08-01 11:05:00'),
('2026BBA008',   'Ananya Goyal',     'ananya.goyal@jklu.edu.in',     NULL,         4, 'BBA',   2026,  0, '2026-08-01 11:10:00'),

-- BDES 2024, 2025, 2026
('2024BDES001',  'Bharat Bhushan',   'bharat.bhushan@jklu.edu.in',   '9829013001', 5, 'BDES',  2024, 30, '2024-08-01 12:00:00'),
('2024BDES002',  'Chhavi Soni',      'chhavi.soni@jklu.edu.in',      '9829013002', 5, 'BDES',  2024, 20, '2024-08-01 12:05:00'),
('2025BDES003',  'Devvrat Rao',      'devvrat.rao@jklu.edu.in',      NULL,         5, 'BDES',  2025, 10, '2025-08-01 12:00:00'),
('2025BDES004',  'Ekta Rawat',       'ekta.rawat@jklu.edu.in',       '9829013004', 5, 'BDES',  2025,  0, '2025-08-01 12:05:00'),
('2025BDES005',  'Girish Sharma',    'girish.sharma@jklu.edu.in',    '9829013005', 5, 'BDES',  2025,  0, '2025-08-01 12:10:00'),
('2026BDES006',  'Himani Gaur',      'himani.gaur@jklu.edu.in',      '9829013006', 5, 'BDES',  2026,  0, '2026-08-01 12:00:00'),
('2026BDES007',  'Ishaan Dixit',     'ishaan.dixit@jklu.edu.in',     '9829013007', 5, 'BDES',  2026,  0, '2026-08-01 12:05:00'),
('2026BDES008',  'Jiya Chauhan',     'jiya.chauhan@jklu.edu.in',     NULL,         5, 'BDES',  2026,  0, '2026-08-01 12:10:00');

-- ----------------------------------------------------------------------------
-- 3. AUTH ACCOUNTS (Admin + Students)
-- Passwords:
--   Admin:   $argon2id$v=19$m=65536,t=3,p=4$X18pS7PfX70O2kY6sbzyaQ$WutVtOKXHcuFjniJ/L8cyzVuA+d8JF73bXJvnBKWUs4  (Admin@JKLU2026)
--   Student: $argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs  (Student@JKLU2026)
-- ----------------------------------------------------------------------------
INSERT INTO auth_account (roll_no, password_hash, role, account_status, email_verified, token_version, created_at) VALUES
('2024BTECH001', '$argon2id$v=19$m=65536,t=3,p=4$X18pS7PfX70O2kY6sbzyaQ$WutVtOKXHcuFjniJ/L8cyzVuA+d8JF73bXJvnBKWUs4', 'ADMIN',   'ACTIVE',           TRUE,  1, '2024-08-01 10:00:00'),
('2024BTECH002', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 10:05:00'),
('2024BTECH003', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 10:10:00'),
('2024BTECH004', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 10:15:00'),
('2024BTECH005', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 10:20:00'),
('2024BTECH006', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 10:25:00'),
('2025BTECH007', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 10:00:00'),
('2025BTECH008', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 10:05:00'),
('2025BTECH009', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 10:10:00'),
('2025BTECH010', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 10:15:00'),
('2025BTECH011', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 10:20:00'),
('2025BTECH012', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 10:25:00'),
('2026BTECH013', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 10:00:00'),
('2026BTECH014', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 10:05:00'),
('2026BTECH015', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 10:10:00'),
('2026BTECH016', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'UNVERIFIED',       FALSE, 1, '2026-08-01 10:15:00'),
('2026BTECH017', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'PENDING_APPROVAL', TRUE,  1, '2026-08-01 10:20:00'),
('2026BTECH018', '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'SUSPENDED',        TRUE,  1, '2026-08-01 10:25:00'),
('2024BBA001',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 11:00:00'),
('2024BBA002',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 11:05:00'),
('2025BBA003',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 11:00:00'),
('2025BBA004',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 11:05:00'),
('2025BBA005',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 11:10:00'),
('2026BBA006',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 11:00:00'),
('2026BBA007',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 11:05:00'),
('2026BBA008',   '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 11:10:00'),
('2024BDES001',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 12:00:00'),
('2024BDES002',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2024-08-01 12:05:00'),
('2025BDES003',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 12:00:00'),
('2025BDES004',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 12:05:00'),
('2025BDES005',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2025-08-01 12:10:00'),
('2026BDES006',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 12:00:00'),
('2026BDES007',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 12:05:00'),
('2026BDES008',  '$argon2id$v=19$m=65536,t=3,p=4$MAFbqGsSpdi1Tg8JIUgmCQ$wWhJfbCG6IdioctbUzIe2bPrV1f6cr+viOeGeM5IRNs', 'STUDENT', 'ACTIVE',           TRUE,  1, '2026-08-01 12:10:00');

-- ----------------------------------------------------------------------------
-- 4. EMAIL VERIFICATION TOKENS
-- ----------------------------------------------------------------------------
INSERT INTO email_verification_token (token_id, roll_no, token_hash, expires_at, used_at, created_at) VALUES
(1, '2026BTECH016', 'a7f3484f932849208a8f89e2837498c8723487c8237498273498237498237498', DATE_ADD(NOW(), INTERVAL 24 HOUR), NULL, NOW()),
(2, '2026BTECH017', 'b8e4595e843950319b9f90f3948509d9834598d9348509384509348509348509', DATE_ADD(NOW(), INTERVAL 24 HOUR), NOW(), DATE_SUB(NOW(), INTERVAL 1 HOUR));

-- ----------------------------------------------------------------------------
-- 5. SKILLS (18 Skills across Computer Science, Design, Business, etc.)
-- ----------------------------------------------------------------------------
INSERT INTO skill (skill_id, name, category, description, created_at) VALUES
(1,  'Python Programming',           'Computer Science', 'Modern Python 3, object-oriented principles, and scripting.', '2024-08-01 09:00:00'),
(2,  'Database Management Systems',  'Computer Science', 'Relational design, normalization, SQL, indexing, transactions.', '2024-08-01 09:00:00'),
(3,  'React & Web Development',       'Computer Science', 'Frontend SPA architecture, React hooks, state management.', '2024-08-01 09:00:00'),
(4,  'Machine Learning',             'Data Science',     'Supervised and unsupervised models, evaluation metrics, scikit-learn.', '2024-08-01 09:00:00'),
(5,  'Data Structures & Algorithms', 'Computer Science', 'Arrays, linked lists, trees, graphs, sorting, dynamic programming.', '2024-08-01 09:00:00'),
(6,  'UI/UX Wireframing & Prototyping', 'Design',       'Figma component libraries, wireframing, user persona mapping.', '2024-08-01 09:00:00'),
(7,  'Design Thinking & Research',   'Design',           'User research, empathy mapping, ideation, iterative usability testing.', '2024-08-01 09:00:00'),
(8,  '3D Modeling & CAD',            'Design',           'SolidWorks, Blender 3D asset pipeline, spatial modeling.', '2024-08-01 09:00:00'),
(9,  'Graphic Design & Typography',  'Design',           'Visual balance, typography hierarchy, Adobe Illustrator, branding.', '2024-08-01 09:00:00'),
(10, 'Financial Accounting',         'Business',         'Balance sheets, ledger bookkeeping, corporate cash flow statements.', '2024-08-01 09:00:00'),
(11, 'Digital Marketing Strategy',   'Business',         'SEO, conversion funnels, SEM, social analytics, campaign ROI.', '2024-08-01 09:00:00'),
(12, 'Business Valuation & Pitching','Business',         'Startup decks, DCF modeling, venture capital presentation.', '2024-08-01 09:00:00'),
(13, 'Public Speaking & Debate',     'Communication',    'Persuasion techniques, impromptu speeches, parliamentary debate.', '2024-08-01 09:00:00'),
(14, 'Academic Research & Writing',  'Communication',    'LaTeX publication, IEEE formatting, research synthesis.', '2024-08-01 09:00:00'),
(15, 'Mobile Development (Flutter)', 'Computer Science', 'Cross-platform mobile apps using Dart and Flutter framework.', '2024-08-01 09:00:00'),
(16, 'Embedded Systems & Arduino',   'Electronics',      'Microcontroller programming, sensor integration, C/C++.', '2024-08-01 09:00:00'),
(17, 'Rust Systems Programming',     'Computer Science', 'Memory safety without garbage collection, borrow checker.', '2024-08-01 09:00:00'), -- Unused in sessions
(18, 'Quantitative Aptitude',        'General',          'Logical reasoning, permutations, probability for placements.', '2024-08-01 09:00:00'), -- Unused in sessions
(19, 'Acoustic & Electric Guitar',             'Music & Performing Arts', 'Chords, strumming patterns, fingerpicking techniques, tabs, and solo improvisation.', '2024-08-01 09:00:00'),
(20, 'Western & Contemporary Dance',           'Dance & Performing Arts', 'Hip-hop choreography, urban grooves, contemporary body isolation, and rhythm training.', '2024-08-01 09:00:00'),
(21, 'Classical Dance (Kathak & Bharatanatyam)', 'Dance & Performing Arts', 'Classical mudras, rhythmic footwork (tatkar), abhinaya expressions, and traditional thumri.', '2024-08-01 09:00:00'),
(22, 'Sketching & Acrylic Painting',           'Fine Arts & Visual Media', 'Pencil shading, facial proportions, perspective, canvas preparation, and acrylic mixing.', '2024-08-01 09:00:00'),
(23, 'Digital Photography & Lightroom',        'Fine Arts & Visual Media', 'DSLR exposure triangle, framing, golden hour portraits, and Adobe Lightroom CC color grading.', '2024-08-01 09:00:00'),
(24, 'Music Production & Beatmaking',          'Music & Performing Arts', 'FL Studio, Ableton Live, MIDI arrangement, beat programming, and sound synthesis.', '2024-08-01 09:00:00'),
(25, 'Vocal Music & Singing',                  'Music & Performing Arts', 'Vocal warmups, pitch accuracy, breathing techniques, riyaz, and acoustic singing.', '2024-08-01 09:00:00'),
(26, 'Creative Writing & Spoken Word',         'Literary & Creative Arts', 'Poetry composition, metaphor crafting, storytelling arcs, and open-mic stage performance.', '2024-08-01 09:00:00'),
(27, 'Chess Strategy & Tactics',               'Sports & Strategy',        'Opening principles, pin/fork tactics, pawn structures, endgame mastery, and time control.', '2024-08-01 09:00:00'),
(28, 'Video Editing & Cinematography',         'Fine Arts & Visual Media', 'Premiere Pro / DaVinci Resolve editing, cinematic transitions, color correction, and audio cleanup.', '2024-08-01 09:00:00');

-- ----------------------------------------------------------------------------
-- 6. STUDENT SKILLS (Mappings with proficiency and can_teach flag)
-- ----------------------------------------------------------------------------
INSERT INTO student_skill (roll_no, skill_id, proficiency_level, can_teach, created_at) VALUES
-- Aarav Sharma (BTECH 2024) - Mentor in Python, DBMS, DSA, Guitar, Chess
('2024BTECH001', 1,  'EXPERT',       TRUE,  '2024-08-05 10:00:00'),
('2024BTECH001', 2,  'EXPERT',       TRUE,  '2024-08-05 10:00:00'),
('2024BTECH001', 5,  'ADVANCED',     TRUE,  '2024-08-05 10:00:00'),
('2024BTECH001', 19, 'ADVANCED',     TRUE,  '2024-08-05 10:00:00'),
('2024BTECH001', 27, 'EXPERT',       TRUE,  '2024-08-05 10:00:00'),

-- Bhavya Patel (BTECH 2024) - Mentor in Python, React, ML, Music Production
('2024BTECH002', 1,  'EXPERT',       TRUE,  '2024-08-05 10:00:00'),
('2024BTECH002', 3,  'EXPERT',       TRUE,  '2024-08-05 10:00:00'),
('2024BTECH002', 4,  'ADVANCED',     TRUE,  '2024-08-05 10:00:00'),
('2024BTECH002', 24, 'EXPERT',       TRUE,  '2024-08-05 10:00:00'),

-- Chirag Singhal (BTECH 2024) - Mentor in ML and Python
('2024BTECH003', 1,  'ADVANCED',     TRUE,  '2024-08-05 10:00:00'),
('2024BTECH003', 4,  'EXPERT',       TRUE,  '2024-08-05 10:00:00'),

-- Divya Jain (BTECH 2024) - Mentor in React, Flutter, Dance
('2024BTECH004', 3,  'ADVANCED',     TRUE,  '2024-08-05 10:00:00'),
('2024BTECH004', 15, 'ADVANCED',     TRUE,  '2024-08-05 10:00:00'),
('2024BTECH004', 20, 'EXPERT',       TRUE,  '2024-08-05 10:00:00'),

-- Eshan Verma (BTECH 2024) - Mentor in Embedded Systems
('2024BTECH005', 16, 'EXPERT',       TRUE,  '2024-08-05 10:00:00'),

-- Gauri Khandelwal (BTECH 2025) - Learner & Mentor (Python, DBMS, Singing)
('2025BTECH007', 1,  'INTERMEDIATE', TRUE,  '2025-08-05 10:00:00'),
('2025BTECH007', 2,  'INTERMEDIATE', TRUE,  '2025-08-05 10:00:00'),
('2025BTECH007', 25, 'ADVANCED',     TRUE,  '2025-08-05 10:00:00'),

-- Harsh Vardhan (BTECH 2025)
('2025BTECH008', 4,  'INTERMEDIATE', TRUE,  '2025-08-05 10:00:00'),
('2025BTECH008', 5,  'INTERMEDIATE', FALSE, '2025-08-05 10:00:00'),

-- Isha Meena (BTECH 2025)
('2025BTECH009', 1,  'INTERMEDIATE', TRUE,  '2025-08-05 10:00:00'),
('2025BTECH009', 3,  'BEGINNER',     FALSE, '2025-08-05 10:00:00'),

-- Sneha Agarwal (BBA 2024) - Mentor in Accounting, Valuation, Creative Writing
('2024BBA001',   10, 'EXPERT',       TRUE,  '2024-08-05 11:00:00'),
('2024BBA001',   12, 'ADVANCED',     TRUE,  '2024-08-05 11:00:00'),
('2024BBA001',   13, 'ADVANCED',     TRUE,  '2024-08-05 11:00:00'),
('2024BBA001',   26, 'EXPERT',       TRUE,  '2024-08-05 11:00:00'),

-- Tanmay Tiwari (BBA 2024) - Mentor in Digital Marketing & Classical Dance
('2024BBA002',   11, 'EXPERT',       TRUE,  '2024-08-05 11:00:00'),
('2024BBA002',   13, 'ADVANCED',     TRUE,  '2024-08-05 11:00:00'),
('2024BBA002',   21, 'ADVANCED',     TRUE,  '2024-08-05 11:00:00'),

-- Urvi Saxena (BBA 2025)
('2025BBA003',   10, 'INTERMEDIATE', TRUE,  '2025-08-05 11:00:00'),
('2025BBA003',   11, 'INTERMEDIATE', FALSE, '2025-08-05 11:00:00'),

-- Bharat Bhushan (BDES 2024) - Mentor in UI/UX, Design Thinking, Fine Art Sketching
('2024BDES001',  6,  'EXPERT',       TRUE,  '2024-08-05 12:00:00'),
('2024BDES001',  7,  'EXPERT',       TRUE,  '2024-08-05 12:00:00'),
('2024BDES001',  9,  'ADVANCED',     TRUE,  '2024-08-05 12:00:00'),
('2024BDES001',  22, 'EXPERT',       TRUE,  '2024-08-05 12:00:00'),

-- Chhavi Soni (BDES 2024) - Mentor in 3D Modeling, Photography, Video Editing
('2024BDES002',  8,  'EXPERT',       TRUE,  '2024-08-05 12:00:00'),
('2024BDES002',  9,  'EXPERT',       TRUE,  '2024-08-05 12:00:00'),
('2024BDES002',  23, 'EXPERT',       TRUE,  '2024-08-05 12:00:00'),
('2024BDES002',  28, 'ADVANCED',     TRUE,  '2024-08-05 12:00:00'),

-- Devvrat Rao (BDES 2025)
('2025BDES003',  6,  'INTERMEDIATE', TRUE,  '2025-08-05 12:00:00'),
('2025BDES003',  8,  'BEGINNER',     FALSE, '2025-08-05 12:00:00'),
('2025BDES003',  22, 'ADVANCED',     TRUE,  '2025-08-05 12:00:00'),

-- Freshmen learners
('2026BTECH013', 1,  'BEGINNER',     FALSE, '2026-08-05 10:00:00'),
('2026BTECH013', 2,  'BEGINNER',     FALSE, '2026-08-05 10:00:00'),
('2026BTECH014', 3,  'BEGINNER',     FALSE, '2026-08-05 10:00:00'),
('2026BBA006',   10, 'BEGINNER',     FALSE, '2026-08-05 11:00:00'),
('2026BDES006',  6,  'BEGINNER',     FALSE, '2026-08-05 12:00:00');
-- Note: 2026BTECH018 has NO skills recorded (tested in edge cases)

-- ----------------------------------------------------------------------------
-- 7. LEARNING SESSIONS (All 5 statuses, past and future, credit_cost = 0)
-- ----------------------------------------------------------------------------
INSERT INTO learning_session (session_id, mentor_roll_no, learner_roll_no, skill_id, topic, mode, scheduled_at, meeting_link, status, credit_cost, created_at, updated_at) VALUES
-- COMPLETED SESSIONS (25 completed sessions across mentors)
-- Mentor: Aarav Sharma (2024BTECH001) - 4 completed
(1,  '2024BTECH001', '2025BTECH007', 1,  'Advanced Python Generators & Decorators', 'ONLINE',  '2025-09-10 16:00:00', 'https://meet.google.com/jkl-u-demo1', 'COMPLETED', 0, '2025-09-08 10:00:00', '2025-09-10 17:30:00'),
(2,  '2024BTECH001', '2025BTECH008', 2,  'Relational Normalization: 1NF to BCNF',   'OFFLINE', '2025-09-15 15:00:00', NULL,                                  'COMPLETED', 0, '2025-09-12 11:00:00', '2025-09-15 16:30:00'),
(3,  '2024BTECH001', '2026BTECH013', 1,  'Python OOP Fundamentals',                'ONLINE',  '2026-08-20 17:00:00', 'https://meet.google.com/jkl-u-demo3', 'COMPLETED', 0, '2026-08-18 09:00:00', '2026-08-20 18:00:00'),
(4,  '2024BTECH001', '2026BTECH014', 5,  'Binary Search and Two Pointer Approach',  'ONLINE',  '2026-09-05 16:00:00', 'https://meet.google.com/jkl-u-demo4', 'COMPLETED', 0, '2026-09-02 12:00:00', '2026-09-05 17:15:00'),

-- Mentor: Bhavya Patel (2024BTECH002) - 5 completed
(5,  '2024BTECH002', '2025BTECH009', 3,  'Building Component Systems in React',     'ONLINE',  '2025-10-02 18:00:00', 'https://meet.google.com/jkl-u-demo5', 'COMPLETED', 0, '2025-09-30 14:00:00', '2025-10-02 19:30:00'),
(6,  '2024BTECH002', '2025BTECH010', 1,  'Data Analysis with Pandas',              'OFFLINE', '2025-10-12 14:00:00', NULL,                                  'COMPLETED', 0, '2025-10-08 10:00:00', '2025-10-12 15:30:00'),
(7,  '2024BTECH002', '2026BTECH013', 3,  'State Management with Zustand and Redux', 'ONLINE',  '2026-08-25 15:00:00', 'https://meet.google.com/jkl-u-demo7', 'COMPLETED', 0, '2026-08-22 11:00:00', '2026-08-25 16:30:00'),
(8,  '2024BTECH002', '2026BTECH015', 4,  'Linear Regression and Gradient Descent',  'ONLINE',  '2026-09-10 17:00:00', 'https://meet.google.com/jkl-u-demo8', 'COMPLETED', 0, '2026-09-07 10:00:00', '2026-09-10 18:30:00'),
(9,  '2024BTECH002', '2024BDES001',  3,  'CSS Grid & Tailwind for Product Designers','ONLINE', '2026-09-18 16:00:00', 'https://meet.google.com/jkl-u-demo9', 'COMPLETED', 0, '2026-09-15 09:00:00', '2026-09-18 17:15:00'),

-- Mentor: Chirag Singhal (2024BTECH003) - 3 completed
(10, '2024BTECH003', '2025BTECH008', 4,  'Decision Trees and Random Forests',       'ONLINE',  '2025-11-05 17:00:00', 'https://meet.google.com/jkl-u-dem10', 'COMPLETED', 0, '2025-11-02 10:00:00', '2025-11-05 18:30:00'),
(11, '2024BTECH003', '2025BTECH011', 4,  'Neural Networks from Scratch in NumPy',   'ONLINE',  '2025-11-20 16:00:00', 'https://meet.google.com/jkl-u-dem11', 'COMPLETED', 0, '2025-11-17 14:00:00', '2025-11-20 17:30:00'),
(12, '2024BTECH003', '2026BTECH017', 1,  'Python Automation & Web Scraping',       'OFFLINE', '2026-09-12 11:00:00', NULL,                                  'COMPLETED', 0, '2026-09-09 16:00:00', '2026-09-12 12:30:00'),

-- Mentor: Divya Jain (2024BTECH004) - 2 completed
(13, '2024BTECH004', '2025BTECH012', 3,  'React Router and Dynamic Routing',        'ONLINE',  '2025-11-12 15:00:00', 'https://meet.google.com/jkl-u-dem13', 'COMPLETED', 0, '2025-11-09 11:00:00', '2025-11-12 16:30:00'),
(14, '2024BTECH004', '2026BTECH014', 15, 'Flutter Widget Lifecycle and Navigation','ONLINE',  '2026-09-15 14:00:00', 'https://meet.google.com/jkl-u-dem14', 'COMPLETED', 0, '2026-09-12 10:00:00', '2026-09-15 15:30:00'),

-- Mentor: Eshan Verma (2024BTECH005) - 1 completed
(15, '2024BTECH005', '2026BTECH015', 16, 'Interfacing Sensors with Arduino via I2C','OFFLINE','2026-09-22 15:00:00', NULL,                                  'COMPLETED', 0, '2026-09-18 10:00:00', '2026-09-22 16:30:00'),

-- Mentor: Gauri Khandelwal (2025BTECH007) - 2 completed
-- Note: Gauri was learner in session 1, and mentor in session 16 & 17! (Both mentor & learner in completed sessions)
(16, '2025BTECH007', '2026BTECH013', 1,  'Python String Manipulation & Regex',      'ONLINE',  '2026-09-20 18:00:00', 'https://meet.google.com/jkl-u-dem16', 'COMPLETED', 0, '2026-09-17 12:00:00', '2026-09-20 19:30:00'),
(17, '2025BTECH007', '2026BTECH016', 2,  'SQL Joins and Aggregation Deep Dive',     'ONLINE',  '2026-09-28 17:00:00', 'https://meet.google.com/jkl-u-dem17', 'COMPLETED', 0, '2026-09-25 15:00:00', '2026-09-28 18:30:00'),

-- Mentor: Harsh Vardhan (2025BTECH008) - 1 completed
(18, '2025BTECH008', '2026BTECH017', 4,  'Clustering with K-Means in Python',       'OFFLINE', '2026-10-02 14:00:00', NULL,                                  'COMPLETED', 0, '2026-09-29 11:00:00', '2026-10-02 15:30:00'),

-- Mentor: Isha Meena (2025BTECH009) - 1 completed
(19, '2025BTECH009', '2026BTECH014', 1,  'Working with JSON and APIs in Python',    'ONLINE',  '2026-10-05 16:00:00', 'https://meet.google.com/jkl-u-dem19', 'COMPLETED', 0, '2026-10-01 10:00:00', '2026-10-05 17:30:00'),

-- Mentor: Sneha Agarwal (2024BBA001) - 3 completed
(20, '2024BBA001',   '2025BBA004',   10, 'Corporate Financial Statement Analysis',  'OFFLINE', '2025-10-15 11:00:00', NULL,                                  'COMPLETED', 0, '2025-10-12 10:00:00', '2025-10-15 12:30:00'),
(21, '2024BBA001',   '2026BBA006',   10, 'Double-Entry Bookkeeping Principles',     'ONLINE',  '2026-09-14 15:00:00', 'https://meet.google.com/jkl-u-dem21', 'COMPLETED', 0, '2026-09-10 11:00:00', '2026-09-14 16:30:00'),
(22, '2024BBA001',   '2025BBA003',   12, 'Discounted Cash Flow (DCF) Modeling',     'ONLINE',  '2026-09-25 14:00:00', 'https://meet.google.com/jkl-u-dem22', 'COMPLETED', 0, '2026-09-21 16:00:00', '2026-09-25 15:30:00'),

-- Mentor: Tanmay Tiwari (2024BBA002) - 2 completed
(23, '2024BBA002',   '2025BBA005',   11, 'Performance Marketing and Meta Ads',      'ONLINE',  '2025-11-08 17:00:00', 'https://meet.google.com/jkl-u-dem23', 'COMPLETED', 0, '2025-11-05 10:00:00', '2025-11-08 18:30:00'),
(24, '2024BBA002',   '2026BBA007',   13, 'Debating and Public Speaking Framing',    'OFFLINE', '2026-09-16 16:00:00', NULL,                                  'COMPLETED', 0, '2026-09-12 12:00:00', '2026-09-16 17:30:00'),

-- Mentor: Bharat Bhushan (2024BDES001) - 3 completed
(25, '2024BDES001',  '2025BDES004',  6,  'Figma Auto-layout and Design Tokens',     'ONLINE',  '2025-10-18 16:00:00', 'https://meet.google.com/jkl-u-dem25', 'COMPLETED', 0, '2025-10-14 11:00:00', '2025-10-18 17:30:00'),
(26, '2024BDES001',  '2026BDES006',  7,  'Design Sprint: Empathy to Prototype',     'OFFLINE', '2026-09-11 14:00:00', NULL,                                  'COMPLETED', 0, '2026-09-08 09:00:00', '2026-09-11 15:30:00'),
(27, '2024BDES001',  '2025BDES003',  6,  'Interactive Micro-interactions in Figma', 'ONLINE',  '2026-09-29 18:00:00', 'https://meet.google.com/jkl-u-dem27', 'COMPLETED', 0, '2026-09-26 14:00:00', '2026-09-29 19:30:00'),

-- Mentor: Chhavi Soni (2024BDES002) - 2 completed
(28, '2024BDES002',  '2025BDES005',  8,  'SolidWorks Parametric Surface Modeling',  'OFFLINE', '2025-11-14 15:00:00', NULL,                                  'COMPLETED', 0, '2025-11-10 11:00:00', '2025-11-14 16:30:00'),
(29, '2024BDES002',  '2026BDES007',  9,  'Editorial Typography and Grid Systems',   'ONLINE',  '2026-09-24 16:00:00', 'https://meet.google.com/jkl-u-dem29', 'COMPLETED', 0, '2026-09-20 10:00:00', '2026-09-24 17:30:00'),

-- Mentor: Devvrat Rao (2025BDES003) - 1 completed
(30, '2025BDES003',  '2026BDES008',  6,  'Wireframing Mobile Flows from User Stories','ONLINE', '2026-10-08 17:00:00', 'https://meet.google.com/jkl-u-dem30', 'COMPLETED', 0, '2026-10-04 15:00:00', '2026-10-08 18:30:00'),

-- UPCOMING / ACCEPTED SESSIONS (status = 'ACCEPTED')
(31, '2024BTECH001', '2025BTECH011', 2,  'Advanced Query Optimization & EXPLAIN',   'ONLINE',  '2026-11-15 16:00:00', 'https://meet.google.com/jkl-u-fut31', 'ACCEPTED',  0, '2026-10-15 10:00:00', '2026-10-16 11:00:00'),
(32, '2024BTECH002', '2025BTECH012', 3,  'Next.js Server Side Rendering (SSR)',      'ONLINE',  '2026-11-18 18:00:00', 'https://meet.google.com/jkl-u-fut32', 'ACCEPTED',  0, '2026-10-18 14:00:00', '2026-10-19 09:30:00'),
(33, '2024BBA001',   '2026BBA008',   10, 'Reading Balance Sheets for Non-Finance',  'OFFLINE', '2026-11-20 15:00:00', NULL,                                  'ACCEPTED',  0, '2026-10-20 11:00:00', '2026-10-21 10:00:00'),

-- REQUESTED SESSIONS (status = 'REQUESTED')
(34, '2024BTECH003', '2026BTECH014', 4,  'Intro to Transformers & HuggingFace',     'ONLINE',  '2026-11-25 17:00:00', NULL,                                  'REQUESTED', 0, '2026-10-21 16:00:00', '2026-10-21 16:00:00'),
(35, '2024BDES001',  '2026BDES007',  7,  'User Journey Mapping for Hackathons',     'ONLINE',  '2026-11-28 15:00:00', NULL,                                  'REQUESTED', 0, '2026-10-22 09:00:00', '2026-10-22 09:00:00'),

-- REJECTED SESSIONS (status = 'REJECTED')
(36, '2024BTECH001', '2025BTECH010', 1,  'Deep Reinforcement Learning (Out of Scope)','ONLINE','2026-09-01 10:00:00', NULL,                                  'REJECTED',  0, '2026-08-28 11:00:00', '2026-08-29 12:00:00'),

-- CANCELLED SESSIONS (status = 'CANCELLED')
(37, '2024BTECH002', '2025BTECH008', 3,  'Redux Saga Implementation',               'ONLINE',  '2026-09-04 16:00:00', NULL,                                  'CANCELLED', 0, '2026-09-01 14:00:00', '2026-09-03 10:00:00');

-- ----------------------------------------------------------------------------
-- 8. REPUTATION HISTORY (Awarded to mentors upon session completion, +10 each)
-- ----------------------------------------------------------------------------
INSERT INTO reputation_history (history_id, roll_no, session_id, points, reason, created_at) VALUES
(1,  '2024BTECH001', 1,  10, 'Completed mentoring session: Advanced Python Generators & Decorators', '2025-09-10 17:30:00'),
(2,  '2024BTECH001', 2,  10, 'Completed mentoring session: Relational Normalization: 1NF to BCNF',   '2025-09-15 16:30:00'),
(3,  '2024BTECH001', 3,  10, 'Completed mentoring session: Python OOP Fundamentals',                '2026-08-20 18:00:00'),
(4,  '2024BTECH001', 4,  10, 'Completed mentoring session: Binary Search and Two Pointer Approach',  '2026-09-05 17:15:00'),
(5,  '2024BTECH002', 5,  10, 'Completed mentoring session: Building Component Systems in React',     '2025-10-02 19:30:00'),
(6,  '2024BTECH002', 6,  10, 'Completed mentoring session: Data Analysis with Pandas',              '2025-10-12 15:30:00'),
(7,  '2024BTECH002', 7,  10, 'Completed mentoring session: State Management with Zustand and Redux', '2026-08-25 16:30:00'),
(8,  '2024BTECH002', 8,  10, 'Completed mentoring session: Linear Regression and Gradient Descent',  '2026-09-10 18:30:00'),
(9,  '2024BTECH002', 9,  10, 'Completed mentoring session: CSS Grid & Tailwind for Product Designers','2026-09-18 17:15:00'),
(10, '2024BTECH003', 10, 10, 'Completed mentoring session: Decision Trees and Random Forests',       '2025-11-05 18:30:00'),
(11, '2024BTECH003', 11, 10, 'Completed mentoring session: Neural Networks from Scratch in NumPy',   '2025-11-20 17:30:00'),
(12, '2024BTECH003', 12, 10, 'Completed mentoring session: Python Automation & Web Scraping',       '2026-09-12 12:30:00'),
(13, '2024BTECH004', 13, 10, 'Completed mentoring session: React Router and Dynamic Routing',        '2025-11-12 16:30:00'),
(14, '2024BTECH004', 14, 10, 'Completed mentoring session: Flutter Widget Lifecycle and Navigation','2026-09-15 15:30:00'),
(15, '2024BTECH005', 15, 10, 'Completed mentoring session: Interfacing Sensors with Arduino via I2C','2026-09-22 16:30:00'),
(16, '2025BTECH007', 16, 10, 'Completed mentoring session: Python String Manipulation & Regex',      '2026-09-20 19:30:00'),
(17, '2025BTECH007', 17, 10, 'Completed mentoring session: SQL Joins and Aggregation Deep Dive',     '2026-09-28 18:30:00'),
(18, '2025BTECH008', 18, 10, 'Completed mentoring session: Clustering with K-Means in Python',       '2026-10-02 15:30:00'),
(19, '2025BTECH009', 19, 10, 'Completed mentoring session: Working with JSON and APIs in Python',    '2026-10-05 17:30:00'),
(20, '2024BBA001',   20, 10, 'Completed mentoring session: Corporate Financial Statement Analysis',  '2025-10-15 12:30:00'),
(21, '2024BBA001',   21, 10, 'Completed mentoring session: Double-Entry Bookkeeping Principles',     '2026-09-14 16:30:00'),
(22, '2024BBA001',   22, 10, 'Completed mentoring session: Discounted Cash Flow (DCF) Modeling',     '2026-09-25 15:30:00'),
(23, '2024BBA002',   23, 10, 'Completed mentoring session: Performance Marketing and Meta Ads',      '2025-11-08 18:30:00'),
(24, '2024BBA002',   24, 10, 'Completed mentoring session: Debating and Public Speaking Framing',    '2026-09-16 17:30:00'),
(25, '2024BDES001',  25, 10, 'Completed mentoring session: Figma Auto-layout and Design Tokens',     '2025-10-18 17:30:00'),
(26, '2024BDES001',  26, 10, 'Completed mentoring session: Design Sprint: Empathy to Prototype',     '2026-09-11 15:30:00'),
(27, '2024BDES001',  27, 10, 'Completed mentoring session: Interactive Micro-interactions in Figma', '2026-09-29 19:30:00'),
(28, '2024BDES002',  28, 10, 'Completed mentoring session: SolidWorks Parametric Surface Modeling',  '2025-11-14 16:30:00'),
(29, '2024BDES002',  29, 10, 'Completed mentoring session: Editorial Typography and Grid Systems',   '2026-09-24 17:30:00'),
(30, '2025BDES003',  30, 10, 'Completed mentoring session: Wireframing Mobile Flows from User Stories','2026-10-08 18:30:00');

-- ----------------------------------------------------------------------------
-- 9. REVIEWS (Rating 1 to 5, reviewer is participant reviewing the other)
-- ----------------------------------------------------------------------------
INSERT INTO review (session_id, roll_no, reviewee_roll_no, rating, comment, created_at) VALUES
-- Reviews on Aarav Sharma (Mentor)
(1, '2025BTECH007', '2024BTECH001', 5, 'Super clear explanations of Python closures and yield expressions. Highly recommended!', '2025-09-10 18:00:00'),
(2, '2025BTECH008', '2024BTECH001', 5, 'Helped me finally understand BCNF lossless decomposition. Great diagrams.',           '2025-09-15 17:00:00'),
(3, '2026BTECH013', '2024BTECH001', 4, 'Patient mentor, took time to explain dunder methods thoroughly.',                     '2026-08-20 18:30:00'),
(4, '2026BTECH014', '2024BTECH001', 5, 'Solved all binary search boundary condition doubts. Excellent mentor.',               '2026-09-05 18:00:00'),

-- Reviews on Bhavya Patel (Mentor)
(5, '2025BTECH009', '2024BTECH002', 5, 'Bhavya knows React inside out. Helped structure clean reusable components.',         '2025-10-02 20:00:00'),
(6, '2025BTECH010', '2024BTECH002', 4, 'Very practical hands-on examples with Pandas dataframes.',                           '2025-10-12 16:00:00'),
(7, '2026BTECH013', '2024BTECH002', 5, 'Brilliant session on Zustand vs Redux state flows.',                                  '2026-08-25 17:00:00'),
(8, '2026BTECH015', '2024BTECH002', 4, 'Clear math intuition behind gradient descent optimization.',                          '2026-09-10 19:00:00'),
-- Mutual review on session 5: Mentor Bhavya also reviewed Learner Isha!
(5, '2024BTECH002', '2025BTECH009', 5, 'Very quick learner with strong core JavaScript fundamentals.',                       '2025-10-02 20:15:00'),

-- Reviews on Chirag Singhal (Mentor)
(10, '2025BTECH008', '2024BTECH003', 5, 'Informative breakdown of Gini impurity vs Entropy in decision trees.',              '2025-11-05 19:00:00'),
(11, '2025BTECH011', '2024BTECH003', 4, 'Good walkthrough of forward and backprop matrix derivatives.',                       '2025-11-20 18:00:00'),

-- Reviews on Sneha Agarwal (Mentor)
(20, '2025BBA004',   '2024BBA001',   5, 'Demystified cash flows vs income statements. Best finance senior at JKLU.',          '2025-10-15 13:00:00'),
(21, '2026BBA006',   '2024BBA001',   5, 'Helped clear my financial accounting mid-term concepts!',                            '2026-09-14 17:00:00'),

-- Reviews on Bharat Bhushan (Mentor)
(25, '2025BDES004',  '2024BDES001',  5, 'Auto-layout masterclass. Clean Figma file hygiene.',                                  '2025-10-18 18:00:00'),
(26, '2026BDES006',  '2024BDES001',  4, 'Great insights on conducting real stakeholder user interviews.',                      '2026-09-11 16:00:00'),

-- Review on Gauri Khandelwal (Mentor)
(16, '2026BTECH013', '2025BTECH007', 4, 'Gauri was very helpful and shared practical regex cheatsheets.',                     '2026-09-20 20:00:00');

-- ----------------------------------------------------------------------------
-- 10. EXPERIENCES (Projects, Internships, Hackathons, Achievements)
-- ----------------------------------------------------------------------------
INSERT INTO experience (roll_no, exp_no, role_title, organization, exp_type, start_date, end_date, description, created_at) VALUES
('2024BTECH001', 1, 'Full Stack Engineering Intern', 'SecurePay Fintech', 'INTERNSHIP', '2025-05-15', '2025-07-30', 'Engineered Python microservices processing payment webhooks with 99.9% uptime.', '2025-08-01 10:00:00'),
('2024BTECH001', 2, 'Lead Backend Developer', 'JKLU Smart Campus Portal', 'PROJECT', '2024-10-01', '2025-04-15', 'Designed relational schemas and JWT authentication for university portal.', '2025-04-20 11:00:00'),
('2024BTECH001', 3, 'Smart India Hackathon Finalist', 'Ministry of Education', 'HACKATHON', '2024-09-15', '2024-09-17', 'Built an AI-driven farmer advisory portal using FastAPI and MySQL.', '2024-09-20 12:00:00'),

('2024BTECH002', 1, 'Frontend Development Intern', 'Zeta Cloud Labs', 'INTERNSHIP', '2025-06-01', '2025-07-31', 'Built responsive React dashboards using Tailwind CSS and Recharts.', '2025-08-05 10:00:00'),
('2024BTECH002', 2, 'Winner - HackJaipur 2024', 'JKLU Tech Club', 'HACKATHON', '2024-11-10', '2024-11-12', 'Secured 1st place building a peer-to-peer campus ride sharing app.', '2024-11-15 10:00:00'),

('2024BTECH003', 1, 'Computer Vision Researcher', 'JKLU AI Lab', 'PROJECT', '2025-01-10', NULL, 'Developing real-time classroom attendance system via face embeddings.', '2025-01-15 10:00:00'),

('2024BBA001',   1, 'Equity Research Analyst Intern', 'Prudent Wealth Advisors', 'INTERNSHIP', '2025-05-10', '2025-07-10', 'Constructed 3-statement financial models for renewable energy startups.', '2025-07-15 10:00:00'),
('2024BBA001',   2, 'Best Delegate - Harvard MUN Jaipur', 'HMUN India', 'ACHIEVEMENT', '2024-10-05', '2024-10-07', 'Represented Japan in the Economic and Financial Committee.', '2024-10-10 10:00:00'),

('2024BDES001',  1, 'UI/UX Design Intern', 'UrbanClap Design Studio', 'INTERNSHIP', '2025-05-01', '2025-07-15', 'Redesigned user checkout flow decreasing drop-offs by 18%.', '2025-07-20 10:00:00'),
('2024BDES001',  2, 'Campus Signage Redesign', 'JKLU Estates Office', 'PROJECT', '2024-11-01', '2025-03-30', 'Audited wayfinding typography and fabricated accessible directional signs.', '2025-04-05 10:00:00');
-- Note: Several students have NO experience entries (e.g. 2026BTECH013, 2026BTECH018) for query 17

-- ----------------------------------------------------------------------------
-- 11. LISTINGS (Marketplace: AVAILABLE, SOLD, REMOVED)
-- ----------------------------------------------------------------------------
INSERT INTO listing (listing_id, seller_roll_no, buyer_roll_no, title, description, status, price, category, item_condition, posted_date, sold_at) VALUES
-- Available Listings
(1, '2024BTECH001', NULL, 'Database System Concepts (Silberschatz, 7th Ed)', 'Hardcover textbook in mint condition. Highlight-free with all DBMS problem sets.', 'AVAILABLE', 450.00, 'Textbooks', 'LIKE_NEW', '2026-09-01 10:00:00', NULL),
(2, '2024BTECH002', NULL, 'Logitech MX Master 3S Wireless Mouse', 'Ergonomic mouse with silent clicks. Used for 4 months, comes with USB receiver.', 'AVAILABLE', 3200.00, 'Electronics', 'LIKE_NEW', '2026-09-05 11:00:00', NULL),
(3, '2024BTECH003', NULL, 'Arduino Mega 2560 R3 + Sensor Starter Kit', 'Includes breadboard, 30+ sensors, jumper wires and carrying case for IoT lab.', 'AVAILABLE', 850.00, 'Lab Equipment', 'GOOD', '2026-09-10 14:00:00', NULL),
(4, '2024BBA001',   NULL, 'Financial Management by Prasanna Chandra', 'Standard reference book for BBA corporate finance courses. Minimal notes.', 'AVAILABLE', 350.00, 'Textbooks', 'GOOD', '2026-09-15 16:00:00', NULL),
(5, '2024BDES001',  NULL, 'Wacom One Drawing Tablet 13.3 Inch', 'Digital drawing screen with pen and nibs. Ideal for digital illustration and design.', 'AVAILABLE', 12500.00, 'Electronics', 'LIKE_NEW', '2026-09-20 12:00:00', NULL),
(6, '2025BTECH007', NULL, 'Dorm Room Study Lamp with USB Charging Port', 'Adjustable LED desk lamp with 3 color temperatures. Perfect for hostel rooms.', 'AVAILABLE', 400.00, 'Hostel Essentials', 'GOOD', '2026-09-25 15:00:00', NULL),
(7, '2025BTECH008', NULL, 'Raspberry Pi 4 Model B (4GB RAM) with Case', 'Includes aluminum heatsink case, official power supply, and 32GB SD card.', 'AVAILABLE', 3800.00, 'Electronics', 'LIKE_NEW', '2026-10-01 10:00:00', NULL),

-- Sold Listings (buyer_roll_no and sold_at populated)
(8,  '2024BTECH001', '2025BTECH007', 'Engineering Mechanics by Beer & Johnston', 'Essential first year reference book. Sold to junior student.', 'SOLD', 300.00, 'Textbooks', 'GOOD', '2026-08-15 10:00:00', '2026-08-20 14:30:00'),
(9,  '2024BTECH002', '2026BTECH013', 'Casio FX-991EX Classwiz Scientific Calculator', 'High resolution scientific calculator approved for university semester exams.', 'SOLD', 750.00, 'Electronics', 'LIKE_NEW', '2026-08-18 11:00:00', '2026-08-22 16:00:00'),
(10, '2024BDES002',  '2026BDES006',  'A3 Drafting Table Board with Parallel Ruler', 'Portable drafting table for technical drawing and product rendering.', 'SOLD', 950.00, 'Lab Equipment', 'GOOD', '2026-08-20 12:00:00', '2026-08-26 15:45:00'),
(11, '2024BBA002',   '2025BBA003',   'Marketing Management by Philip Kotler (15th Ed)', 'Comprehensive marketing reference with case study annotations.', 'SOLD', 500.00, 'Textbooks', 'FAIR', '2026-08-25 10:00:00', '2026-08-30 11:20:00'),

-- Removed Listings (no longer available)
(12, '2025BTECH009', NULL, 'Cycle Lock with High Security Combination', 'Seller decided to keep item for personal use.', 'REMOVED', 150.00, 'Hostel Essentials', 'GOOD', '2026-09-02 10:00:00', NULL),
(13, '2025BDES003',  NULL, 'Acrylic Paint Set & Canvas Pack', 'Withdrawn by seller.', 'REMOVED', 600.00, 'Stationery', 'NEW', '2026-09-12 11:00:00', NULL);
