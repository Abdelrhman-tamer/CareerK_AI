import logging
import re
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util, CrossEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from skill_extractor import extract_skills_from_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recommender")

bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-6")
tfidf_vectorizer = TfidfVectorizer(max_features=5000)

ALPHA = 0.7
SKILL_WEIGHT = 0.2
TITLE_WEIGHT = 2
DESC_WEIGHT = 1
SKILLS_WEIGHT = 3
RERANK_TOP_N = 10


def build_developer_profile(dev: Dict) -> str:
    if dev.get("cv_text"):
        return dev["cv_text"]

    parts = [
        dev.get("brief_bio", ""),
        f"Skills: {', '.join(dev['skills'])}" if dev.get("skills") else "",
        f"{dev['years_of_experience']} years of experience" if dev.get("years_of_experience") else "",
        f"Previously worked as: {dev['previous_job']}" if dev.get("previous_job") else "",
        f"Level: {dev['track_level']}" if dev.get("track_level") else "",
    ]
    return " ".join(filter(None, parts))


def build_post_text(post: Dict, type_: str) -> str:
    title = post.get("title", "")
    description = post.get("description", post.get("job_description", ""))
    skills = post.get("skills", []) if type_ == "job" else post.get("required_skills", [])
    skills = skills or []

    parts = []
    parts.extend([title] * TITLE_WEIGHT)
    parts.extend([description] * DESC_WEIGHT)
    parts.extend(skill for skill in skills for _ in range(SKILLS_WEIGHT))

    return " ".join(parts)


def preprocess(text: str) -> str:
    text = text.lower()
    return re.sub(r"[^a-zA-Z\s]", "", text)


def compute_scores(dev_text: str, job_posts: List[Dict], service_posts: List[Dict]):
    dev_processed = preprocess(dev_text)
    dev_skills = extract_skills_from_text(dev_text)
    logger.info(f"Extracted developer skills: {dev_skills}")

    job_texts = [build_post_text(post, "job") for post in job_posts]
    service_texts = [build_post_text(post, "service") for post in service_posts]

    tfidf_vectorizer.fit([dev_processed] + job_texts + service_texts)
    dev_tfidf = tfidf_vectorizer.transform([dev_processed])
    job_tfidfs = tfidf_vectorizer.transform(job_texts)
    service_tfidfs = tfidf_vectorizer.transform(service_texts)

    dev_embedding = bi_encoder.encode(dev_text, convert_to_tensor=True)
    job_embeddings = bi_encoder.encode(job_texts, convert_to_tensor=True)
    service_embeddings = bi_encoder.encode(service_texts, convert_to_tensor=True)

    job_scores = []
    for i, post in enumerate(job_posts):
        sem_score = float(util.cos_sim(dev_embedding, job_embeddings[i])[0])
        kw_score = (dev_tfidf @ job_tfidfs[i].T).data
        kw_score = float(kw_score[0]) if kw_score.size > 0 else 0.0
        skills = post.get("skills", []) or []
        skill_score = len(set(dev_skills) & set(skills)) / len(skills) if skills else 0
        total = ALPHA * sem_score + (1 - ALPHA) * kw_score + SKILL_WEIGHT * skill_score
        job_scores.append({"id": post["id"], "score": round(total, 4)})

    service_scores = []
    for i, post in enumerate(service_posts):
        sem_score = float(util.cos_sim(dev_embedding, service_embeddings[i])[0])
        kw_score = (dev_tfidf @ service_tfidfs[i].T).data
        kw_score = float(kw_score[0]) if kw_score.size > 0 else 0.0
        skills = post.get("required_skills", []) or []
        skill_score = len(set(dev_skills) & set(skills)) / len(skills) if skills else 0
        total = ALPHA * sem_score + (1 - ALPHA) * kw_score + SKILL_WEIGHT * skill_score
        service_scores.append({"id": post["id"], "score": round(total, 4)})

    job_scores.sort(key=lambda x: x["score"], reverse=True)
    service_scores.sort(key=lambda x: x["score"], reverse=True)

    return job_scores, service_scores


