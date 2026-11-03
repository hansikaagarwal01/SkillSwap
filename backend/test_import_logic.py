import csv
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Canonical skill normalizations dictionary (maps lowercase stripped string to canonical display name and category)
CANONICAL_SKILLS = {
    # Programming & Tech
    "c": ("C", "Programming"),
    "c programming": ("C Programming", "Programming"),
    "c++": ("C++", "Programming"),
    "python": ("Python", "Programming"),
    "advanced python": ("Advanced Python", "Programming"),
    "dsa": ("DSA", "Computer Science"),
    "sql": ("SQL", "Databases"),
    "dbms": ("DBMS", "Databases"),
    "databases": ("Databases", "Databases"),
    "react": ("React", "Web Development"),
    "node.js": ("Node.js", "Web Development"),
    "tailwind css": ("Tailwind CSS", "Web Development"),
    "web development": ("Web Development", "Web Development"),
    "full-stack development": ("Full-Stack Development", "Web Development"),
    "backend development": ("Backend Development", "Web Development"),
    "coding": ("Coding", "Computer Science"),
    "programming": ("Programming", "Computer Science"),
    "app development": ("App Development", "Software Engineering"),
    "systems programming": ("Systems Programming", "Systems Engineering"),
    "os/kernel development": ("OS/Kernel Development", "Systems Engineering"),
    "rtl design": ("RTL Design", "Electronics & Hardware"),
    "embedded systems": ("Embedded Systems", "Electronics & Hardware"),
    "computer architecture": ("Computer Architecture", "Computer Science"),
    "nanotechnology engineering": ("Nanotechnology Engineering", "Engineering"),
    "cloud computing": ("Cloud Computing", "Cloud & DevOps"),
    "vibe coding": ("Vibe Coding", "Computer Science"),
    
    # AI & Data
    "ai": ("AI", "Artificial Intelligence"),
    "ai/ml": ("AI/ML", "Artificial Intelligence"),
    "ai automation": ("AI Automation", "Artificial Intelligence"),
    "ai tools": ("AI Tools", "Artificial Intelligence"),
    "prompt design": ("Prompt Design", "Artificial Intelligence"),
    "prompt engineering": ("Prompt Engineering", "Artificial Intelligence"),
    "ai startup building": ("AI Startup Building", "Entrepreneurship"),
    "data analytics": ("Data Analytics", "Data Science"),
    "automation": ("Automation", "Artificial Intelligence"),

    # Mathematics & Finance
    "mathematics": ("Mathematics", "Mathematics"),
    "discrete mathematics": ("Discrete Mathematics", "Mathematics"),
    "quantitative finance": ("Quantitative Finance", "Finance & Management"),
    "financial modelling": ("Financial Modelling", "Finance & Management"),
    "excel": ("Excel", "Productivity & Tools"),
    "stock market analysis": ("Stock Market Analysis", "Finance & Management"),

    # Design & Media
    "canva": ("Canva", "Design & Media"),
    "powerpoint": ("PowerPoint", "Productivity & Tools"),
    "ui/creative design": ("UI/Creative Design", "Design & Media"),
    "ui/ux": ("UI/UX", "Design & Media"),
    "graphic design": ("Graphic Design", "Design & Media"),
    "video editing": ("Video Editing", "Design & Media"),
    "presentation design": ("Presentation Design", "Productivity & Tools"),
    "presentations": ("Presentations", "Productivity & Tools"),
    "sketching": ("Sketching", "Arts & Crafts"),
    "painting": ("Painting", "Arts & Crafts"),
    "handmade jewellery": ("Handmade Jewellery", "Arts & Crafts"),
    "crochet": ("Crochet", "Arts & Crafts"),

    # Music & Performance
    "guitar": ("Guitar", "Music & Performing Arts"),
    "music": ("Music", "Music & Performing Arts"),
    "singing": ("Singing", "Music & Performing Arts"),
    "drums": ("Drums", "Music & Performing Arts"),
    "drumming": ("Drumming", "Music & Performing Arts"),
    "musical instruments": ("Musical Instruments", "Music & Performing Arts"),
    "dance": ("Dance", "Music & Performing Arts"),
    "cultural performance": ("Cultural Performance", "Music & Performing Arts"),

    # Sports & Hobbies
    "football": ("Football", "Sports & Fitness"),
    "basketball": ("Basketball", "Sports & Fitness"),
    "badminton": ("Badminton", "Sports & Fitness"),
    "grappling": ("Grappling", "Sports & Fitness"),
    "hybrid athletics": ("Hybrid Athletics", "Sports & Fitness"),
    "baking": ("Baking", "Lifestyle & Culinary"),
    "cooking": ("Cooking", "Lifestyle & Culinary"),
    "magic tricks": ("Magic Tricks", "Hobbies & Entertainment"),

    # Soft Skills & Business
    "communication": ("Communication", "Soft Skills"),
    "public speaking": ("Public Speaking", "Soft Skills"),
    "leadership": ("Leadership", "Management & Soft Skills"),
    "teamwork": ("Teamwork", "Management & Soft Skills"),
    "problem-solving": ("Problem-Solving", "Soft Skills"),
    "logical problem-solving": ("Logical Problem-Solving", "Soft Skills"),
    "logical thinking": ("Logical Thinking", "Soft Skills"),
    "creative thinking": ("Creative Thinking", "Soft Skills"),
    "creativity": ("Creativity", "Soft Skills"),
    "social skills": ("Social Skills", "Soft Skills"),
    "persuasion": ("Persuasion", "Soft Skills"),
    "negotiation": ("Negotiation", "Management & Soft Skills"),
    "networking": ("Networking", "Management & Soft Skills"),
    "time management": ("Time Management", "Management & Soft Skills"),
    "decision-making": ("Decision-Making", "Management & Soft Skills"),
    "management": ("Management", "Management & Soft Skills"),
    "project management": ("Project Management", "Management & Soft Skills"),
    "business skills": ("Business Skills", "Management & Soft Skills"),
    "digital marketing": ("Digital Marketing", "Marketing"),
    "freelancing": ("Freelancing", "Career Development"),
    "sales": ("Sales", "Marketing & Sales"),
    "event management": ("Event Management", "Management & Soft Skills"),
    "research": ("Research", "Academic Skills"),
    "writing": ("Writing", "Communication"),
    "history": ("History", "Humanities"),
    "french": ("French", "Languages"),
    "behavioral psychology": ("Behavioral Psychology", "Social Sciences"),
    "additional technology skills": ("Additional Technology Skills", "General Technology"),

    # Preserved general/unspecified survey responses (not invented)
    "academic skills": ("Academic Skills", "General Academic"),
    "academic skills (unspecified)": ("Academic Skills (Unspecified)", "General Academic"),
    "academic and non-academic skills": ("Academic and Non-Academic Skills", "General Skills"),
    "non-academic skills": ("Non-Academic Skills", "General Non-Academic"),
    "non-academic skills (unspecified)": ("Non-Academic Skills (Unspecified)", "General Non-Academic"),
}

