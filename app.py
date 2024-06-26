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
import warnings

warnings.filterwarnings("ignore")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sublime-lyceum-426907-r9-353181f6f35f.json'
from plots import make_plots, DF_PREDICTED, DF_HISTORICAL

available_locations = ['Loja de Cidadão Laranjeiras' , 'Loja de Cidadão Saldanha']

def get_current_time():
    from datetime import datetime as dt

    return dt.now().isoformat()


def hash_password(password):
    from hashlib import sha256

    return sha256((password + "tiny pinch of salt").encode("utf-8")).hexdigest()


@app.route("/")
def index():
    user = session.get("username")
    return render_template('index.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), user=user)


def create_cards_table():
    df_predicted = DF_PREDICTED
    df_predicted['Meses'] = pd.to_datetime(df_predicted['Meses'])
    df_predicted['Ano'] = df_predicted['Meses'].dt.year
    df_predicted = df_predicted.groupby(['Designacao', 'Ano']).agg({
        'Procuras': 'sum',
        'Atendimentos': 'sum',
        'Desistencias': 'sum',
        'Tempo_medio_de_espera_diario': 'mean',
        'Necessity_Metric': 'mean'
    }).reset_index()
    df_predicted['Necessity_Metric'] = df_predicted['Necessity_Metric'].astype(int)
    idx = df_predicted.groupby('Designacao')['Necessity_Metric'].idxmax()
    max_necessity_metric_entries = df_predicted.loc[idx]
    max_necessity_metric_entries = max_necessity_metric_entries.sort_values(by='Necessity_Metric', ascending=False)
    cards_table = []
    js = json.loads(max_necessity_metric_entries.to_json())
    i = 0
    for item in js['Designacao'].keys():
        cards_table.append({
            'index': i,
            'designacao': js['Designacao'][item],
            'necessity_metric': js['Necessity_Metric'][item]
        })
        i += 1
    return cards_table



@app.route('/run', methods=['GET', 'POST'])
def run():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('run')
        return redirect(url_for('login'))

    google_map_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    plots = []
    for location in available_locations:
        plots.append(make_plots(location))
    cards_table = create_cards_table()

    return render_template(
        'run.html',
        isLoginPage=False,
        isAuthenticated=session.get("isAuthenticated", False),
        google_map_api_key=google_map_api_key,
        graph_html=plots,
        cards_data=cards_table,
        user = session.get("username")
    )


# this is not used as of now
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        login = request.form['username']
        email = request.form['email']
        password = request.form['password']
        created_at = get_current_time()

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
    # session["isAuthenticated"] = True
    # return redirect(url_for('index'))

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

@app.route('/save-report', methods=['POST'])
def save_report():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('report')
        return redirect(url_for('login'))

    if request.method == 'POST':
        body = request.get_json()

        # cards_table = create_cards_table()
        # print(cards_table)
        
        report = Report(created_at=datetime.now(), report=json.dumps(body), user=session.get("user_id"))
        db.session.add(report)
        db.session.commit()

    return redirect(url_for('report'))


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

    reports = Report.query.all()
    

    report_data = []
    for report in reports:
        user = Login.query.filter_by(id=report.user).first()
        report_data.append({
            'created_at': report.created_at.strftime("%d" + "-" + "%m" + "-" + "%Y"),
            'report': report.report,
            'user': user.login
        })

    return render_template('report.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), report_data=report_data, user=session.get("username"))


if __name__ == '__main__':
    app.run(debug=True)


    # FROM RUN
    # # Print BigQuery data on terminal
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', 1000)

    # df_historic_data = querry_bq('sublime-lyceum-426907-r9', 'ama', 'merged')

    # # filter the dataframe
    # filtered_df_2024 = df_historic_data[df_historic_data['Year'] == 2024]
    # filtered_df_2024 = filtered_df_2024.sort_values(by="Designacao")
    # columns_to_drop = ["Latitude", "Longitude", "Year", "Month", "Day", "Localidade_Postal",
    #                    "Freguesia", "Codigo_do_Ponto_de_Atendimento", "Population_Density", "Codigo_Freguesia", "Data"]
    # filtered_df_2024 = filtered_df_2024.drop(columns=columns_to_drop)

    # # group the rows by designacao, averaging the other elements
    # df_grouped = filtered_df_2024.groupby('Designacao').agg({"Procuras": 'mean',
    #                                                          "Atendimentos": 'mean',
    #                                                          "Desistencias": 'mean',
    #                                                          "Tempo_medio_de_espera_diario": 'mean',
    #                                                          "Population": 'mean',
    #                                                          }).reset_index()

    # # Calculate the stress values
    # stress_value = [int((a['Procuras'] * a['Desistencias'] * a['Tempo_medio_de_espera_diario'])
    #                     / (a['Atendimentos'] * a['Population']))
    #                 for a in json.loads(df_grouped.to_json(orient='records'))]

    # # Dispose of unecessary data

    # columns_to_drop = ["Procuras", "Atendimentos", "Desistencias",
    #                    "Tempo_medio_de_espera_diario", "Population"]
    # df_grouped = df_grouped.drop(columns=columns_to_drop)
    # df_grouped['stress_value'] = stress_value

    # original_df = pd.read_csv('./static/assets/model_frame.csv')
    # original_df.sort_values(by='Location')
    # predictions = create_dataframe_with_random_deviation(original_df)
    # to_merge_to_cards_table = predictions.sort_values(by='Location')
    # columns_to_drop = ["Year", "Procuras",
    #                    "Tempo_medio_de_espera_diario", "Atendimentos", "Desistencias"]
    # to_merge_to_cards_table = to_merge_to_cards_table.drop(
    #     columns=columns_to_drop)
    # to_merge_to_cards_table = to_merge_to_cards_table.groupby(
    #     'Location').agg({"necessity_metric": 'mean'}).reset_index()
    # # print(to_merge_to_cards_table.head(3))