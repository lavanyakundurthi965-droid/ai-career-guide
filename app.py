from flask import Flask, render_template, request, send_file
import os
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

last_result = {}

@app.route("/", methods=["GET", "POST"])
def home():
    global last_result

    name = None
    skills = []
    missing_skills = []
    score_breakdown = {}
    action_plan = []
    ai_feedback = ""
    score = 0
    level = ""
    domain_match_message = ""

    if request.method == "POST":
        name = request.form["name"]
        choice = request.form["choice"]

        # CATEGORY DEFINITIONS
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

        selected_category = categories[choice]

        file = request.files["resume"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            text_lower = text.lower()

            # 🔍 DETECT DOMAIN
            domain_scores = {}

            for key, value in categories.items():
                count = 0
                for word in value["keywords"]:
                    if word in text_lower:
                        count += 1
                domain_scores[value["name"]] = count

            detected_domain = max(domain_scores, key=domain_scores.get)

            # 🎯 MATCH CHECK
            if detected_domain != selected_category["name"]:
                domain_match_message = f"⚠️ Your resume matches {detected_domain}, but you selected {selected_category['name']}."
                penalty = 15
            else:
                domain_match_message = f"✅ Your resume matches the selected domain ({selected_category['name']})."
                penalty = 0

            # SKILLS
            for skill in selected_category["keywords"]:
                if skill in text_lower:
                    skills.append(skill)
                else:
                    missing_skills.append(skill)

            # SCORE
            score = 50
            score_breakdown["Base"] = 50

            skill_score = len(skills) * 5
            score += skill_score
            score_breakdown["Skills"] = skill_score

            project_score = 10 if "project" in text_lower else 0
            score += project_score
            score_breakdown["Projects"] = project_score

            # APPLY PENALTY
            score -= penalty
            score_breakdown["Domain Penalty"] = -penalty

            if score < 0:
                score = 0
            if score > 100:
                score = 100

            # LEVEL
            if score < 50:
                level = "Beginner"
            elif score < 80:
                level = "Intermediate"
            else:
                level = "Strong"

            # ACTION PLAN
            for skill in missing_skills:
                action_plan.append(f"Learn {skill}")

            first_name = name.split()[-1] if name else "User"

            # ✅ PROFESSIONAL FEEDBACK
            ai_feedback = f"{first_name}, your resume demonstrates a strong foundation in the {detected_domain} domain. "

            if detected_domain != selected_category["name"]:
                ai_feedback += f"However, you have selected {selected_category['name']}, which requires a different skill set and may not fully align with your current profile. "
                ai_feedback += f"If you are aiming to transition into {selected_category['name']}, it is recommended to start building skills in {', '.join(missing_skills)}. "
                ai_feedback += f"You can also explore hybrid roles that combine your existing expertise with {selected_category['name']}. "
            else:
                ai_feedback += f"Your profile aligns well with your selected domain. To further strengthen your profile, focus on improving {', '.join(missing_skills)} and building practical projects. "

            ai_feedback += "Consistent skill development and real-world application will significantly enhance your career opportunities."

            # SAVE
            last_result = {
                "name": name,
                "score": score,
                "level": level,
                "skills": skills,
                "missing_skills": missing_skills,
                "action_plan": action_plan,
                "feedback": ai_feedback
            }

    return render_template(
        "index.html",
        name=name,
        skills=skills,
        ai_feedback=ai_feedback,
        score=score,
        missing_skills=missing_skills,
        score_breakdown=score_breakdown,
        level=level,
        action_plan=action_plan,
        domain_match_message=domain_match_message
    )

# PDF DOWNLOAD
@app.route("/download")
def download():
    file_path = "report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    y = 750

    def draw_multiline(text, x, y):
        max_chars = 80
        while len(text) > max_chars:
            split_index = text.rfind(" ", 0, max_chars)
            if split_index == -1:
                split_index = max_chars
            line = text[:split_index]
            c.drawString(x, y, line)
            text = text[split_index+1:]
            y -= 15
        c.drawString(x, y, text)
        return y - 15

    c.drawString(100, y, f"Name: {last_result.get('name', '')}")
    y -= 30
    c.drawString(100, y, f"Score: {last_result.get('score', '')}")
    y -= 30
    c.drawString(100, y, f"Level: {last_result.get('level', '')}")

    y -= 40
    c.drawString(100, y, "Feedback:")
    y -= 20
    y = draw_multiline(last_result.get("feedback", ""), 120, y)

    c.save()
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)