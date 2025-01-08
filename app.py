import random
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Necessario per gestire la sessione

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
        # Seleziona 5 domande casuali da ciascun file
        random_questions = random.sample(df["text"].tolist(), 5)
        questions.extend(random_questions)

    return questions  # Lista di 25 domande


def save_responses(age_group, gender, questions, responses):
    # Inizializza un dizionario per i dati da salvare
    data = {
        "AgeGroup": [age_group],
        "Gender": [gender]
    }

    # Aggiungi le domande e le risposte in modo dinamico
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        # Crea una colonna per il testo della domanda e una per la risposta
        data[f"Q{i}Text"] = [question]
        data[f"Q{i}Response"] = [response]

    # Converte in dataframe
    df = pd.DataFrame(data)
    
    # Ottieni il percorso assoluto della cartella corrente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definisci il percorso completo del file responses.csv
    file_path = os.path.join(base_dir, './static/responses.csv')
    
    # Salva su CSV
    if not os.path.isfile(file_path):
        # Se il file non esiste, salva l'intestazione e i dati
        df.to_csv(file_path, index=False)
    else:
        # Se il file esiste, aggiungi i dati senza l'intestazione
        df.to_csv(file_path, mode='a', header=False, index=False)


@app.route("/", methods=["GET", "POST"])
def start_survey():
    if request.method == "POST":
        # Salva età e genere nella sessione
        session["age_group"] = request.form.get("age_group")
        session["gender"] = request.form.get("gender")
        return redirect(url_for("survey"))

    return render_template("start_survey.html")


@app.route("/survey", methods=["GET", "POST"])
def survey():
    if request.method == "POST":
        # Recupera le domande e risposte dalla richiesta
        questions = session.get("questions", [])
        responses = [request.form.get(f"q{i}") for i in range(1, len(questions) + 1)]

        # Recupera età e genere dalla sessione
        age_group = session.get("age_group")
        gender = session.get("gender")

        # Salva i dati
        save_responses(age_group, gender, questions, responses)
        return "Thank you for completing the survey!"

    # Carica le domande e salvale nella sessione
    questions = load_questions()
    session["questions"] = questions

    # Passa le domande al template
    return render_template("survey_app.html", questions=questions)


if __name__ == "__main__":
    app.run(debug=True)
