import sqlite3
import os

DB_PATH = os.path.join("database", "resume_screening.db")

SAMPLE_JOBS = [
    {
        "title": "Software Development Engineer I",
        "company": "Amazon",
        "description": "We are looking for a Software Development Engineer with strong skills in Python, SQL, REST APIs, and distributed data systems. Experience with PySpark, Delta Lake, and cloud platforms like Azure or OCI is a plus. Familiarity with FastAPI and backend development is required.",
        "required_skills": "Python, SQL, REST APIs, PySpark, Delta Lake, FastAPI, Azure, OCI"
    },
    {
        "title": "Backend Developer",
        "company": "KPMG",
        "description": "Seeking a backend developer skilled in Python and SQL for building scalable APIs. Experience with database management systems, object-oriented programming, and REST API development is essential.",
        "required_skills": "Python, SQL, REST API, DBMS, OOP"
    },
    {
        "title": "Data Engineer",
        "company": "IBM",
        "description": "Looking for a Data Engineer with experience in distributed data processing, PySpark, Delta Lake, and Databricks. Strong SQL and Python skills required, along with experience building ETL pipelines.",
        "required_skills": "PySpark, Delta Lake, Databricks, SQL, Python, ETL"
    },
    {
        "title": "Full Stack Developer",
        "company": "Oracle",
        "description": "We need a full stack developer proficient in JavaScript, HTML, CSS, and backend frameworks. Knowledge of REST APIs, databases, and cloud deployment is a plus.",
        "required_skills": "JavaScript, HTML, CSS, REST API, SQL"
    },
    {
        "title": "Machine Learning Engineer",
        "company": "TensorLabs",
        "description": "Looking for an ML Engineer with experience in Python, TensorFlow, Keras, and computer vision using OpenCV. Experience with convolutional neural networks and model evaluation required.",
        "required_skills": "Python, TensorFlow, Keras, OpenCV, CNN"
    },
]


def seed_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for job in SAMPLE_JOBS:
        cursor.execute(
            "INSERT INTO jobs (title, company, description, required_skills) VALUES (?, ?, ?, ?)",
            (job["title"], job["company"], job["description"], job["required_skills"])
        )

    conn.commit()
    conn.close()
    print(f"Seeded {len(SAMPLE_JOBS)} jobs into the database.")


if __name__ == "__main__":
    seed_jobs()