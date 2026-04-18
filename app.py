from flask import Flask, render_template, request, send_file
import os
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

last_result = {}

@app.route("/", methods=["GET", "POST"])
def home():
    global last_result

    name = None
    skills = []
    missing_skills = []
    role_missing_skills = []
    score = 0
    level = ""
    ai_feedback = ""
    domain_match_message = ""
    match_percentage = 0

    if request.method == "POST":
        name = request.form["name"]
        choice = request.form["choice"]
        role = request.form["role"]

        categories = {
            "1": {
                "name": "Technology",
                "keywords": ["python", "sql", "machine learning", "flask", "git"],
            },
            "2": {
                "name": "Creativity",
                "keywords": ["figma", "photoshop", "design", "ui", "ux"],
            },
            "3": {
                "name": "Business",
                "keywords": ["marketing", "sales", "communication", "excel", "analytics"],
            }
        }

        job_roles = {
            "Data Scientist": ["python", "machine learning", "statistics", "sql"],
            "Web Developer": ["html", "css", "javascript", "flask", "git"],
            "UI/UX Designer": ["figma", "design", "ui", "ux"],
            "Business Analyst": ["excel", "analytics", "communication", "sql"]
        }

        selected_category = categories[choice]
        required_role_skills = job_roles.get(role, [])

        file = request.files["resume"]

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            text_lower = text.lower()

            # Detect skills
            for skill in selected_category["keywords"]:
                if skill in text_lower:
                    skills.append(skill)
                else:
                    missing_skills.append(skill)

            # Role matching
            matched = 0
            for skill in required_role_skills:
                if skill in text_lower:
                    matched += 1
                else:
                    role_missing_skills.append(skill)

            if required_role_skills:
                match_percentage = int((matched / len(required_role_skills)) * 100)

            # Score
            score = 50 + (len(skills) * 5)
            score = min(score, 100)

            # Level
            if score < 50:
                level = "Beginner"
            elif score < 80:
                level = "Intermediate"
            else:
                level = "Strong"

            # Feedback
            first_name = name.split()[-1]

            ai_feedback = f"{first_name}, your resume shows a good foundation in {selected_category['name']}. "

            ai_feedback += f"For the role of {role}, your match is {match_percentage}%. "

            if role_missing_skills:
                ai_feedback += f"You should focus on learning {', '.join(role_missing_skills)} to improve your chances. "
            else:
                ai_feedback += "Your profile strongly matches this role. "

            ai_feedback += "Building real-world projects will further strengthen your profile."

            last_result = {
                "name": name,
                "score": score,
                "level": level,
                "feedback": ai_feedback
            }

    return render_template(
        "index.html",
        name=name,
        skills=skills,
        missing_skills=missing_skills,
        role_missing_skills=role_missing_skills,
        score=score,
        level=level,
        ai_feedback=ai_feedback,
        match_percentage=match_percentage
    )


@app.route("/download")
def download():
    file_path = "report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)

    c.drawString(100, 750, f"Name: {last_result.get('name', '')}")
    c.drawString(100, 720, f"Score: {last_result.get('score', '')}")
    c.drawString(100, 690, f"Level: {last_result.get('level', '')}")
    c.drawString(100, 660, f"Feedback: {last_result.get('feedback', '')}")

    c.save()
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)