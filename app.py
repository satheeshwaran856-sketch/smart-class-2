import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

# DATABASE CONFIG (Render PostgreSQL or Local SQLite fallback)
database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- DATABASE TABLES ----------------

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dept = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    mood = db.Column(db.String(20), nullable=False)

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    students = Student.query.all()
    return render_template("dashboard.html", students=students)

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        dept = request.form["dept"]

        new_student = Student(name=name, dept=dept)
        db.session.add(new_student)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("add_student.html")

@app.route("/mark", methods=["POST"])
def mark():
    student_id = request.form["student_id"]
    status = request.form["status"]
    mood = request.form["mood"]

    record = Attendance(
        student_id=student_id,
        date=str(date.today()),
        status=status,
        mood=mood
    )

    db.session.add(record)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/report")
def report():
    records = Attendance.query.all()

    happy = sum(1 for r in records if r.mood == "Happy")
    normal = sum(1 for r in records if r.mood == "Normal")
    sad = sum(1 for r in records if r.mood == "Sad")

    return render_template("report.html",
                           happy=happy,
                           normal=normal,
                           sad=sad)

# ---------------- RUN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
