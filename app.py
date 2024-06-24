from config import app, db
from models import *
from flask import (
    render_template,
    session,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)
import pandas as pd
import numpy as np
import requests
import json
import os

from plots import make_plots, querry_bq

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sublime-lyceum-426907-r9-353181f6f35f.json'


def get_now():
    from datetime import datetime as dt

    return dt.now().isoformat()


def hash_password(password):
    from hashlib import sha256

    return sha256((password + "tiny pinch of salt").encode("utf-8")).hexdigest()


@app.route("/")
def index():
    return render_template('index.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False))


@app.route('/run', methods=['GET', 'POST'])
def run():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('run')
        return redirect(url_for('login'))
    
    google_map_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    plots = make_plots()
    df_historic_data = querry_bq()

    # filter the dataframe

    filtered_df_2024 = df_historic_data[df_historic_data['Year'] == 2024]
    filtered_df_2024 = filtered_df_2024.sort_values(by="Designacao")
    columns_to_drop = ["Latitude", "Longitude", "Year", "Month", "Day", "Localidade_Postal",
                       "Freguesia", "Codigo_do_Ponto_de_Atendimento", "Population_Density", "Codigo_Freguesia", "Data"]
    filtered_df_2024 = filtered_df_2024.drop(columns=columns_to_drop)
    # print(filtered_df_2024.head(100))

    # group the rows by designacao, averaging the other elements

    df_grouped = filtered_df_2024.groupby('Designacao').agg({"Procuras": 'mean',
                                                             "Atendimentos": 'mean',
                                                             "Desistencias": 'mean',
                                                             "Tempo_medio_de_espera_diario": 'mean',
                                                             "Population": 'mean',
                                                             }).reset_index()

    # Calculate the stress values

    stress_value = [int((a['Procuras'] * a['Desistencias'] * a['Tempo_medio_de_espera_diario'])
                        / (a['Atendimentos'] * a['Population']))
                    for a in json.loads(df_grouped.to_json(orient='records'))]

    # Dispose of unecessary data

    columns_to_drop = ["Procuras", "Atendimentos", "Desistencias",
                       "Tempo_medio_de_espera_diario", "Population"]
    df_grouped = df_grouped.drop(columns=columns_to_drop)
    df_grouped['stress_value'] = stress_value

    # {'Designacao': {'0': 'Loja de Cidadão Laranjeiras', '1': 'Loja de Cidadão Saldanha'}, 'stress_value': {'0': 28, '1': 43}}

    original_df = pd.read_csv('./static/assets/model_frame.csv')
    original_df.sort_values(by='Location')
    predictions = create_dataframe_with_random_deviation(original_df)
    loc1 = predictions['Location']
    to_merge_to_cards_table = predictions.sort_values(by='Location')
    columns_to_drop = ["Year", "Procuras",
                       "Tempo_medio_de_espera_diario", "Atendimentos", "Desistencias"]
    to_merge_to_cards_table = to_merge_to_cards_table.drop(
        columns=columns_to_drop)
    to_merge_to_cards_table = to_merge_to_cards_table.groupby(
        'Location').agg({"necessity_metric": 'mean'}).reset_index()
    # print(to_merge_to_cards_table.head(3))

    cards_table = []
    js = json.loads(df_grouped.to_json())
    js2 = json.loads(to_merge_to_cards_table.to_json())
    # print(js)
    for index in js['Designacao'].keys():
        cards_table.append({
            'Designacao': js['Designacao'][index],
            'stress_value': js['stress_value'][index],
            'necessity_metric': js2['necessity_metric'][index]
        })

    items = [f'Item {i}' for i in range(1, 3)]  # Example list of items
    # return render_template('index.html', items=items)
    return render_template(
        'run.html',
        isLoginPage=False,
        isAuthenticated=session.get("isAuthenticated", False),
        google_map_api_key=google_map_api_key,
        items=items,
        graph_html=plots,
        cards_data=cards_table
    )


# this is not used as of now
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        login = request.form['username']
        email = request.form['email']
        password = request.form['password']
        created_at = get_now()

        # Hash the password
        hashed_password = hash_password(password)

        # Check if the user already exists
        existing_login = Login.query.filter(
            (Login.login == login) | (Login.email == email)).first()
        if existing_login:
            flash('User already exists', 'error')
            return redirect(url_for('signup'))

        # Create a new user
        new_login = Login(login=login, email=email,
                          password=hashed_password, created_at=created_at)
        db.session.add(new_login)
        db.session.commit()

        flash('User created successfully', 'success')
        session['url'] = url_for('signup')
        return redirect(url_for('index'))

    return render_template('signup.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False))


def create_dataframe_with_random_deviation(original_data: pd.DataFrame) -> pd.DataFrame:
    percentage_deviation_large = 0.05
    percentage_deviation_small = 0.015

    new_data = original_data.copy()

    for column in ['Procuras', 'Tempo_medio_de_espera_diario', 'Desistencias', 'Atendimentos']:
        new_data[column] = new_data[column] * \
            (1 + np.random.uniform(-percentage_deviation_large,
             percentage_deviation_large, size=new_data.shape[0]))

    new_data['necessity_metric'] = new_data['necessity_metric'] * \
        (1 + np.random.uniform(-percentage_deviation_small,
         percentage_deviation_small, size=new_data.shape[0]))
    return new_data


@app.route('/predict', methods=['POST'])
def predict():
    original_df = pd.read_csv('/static/assets/model_frame.csv')
    predictions = create_dataframe_with_random_deviation(original_df)

    return jsonify(predictions)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("isAuthenticated", False):
        session['url'] = url_for('login')
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        login = Login.query.filter_by(login=username).first()
        # here is the problem
        current_entered_pass = hash_password(password)

        if login and login.password == current_entered_pass:
            session['user_id'] = login.id
            session["isAuthenticated"] = True
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(session.get('url', url_for('index')))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', isLoginPage=True, isAuthenticated=session.get("isAuthenticated", False))


@app.route('/logout', methods=['GET'])
def logout():
    session["isAuthenticated"] = False
    return redirect(url_for('index'))


@app.route("/profile")
def profile():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('profile')
        return redirect(url_for('login'))
    user = session.get("username")
    return render_template('profile.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), user=user)


@app.route('/report', methods=['GET', 'POST'])
def report():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('report')
        return redirect(url_for('login'))
    response = requests.get('https://www.worldpop.org/rest/data/pop/pic')

    if response.status_code == 200:
        data = response.json()

        # Select specific fields from the response
        report_data = [
            {
                "id": item["id"],
                "title": item["title"],
                "popyear": item["popyear"],
                "iso3": item["iso3"]
            }
            for item in data["data"]
        ] if data["data"] else []

        return render_template('report.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), report_data=report_data)
    else:
        return render_template('error.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), error="Failed to retrieve data"), response.status_code


@app.route('/save-report', methods=['POST'])
def save_report():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('report')
        return redirect(url_for('login'))
    if request.method == 'POST':
        print(request.form)


if __name__ == '__main__':
    app.run(debug=True)
