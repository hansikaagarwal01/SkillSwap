import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(host="127.0.0.1", port=3306, user="skillswap", password="skillswap_pass", database="skillswap")

out = []
out.append("-- ============================================================================")
out.append("-- SkillSwap JKLU - Authentic Survey Seed Data")
out.append("-- Source of Truth: Real Survey Responses (36 Submissions -> 34 Unique Students)")
out.append("-- Zero Fabricated Students, Zero Fake Reviews, Zero Fake Sessions")
out.append("-- ============================================================================\n")
out.append("SET FOREIGN_KEY_CHECKS = 0;")
out.append("TRUNCATE TABLE survey_import_audit;")
out.append("TRUNCATE TABLE student_desired_skill;")
out.append("TRUNCATE TABLE review;")
out.append("TRUNCATE TABLE learning_session;")
out.append("TRUNCATE TABLE listing;")
out.append("TRUNCATE TABLE experience;")
out.append("TRUNCATE TABLE student_skill;")
out.append("TRUNCATE TABLE skill;")
out.append("TRUNCATE TABLE student;")
out.append("SET FOREIGN_KEY_CHECKS = 1;\n")

with conn.cursor() as cur:
    # 1. Students
    out.append("-- ----------------------------------------------------------------------------")
    out.append("-- 1. STUDENTS (34 Authentic Survey Students)")
    out.append("-- ----------------------------------------------------------------------------")
    cur.execute("SELECT roll_no, name, email, phone, program, admission_year, reputation_points, password_hash, account_status, email_verified FROM student ORDER BY roll_no ASC;")
    st_rows = cur.fetchall()
    out.append("INSERT INTO student (roll_no, name, email, phone, program, admission_year, reputation_points, password_hash, account_status, email_verified) VALUES")
    st_vals = []
    for r in st_rows:
        phone_val = f"'{r[3]}'" if r[3] else "NULL"
        pwd_val = f"'{r[7]}'" if r[7] else "NULL"
        ev_val = "TRUE" if r[9] else "FALSE"
        # escape name
        clean_name = r[1].replace("'", "''")
        st_vals.append(f"('{r[0]}', '{clean_name}', '{r[2]}', {phone_val}, '{r[4]}', {r[5]}, {r[6]}, {pwd_val}, '{r[8]}', {ev_val})")
    out.append(",\n".join(st_vals) + ";\n")

    # 2. Skills
    out.append("-- ----------------------------------------------------------------------------")
    out.append("-- 2. SKILLS (102 Canonical Normalized Skills from Real Survey)")
    out.append("-- ----------------------------------------------------------------------------")
    cur.execute("SELECT skill_id, name, category, description FROM skill ORDER BY skill_id ASC;")
    sk_rows = cur.fetchall()
    out.append("INSERT INTO skill (skill_id, name, category, description) VALUES")
    sk_vals = []
    for r in sk_rows:
        name_esc = r[1].replace("'", "''")
        cat_esc = r[2].replace("'", "''")
        desc_esc = f"'{r[3].replace('\'', '\'\'')}'" if r[3] else "NULL"
        sk_vals.append(f"({r[0]}, '{name_esc}', '{cat_esc}', {desc_esc})")
    out.append(",\n".join(sk_vals) + ";\n")

    # 3. Student Skills (Current)
    out.append("-- ----------------------------------------------------------------------------")
    out.append("-- 3. STUDENT_SKILL (89 Current Skills Possessed by Students)")
    out.append("-- ----------------------------------------------------------------------------")
    cur.execute("SELECT roll_no, skill_id, proficiency_level, can_teach FROM student_skill ORDER BY roll_no ASC, skill_id ASC;")
    ss_rows = cur.fetchall()
    out.append("INSERT INTO student_skill (roll_no, skill_id, proficiency_level, can_teach) VALUES")
    ss_vals = []
    for r in ss_rows:
        ct_val = "TRUE" if r[3] else "FALSE"
        ss_vals.append(f"('{r[0]}', {r[1]}, '{r[2]}', {ct_val})")
    out.append(",\n".join(ss_vals) + ";\n")

    # 4. Student Desired Skills
    out.append("-- ----------------------------------------------------------------------------")
    out.append("-- 4. STUDENT_DESIRED_SKILL (83 Skills Students Desire to Learn)")
    out.append("-- ----------------------------------------------------------------------------")
    cur.execute("SELECT roll_no, skill_id FROM student_desired_skill ORDER BY roll_no ASC, skill_id ASC;")
    sd_rows = cur.fetchall()
    out.append("INSERT INTO student_desired_skill (roll_no, skill_id) VALUES")
    sd_vals = []
    for r in sd_rows:
        sd_vals.append(f"('{r[0]}', {r[1]})")
    out.append(",\n".join(sd_vals) + ";\n")

    # 5. Listings
    out.append("-- ----------------------------------------------------------------------------")
    out.append("-- 5. LISTINGS (9 Authentic Campus Marketplace Items from Real Survey)")
    out.append("-- ----------------------------------------------------------------------------")
    cur.execute("SELECT listing_id, seller_roll_no, buyer_roll_no, title, description, status, price, original_price_text, category, item_condition FROM listing ORDER BY listing_id ASC;")
    ls_rows = cur.fetchall()
    out.append("INSERT INTO listing (listing_id, seller_roll_no, buyer_roll_no, title, description, status, price, original_price_text, category, item_condition) VALUES")
    ls_vals = []
    for r in ls_rows:
        buyer_val = f"'{r[2]}'" if r[2] else "NULL"
        title_esc = r[3].replace("'", "''")
        desc_esc = r[4].replace("'", "''")
        opt_esc = f"'{r[7].replace('\'', '\'\'')}'" if r[7] else "NULL"
        ls_vals.append(f"({r[0]}, '{r[1]}', {buyer_val}, '{title_esc}', '{desc_esc}', '{r[5]}', {r[6]}, {opt_esc}, '{r[8]}', '{r[9]}')")
    out.append(",\n".join(ls_vals) + ";\n")

    # 6. Audit Trail
    out.append("-- ----------------------------------------------------------------------------")
    out.append("-- 6. SURVEY_IMPORT_AUDIT (Full Provenance for All 36 Survey Submissions)")
    out.append("-- ----------------------------------------------------------------------------")
    cur.execute("SELECT submission_id, survey_timestamp, student_name, raw_roll_no, normalized_roll_no, raw_email, raw_current_skills, raw_desired_skills, raw_sell_flag, raw_item, raw_price, raw_description, import_status, notes FROM survey_import_audit ORDER BY submission_id ASC;")
    aud_rows = cur.fetchall()
    out.append("INSERT INTO survey_import_audit (submission_id, survey_timestamp, student_name, raw_roll_no, normalized_roll_no, raw_email, raw_current_skills, raw_desired_skills, raw_sell_flag, raw_item, raw_price, raw_description, import_status, notes) VALUES")
    aud_vals = []
    for r in aud_rows:
        norm_r = f"'{r[4]}'" if r[4] else "NULL"
        rcs = f"'{r[6].replace('\'', '\'\'')}'" if r[6] else "NULL"
        rds = f"'{r[7].replace('\'', '\'\'')}'" if r[7] else "NULL"
        rsf = f"'{r[8]}'" if r[8] else "NULL"
        rit = f"'{r[9].replace('\'', '\'\'')}'" if r[9] else "NULL"
        rp = f"'{r[10].replace('\'', '\'\'')}'" if r[10] else "NULL"
        rd = f"'{r[11].replace('\'', '\'\'')}'" if r[11] else "NULL"
        notes = f"'{r[13].replace('\'', '\'\'')}'" if r[13] else "NULL"
        aud_vals.append(f"({r[0]}, '{r[1]}', '{r[2].replace('\'', '\'\'')}', '{r[3]}', {norm_r}, '{r[5]}', {rcs}, {rds}, {rsf}, {rit}, {rp}, {rd}, '{r[12]}', {notes})")
    out.append(",\n".join(aud_vals) + ";\n")

conn.close()

seed_file = "backend/database/seed.sql"
with open(seed_file, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Generated clean real survey seed file at {seed_file}")

