from flask import Flask, render_template, request, jsonify, redirect, url_for, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import re
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Replace with your secret key

# Define the SQLAlchemy database
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return 'Login Failed. Check your username and password.'
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists. Please choose a different one.'
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return 'Registration successful. You can now <a href="/login">login</a>.'

    return render_template('register.html')

# Define the GitHub statistics function
def get_github_stats(username):
    # Fetch user info including name
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url)
    user_data = response.json()

    if 'message' in user_data and user_data['message'] == 'Not Found':
        return jsonify({'error': 'User not found'}), 404

    # ... (rest of the code remains the same)

    return jsonify(stats)

@app.route('/get_github_stats', methods=['POST'])
@login_required
def fetch_github_stats():
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'Please provide a username'}), 400

    # Use app.app_context() to ensure you're working within the application context
    with app.app_context():
        return get_github_stats(username)

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)