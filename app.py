from flask import Flask, jsonify, render_template, session, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import sha256
from dotenv import load_dotenv
from datetime import datetime
import os

USERS = []
USERS_LIST = []
USER_INDEX = 0

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'SESSION_PSWD'
app.config['SECRET_KEY'] = os.urandom(24) 
db = SQLAlchemy(app)

# for id = 0 in range()

class User(db.Model):
    __tablename__ = 'cunts'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    cuntness = db.Column(db.BigInteger, unique=True, nullable=True)

    def __repr__(self):
        return f'<User: {self.name}, ID: {self.id}, Created at: {self.created_at}, Cuntness: {self.cuntness}>'


class Login(db.Model):
    __tablename__ = 'logins'
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    login = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, unique=False, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'<ID: {self.id}, Created at: {self.created_at}, Login: {self.login} ,Password: {self.password} ,Email: {self.email}>'

@app.route("/")
def index():
    print('Entered index route')
    #if 'index' not in session:
    #    print('here')
    #    session['index'] = 0
    session['index'] = 0
    global USERS
    global USERS_LIST
    USERS = User.query.all()
    USERS_LIST = [{'id': user.id, 'name': user.name, 'timestamp': user.created_at, 'Cuntness': user.cuntness} for user in USERS]
    print(session['index'])
    print('Exited index route')
    return render_template('index.html', user=USERS_LIST[0], previous_disabled=True, next_disabled=False)


@app.route('/previous', methods=['GET'])
def previous_user():
    print("hello")
    session['index'] = session['index'] - 1
    if session['index'] < 1:
        return render_template('index.html', user=USERS_LIST[0], previous_disabled=True, next_disabled=False)
    print(session['index'])
    return render_template('index.html', user=USERS_LIST[session['index']], previous_disabled=False, next_disabled=False)


@app.route('/next', methods=['GET'])
def next_user():
    global USERS_LIST

    print('Entered next route')
    print(session['index'])
    session['index'] = session['index'] + 1
    print(session['index'])
    if (session['index'] == len(USERS_LIST) - 1):
        return render_template('index.html', user=USERS_LIST[session['index']], previous_disabled=False, next_disabled=True)
    print(session['index'])
    print('Exited next route')
    return render_template('index.html', user=USERS_LIST[session['index']], previous_disabled=False, next_disabled=False)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        login = request.form['username']
        email = request.form['email']
        password = request.form['password']
        created_at = datetime.now().isoformat()
        
        # Hash the password
        hashed_password = sha256((password + "tiny pinch of salt").encode("utf-8")).hexdigest()
        
        # Check if the user already exists
        existing_login = Login.query.filter((Login.login == login) | (Login.email == email)).first()
        if existing_login:
            flash('User already exists', 'error')
            return redirect(url_for('signup'))
        
        # Create a new user
        new_login = Login(login=login, email=email, password=hashed_password, created_at=created_at)
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
        print("shit: ", login, password)
        # here is the problem
        current_entered_pass = sha256((password + "tiny pinch of salt").encode("utf-8")).hexdigest()

        if login and login.password == current_entered_pass:
            print("i succedded")
            session['user_id'] = login.id
            flash('Login successful', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/input user', methods=['GET'])
def input_user():
    global USERS_LIST

    print('User input page')
    return render_template('index.html', user=USERS_LIST[session['index']], previous_disabled=False, next_disabled=False)

########################


# Create the tables in the database (uncomment and run this once)
# db.create_all()

#@app.route('/')
#def hello():
#    return 'Hello, World!'

@app.route('/users', methods=['GET'])
def get_users():
    return render_template('users.html', users=USERS_LIST)

#@app.route('/users/<int:user_id>', methods=['GET'])
#def get_user(user_id):
#    user = User.query.get(user_id)
#    if user is None:
#        return jsonify({'error': 'User not found'}), 404
#    user_data = {'id': user.id, 'username': user.username, 'email': user.email}
#    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True)