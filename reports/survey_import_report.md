# SkillSwap JKLU — Survey Data Import & Audit Report

**Execution Timestamp:** 2026-11-03 21:24:59
**Data Source File:** `SkillSwap_Website_Cleaned_Data_Original_Columns.csv`

## 1. Executive Summary & Import Metrics

| Metric | Real Value | Description |
|---|---|---|
| **Total Survey Submissions** | `36` | Total records submitted in college survey |
| **Unique Students Identified** | `34` | Distinct JKLU students by normalized roll number & email |
| **Duplicate Submissions** | `2` | Verified duplicate submissions merged |
| **Valid Students Imported** | `34` | 100% valid roll number and @jklu.edu.in email domain |
| **Successfully Imported Students** | `34` | Imported into `student` table with `UNVERIFIED` status |
| **Records Requiring Review** | `1` | Incomplete marketplace submission flagged in CSV |
| **Invalid Email Addresses** | `0` | All emails strictly `@jklu.edu.in` |
| **Invalid Roll Numbers** | `0` | All roll numbers validated against required regex |
| **Confirmed Roll Corrections** | `2` | `004` -> `2026BBA004` & `147btech2026` -> `2026BTECH147` |
| **Distinct Skills Cataloged** | `102` | Normalized and categorized in `skill` relation |
| **Current Skill Mappings** | `89` | In `student_skill` (`can_teach=FALSE`, `proficiency='BEGINNER'`) |
| **Desired Skill Mappings** | `83` | Stored in dedicated `student_desired_skill` relation |
| **Valid Marketplace Listings** | `9` | Authentic student listings with original price text |
| **Incomplete Listings** | `1` | Flagged for manual review, unpublished |
| **Skipped Non-Seller Records** | `26` | Students who marked 'No' for selling items |

## 2. Confirmed Roll-Number Corrections

| Original Value | Correct Roll_No | Program | Student Name | Reason |
|---|---|---|---|---|
| `004` | `2026BBA004` | BBA | Agam jain | Verified student identity from survey cohort |
| `147btech2026` | `2026BTECH147` | BTECH | Harshit Adhikari | Inverted cohort format normalized |

## 3. Duplicate Submissions & Identity Merging

The survey contained 2 duplicate submissions from respondents submitting twice:

1. **Dhruv Tyagi (`2025BTECH023`)**
   - **Submission #4 (20:45:34):** Entered non-academic skills (unspecified).
   - **Submission #8 (20:54:17):** Entered specific skills: `Baking`, `Guitar`, desired `Communication`.
   - **Resolution:** Merged into single student profile `2025BTECH023` with specific skills. Both entries preserved in `survey_import_audit`.

2. **Dhanyashree Sen (`2025BTECH022`)**
   - **Submission #2 (20:32:21):** Entered skill `Writing`.
   - **Submission #36 (21:53:52):** Entered `Not specified`.
   - **Resolution:** Merged into single student profile `2025BTECH022` preserving `Writing`. Both entries preserved in `survey_import_audit`.

## 4. Records Requiring Manual Review

| Submission ID | Roll No | Student Name | Submitted Item | Price | Description | Review Note |
|---|---|---|---|---|---|---|
| 18 | `2026BBA050` | HIRANAND NAINWANI | `` | `99/-` | `` | Missing item title or description |

*Exported to `reports/records_requiring_manual_review.csv`.*

## 5. Valid Marketplace Listings Created

| ID | Seller Roll | Item Title | Category | Price (₹) | Original Submitted Text | Condition |
|---|---|---|---|---|---|---|
| 1 | `2025BTECH017` | Stainless steel water bottle | Campus Essentials | ₹150.00 | `150` | GOOD |
| 2 | `2025BTECH025` | Pack of playing cards | Hobbies & Games | ₹200.00 | `200` | GOOD |
| 3 | `2025BTECH035` | Reference book / semester notes | Books & Notes | ₹100.00 | `100` | GOOD |
| 4 | `2025BTECH027` | Acrylic colours | Art & Design | ₹120.00 | `120` | GOOD |
| 5 | `2025BTECH105` | Exam Prep Kit – notes, important questions, PYQs and solutions | Books & Notes | ₹99.00 | `₹99 per subject` | NEW |
| 6 | `2025BTECH116` | Programming First Principles Crash Course | Courses & Tutoring | ₹11999.00 | `11999` | NEW |
| 7 | `2026BTECH286` | Small canvas paintings | Art & Design | ₹100.00 | `100-150` | NEW |
| 8 | `2026BBA079` | AI model training guide and ready-made prompts | Digital Resources | ₹29.00 | `29₹` | NEW |
| 9 | `2026BTECH147` | PowerPoint presentation design | Academic Services | ₹100.00 | `₹100 for 10 slides.` | NEW |

## 6. Program-wise Student Distribution

| Program | Student Count | Percentage |
|---|---|---|
| **BBA** | 6 | 17.6% |
| **BTECH** | 28 | 82.4% |
