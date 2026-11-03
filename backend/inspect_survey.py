import csv
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

ROLL_REGEX = re.compile(r"^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$")

CONFIRMED_ROLL_CORRECTIONS = {
    "004": ("2026BBA004", "BBA"),
    "147BTECH2026": ("2026BTECH147", "BTECH"),
    "147btech2026": ("2026BTECH147", "BTECH"),
}

def normalize_roll(raw_roll: str) -> tuple[str | None, str | None, str]:
    raw_clean = raw_roll.strip()
    upper = raw_clean.upper()
    
    # 1. Check confirmed corrections
    if raw_clean in CONFIRMED_ROLL_CORRECTIONS:
        corr_roll, corr_prog = CONFIRMED_ROLL_CORRECTIONS[raw_clean]
        return corr_roll, corr_prog, "Confirmed correction"
    if upper in CONFIRMED_ROLL_CORRECTIONS:
        corr_roll, corr_prog = CONFIRMED_ROLL_CORRECTIONS[upper]
        return corr_roll, corr_prog, "Confirmed correction"

    # 2. Check known unambiguous normalizations
    # e.g., '2026 BBA 050' -> '2026BBA050'
    no_spaces = re.sub(r"\s+", "", upper)
    if ROLL_REGEX.match(no_spaces):
        prog = re.match(ROLL_REGEX, no_spaces).group(2)
        return no_spaces, prog, "Normalized casing/spaces"

    # e.g., '2026/B.Tech/275' -> '2026BTECH275', '2026/b.tech/286' -> '2026BTECH286'
    slash_match = re.match(r"^(20[0-9]{2})/B\.?TECH/([0-9]{3})$", upper)
    if slash_match:
        norm = f"{slash_match.group(1)}BTECH{slash_match.group(2)}"
        return norm, "BTECH", "Normalized slash format"

    slash_bba = re.match(r"^(20[0-9]{2})/B\.?BA/([0-9]{3})$", upper)
    if slash_bba:
        norm = f"{slash_bba.group(1)}BBA{slash_bba.group(2)}"
        return norm, "BBA", "Normalized slash format"

    slash_bdes = re.match(r"^(20[0-9]{2})/B\.?DES/([0-9]{3})$", upper)
    if slash_bdes:
        norm = f"{slash_bdes.group(1)}BDES{slash_bdes.group(2)}"
        return norm, "BDES", "Normalized slash format"

    # If already matches
    if ROLL_REGEX.match(upper):
        prog = re.match(ROLL_REGEX, upper).group(2)
        return upper, prog, "Exact match"

    return None, None, f"Malformed roll number: {raw_roll}"

def validate_email(email: str) -> bool:
    clean = email.strip().lower()
    return clean.endswith("@jklu.edu.in") and not clean.endswith(".evil.com") and clean.count("@") == 1

def parse_price(raw_price: str) -> tuple[float | None, str]:
    if not raw_price:
        return None, ""
    p_str = raw_price.strip()
    # Check simple integers or decimals
    # e.g. "150" -> 150.0
    # "99/-" -> 99.0
    # "29₹" -> 29.0
    # "₹99 per subject" -> 99.0 (with original note)
    # "100-150" -> None or 100.0? "retain as a range; do not choose an arbitrary amount" -> numeric None, or flag
    # "₹100 for 10 slides." -> retain pricing basis
    if re.match(r"^\d+(\.\d+)?$", p_str):
        return float(p_str), p_str
    
    clean_slash = re.match(r"^(\d+)/-$", p_str)
    if clean_slash:
        return float(clean_slash.group(1)), p_str
    
    clean_rupee_suffix = re.match(r"^(\d+)\s*₹$", p_str)
    if clean_rupee_suffix:
        return float(clean_rupee_suffix.group(1)), p_str

    clean_rupee_prefix = re.match(r"^₹\s*(\d+)$", p_str)
    if clean_rupee_prefix:
        return float(clean_rupee_prefix.group(1)), p_str

    return None, p_str

with open("SkillSwap_Website_Cleaned_Data_Original_Columns.csv", mode="r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Total survey submissions: {len(rows)}")

students_by_roll = {}
students_by_email = {}
duplicates = []
invalid_rolls = []
invalid_emails = []

for idx, r in enumerate(rows, 1):
    raw_roll = r.get("Roll Number ", "")
    raw_email = r.get("JKLU Email ID", "")
    name = r.get("Full Name ", "").strip()
    
    norm_roll, prog, roll_status = normalize_roll(raw_roll)
    is_email_valid = validate_email(raw_email)
    norm_email = raw_email.strip().lower()

    if not norm_roll:
        invalid_rolls.append((idx, name, raw_roll, roll_status))
    if not is_email_valid:
        invalid_emails.append((idx, name, raw_email))

    key = norm_roll if norm_roll else f"RAW:{raw_roll}"
    if key in students_by_roll:
        duplicates.append((idx, key, name, norm_email))
    else:
        students_by_roll[key] = []
    students_by_roll[key].append((idx, r, norm_roll, prog, norm_email))

print(f"\nUnique roll number keys identified: {len(students_by_roll)}")
print(f"Duplicate submissions count: {len(duplicates)}")
for dup in duplicates:
    print(f"  Duplicate row #{dup[0]}: Roll {dup[1]} | Name: {dup[2]} | Email: {dup[3]}")

print(f"\nInvalid roll numbers: {len(invalid_rolls)}")
for ir in invalid_rolls:
    print(f"  Row #{ir[0]}: Name {ir[1]} | Roll: {ir[2]!r} | Reason: {ir[3]}")

print(f"\nInvalid emails: {len(invalid_emails)}")
for ie in invalid_emails:
    print(f"  Row #{ie[0]}: Name {ie[1]} | Email: {ie[2]!r}")

