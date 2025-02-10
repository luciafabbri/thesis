import random
import pandas as pd
import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# Configurazione Database
DB_NAME = "thesis_survey"
DB_USER = "thesis_survey_user"
DB_PASSWORD = "gWy2zsdQoT3dKYPhfdbkI80bz2NdZNqc"
DB_HOST = "dpg-cul0pj8gph6c738e8ut0-a.frankfurt-postgres.render.com"
DB_PORT = "5432"

# Connessione al database
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# Caricamento domande (nessuna modifica qui)
def load_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    files = [
        os.path.join(base_dir, "./static/non_toxic_sample.csv"),
        os.path.join(base_dir, "./static/racism_sample.csv"),
        os.path.join(base_dir, "./static/harassment_sample.csv"),
        os.path.join(base_dir, "./static/vulgarity_sample.csv"),
        os.path.join(base_dir, "./static/violence_sample.csv")
    ]
    questions = []
    for file in files:
        df = pd.read_csv(file)
        random_questions = random.sample(df["text"].tolist(), 5)
        questions.extend(random_questions)
    return questions  

# Salvataggio risposte nel database (modifica essenziale)
def save_responses(age_group, gender, questions, responses):
    conn = get_db_connection()
    cur = conn.cursor()
    for question, response in zip(questions, responses):
        cur.execute(
            "INSERT INTO survey_responses (age_group, gender, question, response) VALUES (%s, %s, %s, %s)",
            (age_group, gender, question, response)
        )
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def start_survey():
    if request.method == "POST":
        session["age_group"] = request.form.get("age_group")
        session["gender"] = request.form.get("gender")
        return redirect(url_for("survey"))
    return render_template("start_survey.html")

@app.route("/survey", methods=["GET", "POST"])
def survey():
    if request.method == "POST":
        questions = session.get("questions", [])
        responses = [request.form.get(f"q{i}") for i in range(1, len(questions) + 1)]
        age_group = session.get("age_group")
        gender = session.get("gender")
        save_responses(age_group, gender, questions, responses)
        return "Thank you for completing the survey!"
    
    questions = load_questions()
    session["questions"] = questions
    return render_template("survey_app.html", questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
