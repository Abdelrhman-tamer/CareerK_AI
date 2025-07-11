import csv
import json
import re

# File paths
CSV_PATH = "D:\\careerk-ai-recommendation\\pldb.csv"
OUTPUT_PATH = "./skills-dataset/kaggle_skills.json"

# ✅ Filter function to reject bad entries
def is_valid_skill(skill):
    skill = skill.strip().lower()

    if not skill or len(skill) < 2:
        return False
    if skill in {"a", "b", "c", "i"}:
        return False
    if skill.isdigit():
        return False
    if re.fullmatch(r"[^\w]+", skill):  # only symbols like "++", "--"
        return False
    if not re.search(r"[a-z]", skill):  # must contain at least one letter
        return False
    if len(skill) == 2 and not skill.isalpha():
        return False  # e.g., "c#"
    if re.fullmatch(r"[a-z]", skill):
        return False  # reject one-letter entries

    return True

# ✅ Extraction logic
unique_skills = set()

with open(CSV_PATH, mode="r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    print("📌 Available columns:", reader.fieldnames)

    for row in reader:
        title = row.get("title", "").strip()
        if is_valid_skill(title):
            unique_skills.add(title.lower())

# ✅ Sort and save
cleaned_skills = sorted(unique_skills)

with open(OUTPUT_PATH, mode="w", encoding="utf-8") as jsonfile:
    json.dump(cleaned_skills, jsonfile, indent=2, ensure_ascii=False)

print(f"✅ Extracted {len(cleaned_skills)} clean skills to {OUTPUT_PATH}")









# import csv
# import json
# import re

# CSV_PATH = "D:\\careerk-ai-recommendation\\pldb.csv"
# OUTPUT_PATH = "./skills-dataset/kaggle_skills.json"

# def is_valid_skill(skill):
#     if len(skill) < 2:
#         return False
#     if skill.isdigit():
#         return False
#     if re.match(r"^[^\w]+$", skill):  # only symbols/punctuation
#         return False
#     if not re.search(r"[a-zA-Z]", skill):  # must contain letters
#         return False
#     return True

# unique_skills = set()

# with open(CSV_PATH, mode="r", encoding="utf-8") as csvfile:
#     reader = csv.DictReader(csvfile)
#     print("📌 Available columns:", reader.fieldnames)

#     for row in reader:
#         title = row.get("title", "").strip().lower()
#         if is_valid_skill(title):
#             unique_skills.add(title)

# # Sort alphabetically and save
# cleaned_skills = sorted(list(unique_skills))

# with open(OUTPUT_PATH, mode="w", encoding="utf-8") as jsonfile:
#     json.dump(cleaned_skills, jsonfile, indent=2, ensure_ascii=False)

# print(f"✅ Extracted {len(cleaned_skills)} clean skills to {OUTPUT_PATH}")







