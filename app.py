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
from cache import Cache
import pandas as pd
import numpy as np
import json
import os
import warnings

warnings.filterwarnings("ignore")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sublime-lyceum-426907-r9-353181f6f35f.json'

from plots import make_plots, DF_PREDICTED, DF_HISTORICAL

available_locations = ['Loja de Cidadão Laranjeiras' , 'Loja de Cidadão Saldanha']

CACHE = Cache(disk=False)


def get_current_time():
    from datetime import datetime as dt

    return dt.now().isoformat()


def hash_password(password):
    from hashlib import sha256

    return sha256((password + "tiny pinch of salt").encode("utf-8")).hexdigest()


@app.route("/")
def index():
    return render_template('index.html',
                           isLoginPage=False,
                           isAuthenticated=session.get("isAuthenticated", False),
                           user=session.get("username"))


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
    df_predicted['Necessity_Metric'] = df_predicted['Necessity_Metric'].round(2)
    idx = df_predicted.groupby('Designacao')['Necessity_Metric'].idxmax()
    max_necessity_metric_entries = df_predicted.loc[idx]
    max_necessity_metric_entries = max_necessity_metric_entries.reset_index(drop=True)
    max_necessity_metric_entries['Index'] = max_necessity_metric_entries.index
    max_necessity_metric_entries = max_necessity_metric_entries.sort_values(by='Necessity_Metric', ascending=False)
    cards_table = []
    js = json.loads(max_necessity_metric_entries.to_json())
    for index, item in enumerate(js['Designacao'].keys()):
        cards_table.append({
            'index_before_sorting': js['Index'][item],
            'index': index,
            'designacao': js['Designacao'][item],
            'necessity_metric': js['Necessity_Metric'][item]
        })
    return cards_table


@app.route('/run', methods=['GET', 'POST'])
def run():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('run')
        return redirect(url_for('login'))

    # # Period for prediction
    period = request.args.get('period')
    if not period:
        period = '1 year'

    length_of_prediction = period.split()[0]

    google_map_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    plots_merged = []
    plots_historic = []
    data_by_year = []
    data_analysis = {}
    for location in available_locations:
        pm, ph, dby, msg = CACHE.get(f'{location}', make_plots, location)
        if not pm:
            pm, ph, dby, msg = make_plots(location)

        plots_merged.append(pm)
        plots_historic.append(ph)
        data_by_year.append(dby)
        data_analysis[location] = msg

    cards_table = CACHE.get('cards_table', create_cards_table)
    CACHE.set('data_analysis', data_analysis)

    return render_template(
        'run.html',
        isLoginPage=False,
        isAuthenticated=session.get("isAuthenticated", False),
        google_map_api_key=google_map_api_key,
        graph_html_merged=plots_merged,
        graph_html_historic=plots_historic,
        data_by_year=data_by_year,
        data_analysis=data_analysis,
        cards_data=cards_table,
        user=session.get("username")
    )

@app.route('/edit', methods=['GET'])
def edit():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('run')
        return redirect(url_for('login'))

    # get the same data as the run page
    return render_template(
        'edit.html',
        isLoginPage=False,
        isAuthenticated=session.get("isAuthenticated", False),
        google_map_api_key=os.getenv('GOOGLE_MAP_API_KEY'),
        user=session.get("username")
    )


# this is not used as of now
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return redirect(url_for('login')) # for now no signing up

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
    if session.get("isAuthenticated", False):
        session['url'] = url_for('login')
        return redirect(url_for('index'))

    if request.method == 'POST':
        CACHE.clear()

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
    CACHE.clear()

    session.pop("user_id", None)
    session.pop("username", None)
    session["isAuthenticated"] = False
    return redirect(url_for('index'))


@app.route('/save-report', methods=['POST'])
def save_report():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('report')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            body = request.get_json()
            location = body.get('location')

            cards_table = CACHE.get('cards_table', create_cards_table)
            data_analysis = CACHE.get('data_analysis', lambda: {})

            # Filter cards_table for the specific location
            filtered_cards_table = next([card for card in cards_table if card.get('designacao') == location])

            # Update body with the filtered data
            body['cards_table'] = filtered_cards_table
            body['AI_insight'] = data_analysis[location]

            # Create the Report object
            report = Report(
                created_at=datetime.now(),
                report=json.dumps(body),
                user=session.get("user_id"),
                cards_table=json.dumps(filtered_cards_table),
                AI_insight=data_analysis[location]
            )

            db.session.add(report)
            db.session.commit()

            return jsonify({'status': 'success'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/profile")
def profile():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('profile')
        return redirect(url_for('login'))
    return render_template('profile.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), user=session.get("username"))


@app.route('/report', methods=['GET', 'POST'])
def report():
    # if not session.get("isAuthenticated", False):
    #     session['url'] = url_for('report')
    #     return redirect(url_for('login'))

    reports = Report.query.all()[::-1]

    report_data = []
    for report in reports:
        user = Login.query.filter_by(id=report.user).first()
        report_data.append({
            'created_at': report.created_at.strftime("%d" + "-" + "%m" + "-" + "%Y"),
            'report': report.report,
            'user': user.login,
            'email': user.email,
            'cards_table': report.cards_table,
            'AI_insight': report.AI_insight
    })

    return render_template(
        'report.html',
        isLoginPage=False,
        isAuthenticated=session.get("isAuthenticated", False),
        report_data=report_data,
        user=session.get("username")
    )


if __name__ == '__main__':
    app.run(debug=True)
