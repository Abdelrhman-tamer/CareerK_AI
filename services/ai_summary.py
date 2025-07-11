import google.generativeai as genai
import os
import re

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def clean_summary(summary: str) -> str:
    # Remove known placeholders or bracketed notes
    summary = re.sub(r"\[.*?\]", "", summary)
    summary = re.sub(r"\bX%|\bXYZ\b", "", summary)

    # Remove orphaned "by ." and similar broken phrases
    summary = re.sub(r"\bby\s*\.\b", "", summary)
    summary = re.sub(r"\bby\.\b", "", summary)
    summary = re.sub(r"\bby\s+\b", "", summary)

    # Replace broken "Delivered projects." with a valid default
    summary = re.sub(r"\bDelivered\s*projects\b\.?", "Delivered successful projects.", summary)

    # Collapse repeated bullets or whitespace
    summary = re.sub(r"[•]{2,}", "•", summary)
    summary = re.sub(r"\s{2,}", " ", summary)
    summary = summary.replace("•", " • ").replace("  ", " ")

    # Trim any trailing/leading unwanted characters
    return summary.strip()


def generate_professional_summary(cv_data: dict) -> str:
    try:
        education = cv_data.get("education", [])
        experience = cv_data.get("experience", [])
        skills = cv_data.get("skillsets", [])
        projects = cv_data.get("projects", [])
        certifications = cv_data.get("certifications", [])

        # Build content summaries
        edu_str = (
            f"{education[0]['degree']} in {education[0].get('field', '')} at {education[0]['institution']}"
            if education else ""
        )
        exp_str = ", ".join(f"{e['position']} at {e['company']}" for e in experience)
        skills_str = ", ".join(skills)
        proj_str = ", ".join(p["title"] for p in projects)
        cert_str = ", ".join(c["name"] for c in certifications)

        # Optional: aggregate achievements and results
        achievements = " | ".join(
            a for e in experience for a in e.get("achievements", [])
        )
        results = " | ".join(
            r for p in projects for r in p.get("results", [])
        )

        # Gemini prompt
        prompt = f"""
        Write a professional resume summary using the following:
        - Education: {edu_str}
        - Experience: {exp_str}
        - Skills: {skills_str}
        - Projects: {proj_str}
        - Project Results: {results}
        - Achievements: {achievements}
        - Certifications: {cert_str}

        Guidelines:
        - Limit to 4–5 lines
        - Start with a strong title (e.g., "Results-driven Software Engineer")
        - Focus on measurable accomplishments and technologies
        - Use full sentences in a formal tone
        - Avoid placeholder values like "X%", "[quantifiable achievement]", or "XYZ"
        - If data is not available, skip that part entirely
        
        - Do NOT make up fictional experience, degrees, or company names.
        - Only use the data provided.
        - If sections like experience or education are missing, just focus on skills and tone.
        """

        response = model.generate_content(prompt)
        summary = "".join(part.text for part in response.parts).strip()
        return clean_summary(summary)

    except Exception as e:
        print("AI Summary generation failed:", str(e))
        return "Experienced professional with a strong technical background and a track record of delivering results in team-driven environments."









# import google.generativeai as genai
# import os
# import re

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-1.5-flash-latest")


# def clean_summary(summary: str) -> str:
#     # Remove known placeholders or brackets
#     summary = re.sub(r"\[.*?\]", "", summary)
#     summary = re.sub(r"\bX%|\bXYZ\b", "", summary)
#     return summary.strip()


# def generate_professional_summary(cv_data: dict) -> str:
#     try:
#         education = cv_data.get("education", [])
#         experience = cv_data.get("experience", [])
#         skills = cv_data.get("skillsets", [])
#         projects = cv_data.get("projects", [])
#         certifications = cv_data.get("certifications", [])

#         # Build content summaries
#         edu_str = (
#             f"{education[0]['degree']} in {education[0].get('field', '')} at {education[0]['institution']}"
#             if education else ""
#         )

#         exp_str = ", ".join(f"{e['position']} at {e['company']}" for e in experience)
#         skills_str = ", ".join(skills)
#         proj_str = ", ".join(p["title"] for p in projects)
#         cert_str = ", ".join(c["name"] for c in certifications)

#         # Optional: aggregate achievements and results for better context
#         achievements = " | ".join(
#             a for e in experience for a in e.get("achievements", [])
#         )
#         results = " | ".join(
#             r for p in projects for r in p.get("results", [])
#         )

#         # Improved Gemini prompt
#         prompt = f"""
#         Write a professional resume summary using the following:
#         - Education: {edu_str}
#         - Experience: {exp_str}
#         - Skills: {skills_str}
#         - Projects: {proj_str}
#         - Project Results: {results}
#         - Achievements: {achievements}
#         - Certifications: {cert_str}

#         Guidelines:
#         - Limit to 4–5 lines
#         - Start with a strong title (e.g., "Results-driven Software Engineer")
#         - Focus on measurable accomplishments and technologies
#         - Use full sentences in a formal tone
#         - Avoid placeholder values like "X%", "[quantifiable achievement]", or "XYZ"
#         """

#         response = model.generate_content(prompt)
#         summary = "".join(part.text for part in response.parts).strip()
#         return clean_summary(summary)

#     except Exception as e:
#         print("AI Summary generation failed:", str(e))
#         return "Experienced professional with a strong technical background and a track record of delivering results in team-driven environments."







