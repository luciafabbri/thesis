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

# Salvataggio risposte nel database
def save_responses(age_group, gender, questions, responses):
    conn = get_db_connection()
    cur = conn.cursor()

    # Aggiungi la query per l'inserimento dei dati nelle colonne corrette
    query = """
        INSERT INTO responses (age_group, gender, 
                               q1_text, q1_response, 
                               q2_text, q2_response, 
                               q3_text, q3_response, 
                               q4_text, q4_response, 
                               q5_text, q5_response, 
                               q6_text, q6_response, 
                               q7_text, q7_response, 
                               q8_text, q8_response, 
                               q9_text, q9_response, 
                               q10_text, q10_response, 
                               q11_text, q11_response, 
                               q12_text, q12_response, 
                               q13_text, q13_response, 
                               q14_text, q14_response, 
                               q15_text, q15_response, 
                               q16_text, q16_response, 
                               q17_text, q17_response, 
                               q18_text, q18_response, 
                               q19_text, q19_response, 
                               q20_text, q20_response, 
                               q21_text, q21_response, 
                               q22_text, q22_response, 
                               q23_text, q23_response, 
                               q24_text, q24_response, 
                               q25_text, q25_response)
        VALUES (%s, %s,
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s)
    """
    
    # Crea una lista con le risposte da inserire
    values = [age_group, gender]
    
    # Assumiamo che le risposte siano una lista con le risposte per ogni domanda
    for i in range(len(questions)):
        question_column = f"q{i+1}_text"
        response_column = f"q{i+1}_response"
        question = questions[i]
        response = responses[i]
        
        # Aggiungi domanda e risposta alla lista dei valori
        values.extend([question, response])
    
    # Esegui l'inserimento nel database
    cur.execute(query, values)
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
        # Recupera le risposte
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
