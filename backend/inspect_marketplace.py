import csv
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("SkillSwap_Website_Cleaned_Data_Original_Columns.csv", mode="r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("=== MARKETPLACE SURVEY RESPONSES ===")
for idx, r in enumerate(rows, 1):
    sell = r.get("Is there anything you would like to sell to other JKLU students?", "").strip()
    item = r.get("What item would you like to sell?", "").strip()
    price = r.get("What is the expected selling price (in ₹)?", "").strip()
    desc = r.get("Give a brief description of the item", "").strip()
    name = r.get("Full Name ", "").strip()
    roll = r.get("Roll Number ", "").strip()

    if sell.lower() == "yes" or item or price or desc:
        print(f"\nRow #{idx}: Name: {name} | Roll: {roll} | Sell: {sell!r}")
        print(f"  Item: {item!r}")
        print(f"  Price: {price!r}")
        print(f"  Description: {desc!r}")

