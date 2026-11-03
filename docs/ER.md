# Entity-Relationship (ER) Model — SkillSwap JKLU

```mermaid
erDiagram
    STUDENT ||--o{ STUDENT_SKILL : "possesses"
    SKILL ||--o{ STUDENT_SKILL : "categorized_by"

    STUDENT ||--o{ STUDENT_DESIRED_SKILL : "desires_to_learn"
    SKILL ||--o{ STUDENT_DESIRED_SKILL : "needed_in"
    
    STUDENT ||--o{ LEARNING_SESSION : "mentors (mentor_roll_no)"
    STUDENT ||--o{ LEARNING_SESSION : "learns (learner_roll_no)"
    SKILL ||--o{ LEARNING_SESSION : "taught_in"

    LEARNING_SESSION ||--o{ REVIEW : "evaluated_in"
    STUDENT ||--o{ REVIEW : "writes (reviewer)"
    STUDENT ||--o{ REVIEW : "receives (reviewee)"

    STUDENT ||--o{ EXPERIENCE : "documents"
    STUDENT ||--o{ LISTING : "sells"
    STUDENT ||--o{ LISTING : "buys"

    STUDENT {
        string roll_no PK "regex ^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$"
        string name
        string email UK "@jklu.edu.in"
        string phone
        enum program "BTECH, BBA, BDES"
        smallint admission_year
        int reputation_points ">= 0"
        string password_hash "Nullable until claimed"
        enum account_status "UNVERIFIED, PENDING_APPROVAL, ACTIVE, SUSPENDED"
        boolean email_verified
        datetime last_login_at
        int token_version
        string verification_token_hash UK "SHA-256"
        datetime verification_token_expires_at
        datetime created_at
        datetime updated_at
    }

    SKILL {
        int skill_id PK
        string name UK
        string category
        text description
        datetime created_at
    }

    STUDENT_SKILL {
        string roll_no PK, FK
        int skill_id PK, FK
        enum proficiency_level "BEGINNER, INTERMEDIATE, ADVANCED, EXPERT"
        boolean can_teach
        datetime created_at
    }

    STUDENT_DESIRED_SKILL {
        string roll_no PK, FK
        int skill_id PK, FK
        datetime created_at
    }

    LEARNING_SESSION {
        int session_id PK
        string mentor_roll_no FK
        string learner_roll_no FK
        int skill_id FK
        string topic
        enum mode "ONLINE, OFFLINE"
        datetime scheduled_at
        string meeting_link
        enum status "REQUESTED, ACCEPTED, REJECTED, CANCELLED, COMPLETED"
        int credit_cost "Must be 0"
        int points_awarded "10 on completion"
        boolean reputation_awarded
        datetime reputation_awarded_at
        datetime created_at
        datetime updated_at
    }

    REVIEW {
        int session_id PK, FK
        string roll_no PK, FK "Reviewer"
        string reviewee_roll_no FK "Target"
        smallint rating "1 to 5"
        text comment
        datetime created_at
    }

    EXPERIENCE {
        string roll_no PK, FK
        int exp_no PK
        string role_title
        string organization
        enum exp_type "INTERNSHIP, PROJECT, HACKATHON, ACHIEVEMENT, OTHER"
        date start_date
        date end_date
        text description
        datetime created_at
    }

    LISTING {
        int listing_id PK
        string seller_roll_no FK
        string buyer_roll_no FK
        string title
        text description
        enum status "AVAILABLE, SOLD, REMOVED"
        decimal price ">= 0"
        string original_price_text "Survey submitted price"
        string category
        enum item_condition "NEW, LIKE_NEW, GOOD, FAIR"
        datetime posted_date
        datetime sold_at
    }

    SURVEY_IMPORT_AUDIT {
        int audit_id PK
        datetime submission_timestamp
        string raw_name
        string raw_roll_number
        string normalized_roll_no
        string raw_email
        text raw_current_skills
        text raw_desired_skills
        string raw_marketplace_item
        string raw_price
        text raw_item_description
        enum import_status "IMPORTED, MERGED, REVIEW_REQUIRED"
        text error_notes
        datetime created_at
    }
```
