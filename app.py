from config import app, db
from models import *
from flask import (
    render_template,
    session,
    request,
    redirect,
    url_for,
    session,
    flash
)
import requests


def get_now():
    from datetime import datetime as dt

    return dt.now().isoformat()

def hash_password(password):
    from hashlib import sha256

    return sha256((password + "tiny pinch of salt").encode("utf-8")).hexdigest()


@app.route("/")
def index():
    if 'index' not in session:
        session['index'] = 0
    return render_template('index.html')

@app.route('/run', methods=['GET', 'POST'])
def run():
    # if not logged in
    #     return redirect(url_for('index'))
    return render_template('run.html')


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
        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        login = Login.query.filter_by(login=username).first()
        # here is the problem
        current_entered_pass = hash_password(password)

        if login and login.password == current_entered_pass:
            session['user_id'] = login.id
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        num_fields = int(request.form.get('num_fields', 10))
    else:
        num_fields = int(request.args.get('num_fields', 10))

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
            for item in data["data"][:num_fields]
        ]

        return render_template('report.html', report_data=report_data, num_fields = num_fields)
    else:
        return render_template('error.html', error="Failed to retrieve data"), response.status_code
    

if __name__ == '__main__':
    app.run(debug=True)
