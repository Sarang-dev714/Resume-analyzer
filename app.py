import re
import PyPDF2
from flask import Flask, render_template, request

app = Flask(__name__)

# SKILL KEYWORDS
skill_keywords = [
    "python", "java", "c", "c++", "sql", "html", "css", "javascript",
    "machine learning", "data analysis", "flask", "django",
    "react", "node", "excel", "power bi", "communication",
    "teamwork", "leadership"
]

# -------- FORMAT RESUME INTO SECTIONS --------
def format_resume(text):
    sections = {
        "Summary": "",
        "Education": "",
        "Experience": "",
        "Skills": "",
        "Other": ""
    }

    lines = text.split("\n")
    current_section = "Summary"

    for line in lines:
        l = line.lower()

        if "education" in l:
            current_section = "Education"
        elif "experience" in l or "intern" in l:
            current_section = "Experience"
        elif "skill" in l:
            current_section = "Skills"

        sections[current_section] += line + "\n"

    return sections


# -------- EXTRACT TEXT FROM PDF --------
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content

    return text


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        if 'resume' not in request.files:
            return "No file uploaded"

        file = request.files['resume']

        if file.filename == '':
            return "No file selected"

        # -------- EXTRACT TEXT --------
        text = extract_text(file)

        text_lower = text.lower()

        # -------- SKILL MATCH (SMART) --------
        found_skills = []

        for skill in skill_keywords:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.append(skill)

        missing_skills = [s for s in skill_keywords if s not in found_skills]

        # -------- SCORE SYSTEM --------
        score = 0

        # Skill weight
        score += len(found_skills) * 4

        # Resume length
        if len(text) > 1200:
            score += 20
        elif len(text) > 600:
            score += 10

        # Section presence
        if "experience" in text_lower:
            score += 10

        if "project" in text_lower:
            score += 10

        # Cap score
        score = min(score, 100)

        # -------- SUGGESTIONS --------
        suggestions = []

        if missing_skills:
            suggestions.append("Top missing skills to improve your resume:")
            for skill in missing_skills[:5]:
                suggestions.append(f"Add '{skill}' to increase ATS score")

        if len(found_skills) < 5:
            suggestions.append("Your resume lacks technical depth")
        elif len(found_skills) < 10:
            suggestions.append("Good, but add more domain-specific skills")
        else:
            suggestions.append("Strong technical profile")

        if "experience" not in text_lower:
            suggestions.append("Add a clear Experience section")

        if "project" not in text_lower:
            suggestions.append("Include projects to strengthen your resume")

        # -------- FORMAT RESUME --------
        formatted_resume = format_resume(text)

        return render_template(
            "index.html",
            formatted_resume=formatted_resume,
            skills=found_skills,
            missing_skills=missing_skills,
            score=score,
            suggestions=suggestions
        )

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)