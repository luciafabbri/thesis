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

# Caricamento domande
def load_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    files = [
        os.path.join(base_dir, "./static/non_toxic_sample.csv"),
        os.path.join(base_dir, "./static/racism_sample.csv"),
        os.path.join(base_dir, "./static/harassment_sample.csv"),
        os.path.join(base_dir, "./static/vulgarity_sample.csv"),
        os.path.join(base_dir, "./static/violence_sample.csv")
    ]
    questions = {}
    for i, file in enumerate(files, start=1):
        df = pd.read_csv(file)
        random_questions = random.sample(df["text"].tolist(), 5)
        for j, question in enumerate(random_questions, start=1):
            questions[f"q{i*5+j}_text"] = question
            questions[f"q{i*5+j}_response"] = None  # Placeholder per la risposta
    return questions  

# Salvataggio risposte nel database
def save_responses(age_group, gender, questions, responses):
    conn = get_db_connection()
    cur = conn.cursor()

    # Uniamo le domande e le risposte in un dizionario per inserire i valori
    values = {
        "age_group": age_group,
        "gender": gender,
        **questions,  # Aggiungi tutte le domande
        **responses,  # Aggiungi tutte le risposte
    }
    
    # Query dinamica per inserire tutte le risposte
    query = """
    INSERT INTO responses (age_group, gender, 
    q1_text, q1_response, q2_text, q2_response, q3_text, q3_response, q4_text, q4_response,
    q5_text, q5_response, q6_text, q6_response, q7_text, q7_response, q8_text, q8_response, 
    q9_text, q9_response, q10_text, q10_response, q11_text, q11_response, q12_text, q12_response,
    q13_text, q13_response, q14_text, q14_response, q15_text, q15_response, q16_text, q16_response,
    q17_text, q17_response, q18_text, q18_response, q19_text, q19_response, q20_text, q20_response,
    q21_text, q21_response, q22_text, q22_response, q23_text, q23_response, q24_text, q24_response,
    q25_text, q25_response) 
    VALUES (%(age_group)s, %(gender)s, 
    %(q1_text)s, %(q1_response)s, %(q2_text)s, %(q2_response)s, %(q3_text)s, %(q3_response)s, %(q4_text)s, %(q4_response)s,
    %(q5_text)s, %(q5_response)s, %(q6_text)s, %(q6_response)s, %(q7_text)s, %(q7_response)s, %(q8_text)s, %(q8_response)s,
    %(q9_text)s, %(q9_response)s, %(q10_text)s, %(q10_response)s, %(q11_text)s, %(q11_response)s, %(q12_text)s, %(q12_response)s,
    %(q13_text)s, %(q13_response)s, %(q14_text)s, %(q14_response)s, %(q15_text)s, %(q15_response)s, %(q16_text)s, %(q16_response)s,
    %(q17_text)s, %(q17_response)s, %(q18_text)s, %(q18_response)s, %(q19_text)s, %(q19_response)s, %(q20_text)s, %(q20_response)s,
    %(q21_text)s, %(q21_response)s, %(q22_text)s, %(q22_response)s, %(q23_text)s, %(q23_response)s, %(q24_text)s, %(q24_response)s,
    %(q25_text)s, %(q25_response)s);
    """
    
    # Esegui la query
    cur.execute(query, values)
    
    # Commit e chiudi la connessione
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
        questions = session.get("questions", {})
        responses = {f"q{i}_response": request.form.get(f"q{i}") for i in range(1, 26)}  # Ricevi le risposte dal form
        age_group = session.get("age_group")
        gender = session.get("gender")
        save_responses(age_group, gender, questions, responses)
        return "Thank you for completing the survey!"
    
    questions = load_questions()
    session["questions"] = questions
    return render_template("survey_app.html", questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
