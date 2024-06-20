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
from dotenv import load_dotenv
import os

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
        return redirect(url_for('login'))
    google_map_api_key = os.getenv('GOOGLE_MAP_API_KEY')
    # def index():
    items = [f'Item {i}' for i in range(1, 3)]  # Example list of items
    # return render_template('index.html', items=items)
    return render_template('run.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), google_map_api_key=google_map_api_key, items=items)


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

    return render_template('signup.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("isAuthenticated", False):
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
            return redirect(url_for('index'))
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
        return redirect(url_for('login'))
    user = session.get("username")
    print(user)
    return render_template('profile.html', isLoginPage=False, isAuthenticated=session.get("isAuthenticated", False), user=user)


@app.route('/report', methods=['GET', 'POST'])
def report():
    if not session.get("isAuthenticated", False):
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
        return redirect(url_for('login'))
    if request.method == 'POST':
       print(request.form)


if __name__ == '__main__':
    app.run(debug=True)
