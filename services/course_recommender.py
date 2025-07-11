import asyncpg
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def format_duration(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}h {mins}min"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}min"

async def get_course_recommendations(developer_id: str):
    conn = await asyncpg.connect(
        user="postgres", password="CareerK132@", database="CareerK", host="localhost"
    )

    try:
        # 1. Get developer profile
        dev_row = await conn.fetchrow("""
            SELECT skills, interested_courses, current_track, track_level, brief_bio
            FROM developers WHERE id = $1
        """, developer_id)

        if not dev_row:
            raise ValueError("Developer not found.")

        skills = dev_row["skills"] or []
        interests = dev_row["interested_courses"] or []
        dev_keywords = skills + interests
        dev_text = " ".join(dev_keywords).strip()

        if not dev_text:
            fallback_keywords = [
                dev_row["current_track"] or "",
                dev_row["track_level"] or "",
                dev_row["brief_bio"] or ""
            ]
            dev_text = " ".join(fallback_keywords).strip()

        if not dev_text:
            return []

        dev_embedding = model.encode(dev_text, convert_to_tensor=True)

        # 2. Load courses with lesson/rating/duration info
        course_rows = await conn.fetch("""
            SELECT
                c.id,
                c.name,
                c.description,
                c.image_url,
                c.track_id,
                COALESCE(SUM(CASE WHEN cc.type = 'video' THEN cc.video_time_minutes ELSE 0 END), 0) AS total_video_minutes,
                COUNT(cc.*) FILTER (WHERE cc.type IN ('video', 'quiz')) AS total_lessons,
                ROUND(AVG(cr.rating)::numeric, 1) AS average_rating
            FROM courses c
            LEFT JOIN course_contents cc ON c.id = cc.course_id
            LEFT JOIN course_reviews cr ON c.id = cr.course_id
            WHERE c.name IS NOT NULL AND c.description IS NOT NULL
            GROUP BY c.id
        """)

        recommendations = []

        for row in course_rows:
            course_text = f"{row['name']} {row['description']}"
            course_embedding = model.encode(course_text, convert_to_tensor=True)
            similarity = util.cos_sim(dev_embedding, course_embedding).item()

            # BOOST: Match with developer keywords
            keyword_match = 0
            for kw in dev_keywords:
                if kw.lower() in course_text.lower():
                    keyword_match += 1

            keyword_boost = min(keyword_match * 0.02, 0.1)  # Max +0.1
            score = similarity + keyword_boost

            if score >= 0.15:  # ✅ Loosened threshold
                recommendations.append({
                    "course_id": str(row["id"]),
                    "name": row["name"],
                    "image_url": row["image_url"],
                    "track_id": str(row["track_id"]) if row["track_id"] else None,
                    "duration": format_duration(row["total_video_minutes"]),
                    "rating": float(row["average_rating"]) if row["average_rating"] is not None else None,
                    "total_lessons": row["total_lessons"],
                    "score": round(score, 4)
                })

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:20]  # ✅ Up to 20 top matches

    finally:
        await conn.close()




# import asyncpg
# from sentence_transformers import SentenceTransformer, util

# model = SentenceTransformer('all-MiniLM-L6-v2')

# def format_duration(minutes):
#     hours = minutes // 60
#     mins = minutes % 60
#     if hours > 0 and mins > 0:
#         return f"{hours}h {mins}min"
#     elif hours > 0:
#         return f"{hours}h"
#     else:
#         return f"{mins}min"

# async def get_course_recommendations(developer_id: str):
#     conn = await asyncpg.connect(
#         user="postgres", password="CareerK132@", database="CareerK", host="localhost"
#     )

#     try:
#         # 1. Get developer info
#         dev_row = await conn.fetchrow("""
#             SELECT skills, interested_courses, current_track, track_level, brief_bio
#             FROM developers WHERE id = $1
#         """, developer_id)

#         if not dev_row:
#             raise ValueError("Developer not found.")

#         skills = dev_row["skills"] or []
#         interests = dev_row["interested_courses"] or []
#         dev_keywords = skills + interests
#         dev_text = " ".join(dev_keywords).strip()

#         if not dev_text:
#             fallback_keywords = [
#                 dev_row["current_track"] or "",
#                 dev_row["track_level"] or "",
#                 dev_row["brief_bio"] or ""
#             ]
#             dev_text = " ".join(fallback_keywords).strip()

#         if not dev_text:
#             return []

#         dev_embedding = model.encode(dev_text, convert_to_tensor=True)

#         # 2. Fetch course info with duration, lessons, and rating calculated
#         course_rows = await conn.fetch("""
#             SELECT
#                 c.id,
#                 c.name,
#                 c.description,
#                 c.image_url,
#                 c.track_id,
#                 COALESCE(SUM(CASE WHEN cc.type = 'video' THEN cc.video_time_minutes ELSE 0 END), 0) AS total_video_minutes,
#                 COUNT(cc.*) FILTER (WHERE cc.type IN ('video', 'quiz')) AS total_lessons,
#                 ROUND(AVG(cr.rating)::numeric, 1) AS average_rating
#             FROM courses c
#             LEFT JOIN course_contents cc ON c.id = cc.course_id
#             LEFT JOIN course_reviews cr ON c.id = cr.course_id
#             WHERE c.name IS NOT NULL AND c.description IS NOT NULL
#             GROUP BY c.id
#         """)

#         recommendations = []

#         for row in course_rows:
#             course_text = f"{row['name']} {row['description']}"
#             course_embedding = model.encode(course_text, convert_to_tensor=True)
#             similarity = util.cos_sim(dev_embedding, course_embedding).item()

#             if similarity >= 0.3:
#                 recommendations.append({
#                     "course_id": str(row["id"]),
#                     "name": row["name"],
#                     "image_url": row["image_url"],
#                     "track_id": str(row["track_id"]) if row["track_id"] else None,
#                     "duration": format_duration(row["total_video_minutes"]),
#                     "rating": float(row["average_rating"]) if row["average_rating"] is not None else None,
#                     "total_lessons": row["total_lessons"],
#                     "score": round(similarity, 4)
#                 })

#         recommendations.sort(key=lambda x: x["score"], reverse=True)
#         return recommendations[:10]

#     finally:
#         await conn.close()