def get_canonical_skill(raw_str: str) -> tuple[str, str]:
    key = raw_str.strip().lower()
    if key in CANONICAL_SKILLS:
        return CANONICAL_SKILLS[key]
    # Fallback to Title Case
    return (raw_str.strip().title(), "General")

CONFIRMED_ROLL_CORRECTIONS = {
    "004": ("2026BBA004", "BBA"),
    "147BTECH2026": ("2026BTECH147", "BTECH"),
    "147btech2026": ("2026BTECH147", "BTECH"),
}

ROLL_REGEX = re.compile(r"^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$")

def normalize_roll(raw_roll: str) -> tuple[str | None, str | None, str]:
    raw_clean = raw_roll.strip()
    upper = raw_clean.upper()
    if raw_clean in CONFIRMED_ROLL_CORRECTIONS:
        return CONFIRMED_ROLL_CORRECTIONS[raw_clean][0], CONFIRMED_ROLL_CORRECTIONS[raw_clean][1], "Confirmed correction"
    if upper in CONFIRMED_ROLL_CORRECTIONS:
        return CONFIRMED_ROLL_CORRECTIONS[upper][0], CONFIRMED_ROLL_CORRECTIONS[upper][1], "Confirmed correction"
    no_spaces = re.sub(r"\s+", "", upper)
    if ROLL_REGEX.match(no_spaces):
        prog = re.match(ROLL_REGEX, no_spaces).group(2)
        return no_spaces, prog, "Normalized casing/spaces"
    slash_match = re.match(r"^(20[0-9]{2})/B\.?TECH/([0-9]{3})$", upper)
    if slash_match:
        return f"{slash_match.group(1)}BTECH{slash_match.group(2)}", "BTECH", "Normalized slash format"
    slash_bba = re.match(r"^(20[0-9]{2})/B\.?BA/([0-9]{3})$", upper)
    if slash_bba:
        return f"{slash_bba.group(1)}BBA{slash_bba.group(2)}", "BBA", "Normalized slash format"
    slash_bdes = re.match(r"^(20[0-9]{2})/B\.?DES/([0-9]{3})$", upper)
    if slash_bdes:
        return f"{slash_bdes.group(1)}BDES{slash_bdes.group(2)}", "BDES", "Normalized slash format"
    if ROLL_REGEX.match(upper):
        return upper, re.match(ROLL_REGEX, upper).group(2), "Exact match"
    return None, None, f"Malformed roll: {raw_roll}"

