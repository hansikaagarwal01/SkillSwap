import csv
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("SkillSwap_Website_Cleaned_Data_Original_Columns.csv", mode="r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

def clean_skill_string(s: str) -> list[str]:
    if not s:
        return []
    s = s.strip()
    if s.lower() in ["not specified", "none", "n/a", "na"]:
        return []
    
    # Check if vague
    # Split on comma or semicolon
    raw_tokens = re.split(r"[,;]", s)
    tokens = []
    for t in raw_tokens:
        cleaned = t.strip()
        # remove quotes if any
        cleaned = cleaned.strip('"\'')
        if cleaned and cleaned.lower() not in ["not specified", "none", "na"]:
            tokens.append(cleaned)
    return tokens

current_skills_map = {} # roll -> set of skills
desired_skills_map = {} # roll -> set of skills
all_current_skills = set()
all_desired_skills = set()

for idx, r in enumerate(rows, 1):
    raw_roll = r.get("Roll Number ", "").strip()
    cur_text = r.get("What skills do you currently possess? (Academic or Non-Academic)", "")
    des_text = r.get("What skills would you like to learn? (Academic or Non-Academic)", "")

    c_skills = clean_skill_string(cur_text)
    d_skills = clean_skill_string(des_text)

    print(f"Row #{idx:2d} | Roll: {raw_roll:15s} | Cur: {c_skills} | Des: {d_skills}")
    for cs in c_skills:
        all_current_skills.add(cs)
    for ds in d_skills:
        all_desired_skills.add(ds)

print("\n=== SUMMARY OF UNIQUE SKILL STRINGS ===")
print(f"Total distinct current skill strings: {len(all_current_skills)}")
for cs in sorted(all_current_skills):
    print(f"  - {cs}")

print(f"\nTotal distinct desired skill strings: {len(all_desired_skills)}")
for ds in sorted(all_desired_skills):
    print(f"  - {ds}")