def rerank(dev_text: str, posts: List[Dict], post_texts: List[str], scores: List[Dict]):
    top = scores[:RERANK_TOP_N]
    top_ids = [x["id"] for x in top]
    top_indices = [i for i, p in enumerate(posts) if p["id"] in top_ids]
    pairs = [(dev_text, post_texts[i]) for i in top_indices]
    rerank_scores = cross_encoder.predict(pairs)

    updated = []
    for i, idx in enumerate(top_indices):
        original = scores[idx]["score"]
        new_score = 0.7 * original + 0.3 * rerank_scores[i]
        updated.append({"id": posts[idx]["id"], "score": round(new_score, 4)})

    return sorted(updated, key=lambda x: x["score"], reverse=True)


def recommend_for_developer(developer: Dict, job_posts: List[Dict], service_posts: List[Dict], rerank_enabled=True):
    logger.info("🔍 Starting recommendation...")

    dev_text = build_developer_profile(developer)
    job_scores, service_scores = compute_scores(dev_text, job_posts, service_posts)

    if rerank_enabled:
        job_scores = rerank(dev_text, job_posts, [build_post_text(p, "job") for p in job_posts], job_scores)
        service_scores = rerank(dev_text, service_posts, [build_post_text(p, "service") for p in service_posts], service_scores)

    logger.info("✅ Recommendation finished.")
    return {
        "job_recommendations": job_scores,
        "service_recommendations": service_scores
    }



# import logging
# import re
# import numpy as np
# from typing import List, Dict
# from sentence_transformers import SentenceTransformer, util, CrossEncoder
# from sklearn.feature_extraction.text import TfidfVectorizer
# from skill_extractor import extract_skills_from_text  # ✅ External NER-based skill extractor

# # Setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("recommender")

# # Load models
# bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
# cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-6")
# tfidf_vectorizer = TfidfVectorizer(max_features=5000)

# # Constants
# ALPHA = 0.7
# SKILL_WEIGHT = 0.2
# TITLE_WEIGHT = 2
# DESC_WEIGHT = 1
# SKILLS_WEIGHT = 3
# RERANK_TOP_N = 10
# MIN_SIMILARITY = 0.3
# MIN_SKILL_MATCH = 0.2


# def build_developer_profile(dev: Dict) -> str:
#     # Use generated CV if it exists, fallback to uploaded CV
#     if dev.get("generated_cv_text"):
#         return dev["generated_cv_text"]
#     elif dev.get("uploaded_cv_text"):
#         return dev["uploaded_cv_text"]

#     # Otherwise, build from fields
#     parts = [
#         dev.get("brief_bio", ""),
#         f"Skills: {', '.join(dev['skills'])}" if dev.get("skills") else "",
#         f"{dev['years_of_experience']} years of experience" if dev.get("years_of_experience") else "",
#         f"Previously worked as: {dev['previous_job']}" if dev.get("previous_job") else "",
#         f"Level: {dev['track_level']}" if dev.get("track_level") else "",
#     ]
#     return " ".join(filter(None, parts))


# def build_post_text(post: Dict, type_: str) -> str:
#     title = post.get("title", "")
#     description = post.get("description", "")
    
#     # Get skills safely
#     if type_ == "job":
#         skills = post.get("skills", [])
#     elif type_ == "service":
#         skills = post.get("required_skills", [])
#     else:
#         skills = []

#     # Ensure it's a list, not None
#     if skills is None:
#         skills = []

#     parts = []
#     parts.extend([title] * TITLE_WEIGHT)
#     parts.extend([description] * DESC_WEIGHT)
#     parts.extend(skill for skill in skills for _ in range(SKILLS_WEIGHT))

#     return " ".join(parts)


# def preprocess(text: str) -> str:
#     text = text.lower()
#     return re.sub(r"[^a-zA-Z\s]", "", text)


