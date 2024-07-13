from config import app, supabase, cache
from flask import (
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)
# from cache import Cache
import pandas as pd
import numpy as np
import json
import os
import warnings
from dateutil import parser
from datetime import datetime

# to config file
from flask_session import Session

warnings.filterwarnings("ignore")

from plots import make_plots, DF_PREDICTED, DF_HISTORICAL, supabase_querry, supabase_insert

available_locations = ['Loja de Cidadão Laranjeiras' , 'Loja de Cidadão Saldanha']

# to config file
Session(app)

USING_CACHE = 0
CACHE_TIMEOUT = 500


def get_current_time():
    from datetime import datetime as dt

    return dt.now().isoformat()


def hash_password(password):
    from hashlib import sha256

    return sha256((password + os.getenv('PASSWORD_SALT')).encode("utf-8")).hexdigest()


@app.route("/")
def index():
    return render_template('index.html',
                           isAuthenticated=session.get("isAuthenticated", False),
                           user=session.get("username"))


def generate_cards(length_of_prediction, location=None):
    cards = []
    if not location:
        for location in available_locations:
            cards.append(make_plots(location, length_of_prediction))
    else:
        cards.append(make_plots(location, length_of_prediction))
    sorted_cards = sorted(cards, key=lambda x: x['summary']['max_necessity_metric'],
                        reverse=True)
    
    return sorted_cards


@app.route('/run', methods=['GET', 'POST'])
def run():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('run')
        return redirect(url_for('index'))

    prediction_period = request.args.get('period')
    prediction_location = request.args.get('location')

    if not prediction_period:
        return redirect(url_for('index'))
    length_of_prediction = prediction_period.split()[0]

    google_map_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    session['cache_key'] = prediction_location + length_of_prediction
    cards = cache.get(session['cache_key'])
    if not cards:
        cards = generate_cards(length_of_prediction)
        if USING_CACHE:
            cache.set(session['cache_key'], cards, timeout=CACHE_TIMEOUT)

    cards_js = [
        {
            'latitude': card['latitude'],
            'longitude': card['longitude'],
            'location': card['location'],
            'safe_location': card['safe_location']
        }
        for card in cards
    ]
        
    return render_template(
        'run.html',
        isAuthenticated=session.get("isAuthenticated", False),
        google_map_api_key=google_map_api_key,
        cards=cards,
        cards_js=cards_js,
        user=session.get("username")
    )

@app.route('/edit', methods=['GET'])
def edit():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('run')
        return redirect(url_for('index'))

    # get the same data as the run page
    return render_template(
        'edit.html',
        isAuthenticated=session.get("isAuthenticated", False),
        google_map_api_key=os.getenv('GOOGLE_MAP_API_KEY'),
        user=session.get("username")
    )


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return redirect(url_for('index')) # for now no signing up

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

    return render_template('signup.html', isAuthenticated=session.get("isAuthenticated", False))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("isAuthenticated", False):
        session['url'] = url_for('login')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_check = (
            supabase.table('users')
            .select('username', 'password', 'id')
            .eq('username', username)
            .execute()
        ).data

        if user_check and user_check[0]['password'] == hash_password(password):
            session["isAuthenticated"] = True
            session['user_id'] = user_check[0]['id']
            session['username'] = user_check[0]['username']
            flash('Login successful', 'info')
            return redirect(session.get('url', url_for('index')))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('index'))

    return render_template('login.html', isAuthenticated=session.get("isAuthenticated", False))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session['isAuthenticated'] = False
    session['user_id'] = -1
    session['username'] = ''

    return redirect(url_for('index'))


@app.route('/save-report', methods=['POST'])
def save_report():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('report')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            print('creating report...')
            body = request.get_json()
            location = body.get('location')
            prediction_period = body.get('period')
            length_of_prediction = prediction_period.split()[0]
            cards = cache.get(session['cache_key'])
    
            if not cards:
                cards = generate_cards(length_of_prediction, location)
                if USING_CACHE:
                    cache.set(session['cache_key'], cards, timeout=CACHE_TIMEOUT)

            this_card = next((card for card in cards if card.get('location') == location), None)
            this_card.pop('plots_merged')
            this_card.pop('plots_historic')
            this_card.pop('safe_location')
            # this_card.pop('summary')
            this_card.pop('latitude')
            this_card.pop('longitude')
            this_card.pop('data_by_year')
            
            from bs4 import BeautifulSoup
            this_card['insights'] = BeautifulSoup(this_card['insights'], "html.parser").get_text()
            # Remove this when generated report is done properly
            this_card['old_insights'] = this_card['insights']

            body['card'] = this_card

            report = {
                "created_at": datetime.now().isoformat(),
                "report": body,
                "user": session.get("user_id", -1)
            }
            supabase_insert('reports', report)
            print('report created!')
            return jsonify({'status': 'success'})
        except Exception as e:
            print(str(e))
            return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/profile")
def profile():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('profile')
        return redirect(url_for('index'))
    return render_template('profile.html', isAuthenticated=session.get("isAuthenticated", False), user=session.get("username"))


@app.route('/report', methods=['GET', 'POST'])
def report():
    if not session.get("isAuthenticated", False):
        session['url'] = url_for('report')
        return redirect(url_for('index'))

    # Filtered querry to supabase
    reports = (
        supabase.table("reports")
        .select("*")
        .eq("user", session.get('user_id', -1))
        .execute()
    ).data


    report_data = []
    for report in reports:
        user = (
            supabase.table('users')
            .select('username', 'email', 'id')
            .eq('id', report['user'])
            .execute()
        ).data
        if not user:
            continue
        report['created_at'] = parser.parse(report['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        report_data.append({
            'created_at': report['created_at'],
            'report': report['report'],
            'user': user[0]['username'],
            'email': user[0]['email'],
    })
        
    return render_template(
        'report.html',
        isAuthenticated=session.get("isAuthenticated", False),
        report_data=report_data,
        user=session.get("username")
    )


if __name__ == '__main__':
    app.run(debug=True)
