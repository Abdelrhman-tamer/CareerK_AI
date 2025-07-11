import spacy
from spacy.matcher import PhraseMatcher
import json
import re

nlp = spacy.load("en_core_web_sm")

def normalize(skill):
    return re.sub(r"[^\w\s]", "", skill.lower().strip())

with open("./skills-dataset/kaggle_skills.json", encoding="utf-8") as f:
    raw_skills = json.load(f)

normalized_skills = list(set(normalize(skill) for skill in raw_skills if len(skill) > 1))
patterns = [nlp.make_doc(skill) for skill in normalized_skills]
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add("SKILLS", patterns)

def extract_skills_from_text(text):
    doc = nlp(normalize(text))
    matches = matcher(doc)
    extracted = [doc[start:end].text.lower() for _, start, end in matches]
    return sorted(set(s for s in extracted if len(s) > 2 and not re.fullmatch(r"[a-z]", s)))




# import spacy
# from spacy.matcher import PhraseMatcher
# import json
# import re

# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")

# # Load and normalize skills
# def normalize(skill):
#     return re.sub(r"[^\w\s]", "", skill.lower().strip())

# with open("./skills-dataset/kaggle_skills.json", encoding="utf-8") as f:
#     raw_skills = json.load(f)

# # Create unique normalized skill set
# normalized_skills = list(set(normalize(skill) for skill in raw_skills if len(skill) > 1))

# # Create matcher patterns
# patterns = [nlp.make_doc(skill) for skill in normalized_skills]
# matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
# matcher.add("SKILLS", patterns)

# # Main extractor
# def extract_skills_from_text(text):
#     doc = nlp(normalize(text))
#     matches = matcher(doc)
#     extracted = [doc[start:end].text.lower() for _, start, end in matches]
#     return sorted(set(s for s in extracted if len(s) > 2 and not re.fullmatch(r"[a-z]", s)))
#     return sorted(list(set(doc[start:end].text.lower() for _, start, end in matches)))