# def compute_scores(dev_text: str, job_posts: List[Dict], service_posts: List[Dict]):
#     dev_processed = preprocess(dev_text)
#     dev_skills = extract_skills_from_text(dev_text)
#     logger.info(f"Extracted developer skills: {dev_skills}")

#     # Build text data
#     job_texts = [build_post_text(post, "job") for post in job_posts]
#     service_texts = [build_post_text(post, "service") for post in service_posts]

#     # TF-IDF scores
#     tfidf_vectorizer.fit([dev_processed] + job_texts + service_texts)
#     dev_tfidf = tfidf_vectorizer.transform([dev_processed])
#     job_tfidfs = tfidf_vectorizer.transform(job_texts)
#     service_tfidfs = tfidf_vectorizer.transform(service_texts)

#     # Semantic similarity
#     dev_embedding = bi_encoder.encode(dev_text, convert_to_tensor=True)
#     job_embeddings = bi_encoder.encode(job_texts, convert_to_tensor=True)
#     service_embeddings = bi_encoder.encode(service_texts, convert_to_tensor=True)

#     job_scores = []
#     for i, post in enumerate(job_posts):
#         sem_score = float(util.cos_sim(dev_embedding, job_embeddings[i])[0])
#         kw_score = (dev_tfidf @ job_tfidfs[i].T).data
#         kw_score = float(kw_score[0]) if kw_score.size > 0 else 0.0
#         skills = post.get("skills", []) or []
#         skill_score = len(set(dev_skills) & set(skills)) / len(skills) if skills else 0
#         total = ALPHA * sem_score + (1 - ALPHA) * kw_score + SKILL_WEIGHT * skill_score
#         job_scores.append({ "id": post["id"], "score": round(total, 4) })

#     service_scores = []
#     for i, post in enumerate(service_posts):
#         sem_score = float(util.cos_sim(dev_embedding, service_embeddings[i])[0])
#         kw_score = (dev_tfidf @ service_tfidfs[i].T).data
#         kw_score = float(kw_score[0]) if kw_score.size > 0 else 0.0
#         skills = post.get("required_skills", []) or []
#         skill_score = len(set(dev_skills) & set(skills)) / len(skills) if skills else 0
#         total = ALPHA * sem_score + (1 - ALPHA) * kw_score + SKILL_WEIGHT * skill_score
#         service_scores.append({ "id": post["id"], "score": round(total, 4) })

#     job_scores.sort(key=lambda x: x["score"], reverse=True)
#     service_scores.sort(key=lambda x: x["score"], reverse=True)

#     return job_scores, service_scores


# def rerank(dev_text: str, posts: List[Dict], post_texts: List[str], scores: List[Dict]):
#     top = scores[:RERANK_TOP_N]
#     top_ids = [x["id"] for x in top]
#     top_indices = [i for i, p in enumerate(posts) if p["id"] in top_ids]
#     pairs = [(dev_text, post_texts[i]) for i in top_indices]
#     rerank_scores = cross_encoder.predict(pairs)

#     updated = []
#     for i, idx in enumerate(top_indices):
#         original = scores[idx]["score"]
#         new_score = 0.7 * original + 0.3 * rerank_scores[i]
#         updated.append({ "id": posts[idx]["id"], "score": round(new_score, 4) })

#     return sorted(updated, key=lambda x: x["score"], reverse=True)


# def recommend_for_developer(developer: Dict, job_posts: List[Dict], service_posts: List[Dict], rerank_enabled=True):
#     logger.info("🔍 Starting recommendation...")

#     dev_text = build_developer_profile(developer)
#     job_scores, service_scores = compute_scores(dev_text, job_posts, service_posts)

#     if rerank_enabled:
#         job_scores = rerank(dev_text, job_posts, [build_post_text(p, "job") for p in job_posts], job_scores)
#         service_scores = rerank(dev_text, service_posts, [build_post_text(p, "service") for p in service_posts], service_scores)

#     logger.info("✅ Recommendation finished.")
#     return {
#         "job_recommendations": job_scores,
#         "service_recommendations": service_scores
#     }