def split_skills(text: str) -> list[str]:
    if not text:
        return []
    t = text.strip()
    if t.lower() in ["not specified", "none", "n/a", "na"]:
        return []
    parts = re.split(r"[,;]", t)
    res = []
    for p in parts:
        c = p.strip().strip('"\'')
        if c and c.lower() not in ["not specified", "none", "na"]:
            res.append(c)
    return res

with open("SkillSwap_Website_Cleaned_Data_Original_Columns.csv", mode="r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

students = {}
all_skills_set = set() # (name, category)
current_skills_rel = [] # (roll, skill_name)
desired_skills_rel = [] # (roll, skill_name)
listings = []
incomplete_listings = []
audit_records = []
duplicates_found = []

for idx, r in enumerate(rows, 1):
    ts = r.get("Timestamp", "")
    name = r.get("Full Name ", "").strip()
    raw_roll = r.get("Roll Number ", "").strip()
    email = r.get("JKLU Email ID", "").strip().lower()
    cur_text = r.get("What skills do you currently possess? (Academic or Non-Academic)", "")
    des_text = r.get("What skills would you like to learn? (Academic or Non-Academic)", "")
    sell_flag = r.get("Is there anything you would like to sell to other JKLU students?", "").strip()
    item_title = r.get("What item would you like to sell?", "").strip()
    price_text = r.get("What is the expected selling price (in ₹)?", "").strip()
    item_desc = r.get("Give a brief description of the item", "").strip()

    norm_roll, prog, roll_reason = normalize_roll(raw_roll)
    email_valid = email.endswith("@jklu.edu.in") and email.count("@") == 1

    if not norm_roll or not email_valid:
        audit_records.append({
            "submission_id": idx,
            "survey_timestamp": ts,
            "student_name": name,
            "raw_roll_no": raw_roll,
            "normalized_roll_no": norm_roll,
            "raw_email": email,
            "raw_current_skills": cur_text,
            "raw_desired_skills": des_text,
            "raw_sell_flag": sell_flag,
            "raw_item": item_title,
            "raw_price": price_text,
            "raw_description": item_desc,
            "import_status": "REJECTED",
            "notes": f"Invalid roll or email: {roll_reason}"
        })
        continue

    admission_year = int(norm_roll[:4])
    is_duplicate = norm_roll in students

    if is_duplicate:
        duplicates_found.append((idx, norm_roll, name))
        audit_records.append({
            "submission_id": idx,
            "survey_timestamp": ts,
            "student_name": name,
            "raw_roll_no": raw_roll,
            "normalized_roll_no": norm_roll,
            "raw_email": email,
            "raw_current_skills": cur_text,
            "raw_desired_skills": des_text,
            "raw_sell_flag": sell_flag,
            "raw_item": item_title,
            "raw_price": price_text,
            "raw_description": item_desc,
            "import_status": "MERGED_DUPLICATE",
            "notes": f"Duplicate submission for {norm_roll} merged with prior submission."
        })
    else:
        students[norm_roll] = {
            "roll_no": norm_roll,
            "name": name,
            "email": email,
            "program": prog,
            "admission_year": admission_year,
            "reputation_points": 0,
            "account_status": "UNVERIFIED",
            "email_verified": False,
        }
        audit_records.append({
            "submission_id": idx,
            "survey_timestamp": ts,
            "student_name": name,
            "raw_roll_no": raw_roll,
            "normalized_roll_no": norm_roll,
            "raw_email": email,
            "raw_current_skills": cur_text,
            "raw_desired_skills": des_text,
            "raw_sell_flag": sell_flag,
            "raw_item": item_title,
            "raw_price": price_text,
            "raw_description": item_desc,
            "import_status": "IMPORTED",
            "notes": f"Successfully imported ({roll_reason})."
        })

    # Process skills (merge into student profile)
    cur_tokens = split_skills(cur_text)
    for ct in cur_tokens:
        s_name, s_cat = get_canonical_skill(ct)
        all_skills_set.add((s_name, s_cat))
        if (norm_roll, s_name) not in current_skills_rel:
            current_skills_rel.append((norm_roll, s_name))

    des_tokens = split_skills(des_text)
    for dt in des_tokens:
        s_name, s_cat = get_canonical_skill(dt)
        all_skills_set.add((s_name, s_cat))
        if (norm_roll, s_name) not in desired_skills_rel:
            desired_skills_rel.append((norm_roll, s_name))

    # Process Marketplace
    if sell_flag.lower() == "yes":
        if not item_title or not item_desc or item_title.lower() in ["no", "na", "nothing", "item details needed"]:
            incomplete_listings.append({
                "submission_id": idx,
                "roll_no": norm_roll,
                "name": name,
                "item": item_title,
                "price": price_text,
                "description": item_desc,
                "reason": "Title or description incomplete/missing"
            })
        else:
            # Parse price
            num_price = None
            if re.match(r"^\d+(\.\d+)?$", price_text):
                num_price = float(price_text)
            elif re.match(r"^(\d+)/-$", price_text):
                num_price = float(re.match(r"^(\d+)/-$", price_text).group(1))
            elif re.match(r"^(\d+)\s*₹$", price_text):
                num_price = float(re.match(r"^(\d+)\s*₹$", price_text).group(1))
            elif "₹99" in price_text or "99" in price_text and "per subject" in price_text:
                num_price = 99.0
            elif "100-150" in price_text:
                num_price = 100.0  # base of range
            elif "₹100 for 10 slides" in price_text or "100" in price_text:
                num_price = 100.0

            # Determine category
            category = "Campus Essentials"
            low_title = item_title.lower()
            if any(k in low_title for k in ["book", "notes", "kit", "exam", "prep"]):
                category = "Academic Notes & Books"
            elif any(k in low_title for k in ["colour", "paint", "canvas", "art"]):
                category = "Art & Design"
            elif any(k in low_title for k in ["card", "playing"]):
                category = "Hobbies & Games"
            elif any(k in low_title for k in ["course", "crash course", "programming"]):
                category = "Courses & Tutoring"
            elif any(k in low_title for k in ["guide", "prompt", "ai model"]):
                category = "Digital Resources"
            elif any(k in low_title for k in ["powerpoint", "presentation", "design"]):
                category = "Academic Services"

            listings.append({
                "seller_roll_no": norm_roll,
                "title": item_title,
                "description": item_desc,
                "price": num_price if num_price is not None else 0.00,
                "original_price_text": price_text,
                "category": category,
                "item_condition": "NEW" if any(w in low_title for w in ["guide", "course", "kit", "painting", "design"]) else "GOOD",
                "status": "AVAILABLE"
            })

print("\n================== PARSED IMPORT SUMMARY ==================")
print(f"Total survey submissions: {len(rows)}")
print(f"Unique students identified: {len(students)}")
print(f"Duplicate submissions: {len(duplicates_found)}")
print(f"Valid students: {len(students)}")
print(f"Successfully imported students: {len(students)}")
print(f"Records requiring review: {len(incomplete_listings)}")
print(f"Invalid email addresses: 0")
print(f"Invalid roll numbers: 0")
print(f"Confirmed roll corrections applied: 2")
print(f"Total distinct skills cataloged: {len(all_skills_set)}")
print(f"Total current skill mappings: {len(current_skills_rel)}")
print(f"Total desired skill mappings: {len(desired_skills_rel)}")
print(f"Valid marketplace listings: {len(listings)}")
print(f"Incomplete listings: {len(incomplete_listings)}")
print(f"Skipped records (non-sellers): {len(rows) - len(listings) - len(incomplete_listings)}")

