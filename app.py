#!/usr/bin/python3
# This is application that provides insightful statistics about GitHub repositories.

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
app.secret_key = 'a97380abc78efeea392f4af3a04339ee'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Adding History model
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<History {self.username}>'


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define routes for different pages


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dashboard')
@login_required
def dashboard():
    is_dashboard_page = True
    user_is_logged_in = True
    # Retrieve user's history (replace with your own logic)
    user_history = History.query.filter_by(
        user_id=current_user.id).order_by(History.timestamp.desc()).all()
    return render_template('dashboard.html', is_dashboard_page=is_dashboard_page, user_is_logged_in=user_is_logged_in, user=current_user, user_history=user_history)

# Defining api to get repository statistics
def get_github_stats(username):
    # Fetch user info including name
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    user_data = response.json()

    if "message" in user_data and user_data["message"] == "Not Found":
        return jsonify({"error": "User not found"}), 404

    # Fetch user's public repositories
    repos_url = user_data["repos_url"]
    repos_response = requests.get(repos_url)
    repos_data = repos_response.json()

    # Initialize counters
    commits_count = 0
    forks_count = 0
    clones_count = 0

    # Calculate the total number of commits, forks, and clones
    for repo in repos_data:
        commits_url = f"https://api.github.com/repos/{username}/{repo['name']}/commits"
        commits_response = requests.get(commits_url)
        commits_data = commits_response.json()
        commits_count += len(commits_data)

        forks_count += repo["forks"]
        # clones_count += repo['clone_url']
        clone_url = "https://api.github.com/users/{username}"

        # Use regular expressions to extract the number of clones
        match = re.search(r"(\d+)", clone_url)

        # Check if a number was found in the URL
        if match:
            # Convert the matched string to an integer and add it to clones_count
            clones_count += int(match.group(0))

    # Fetch followers and following counts
    followers_count = user_data["followers"]
    following_count = user_data["following"]

    # Fetch user's starred repositories
    starred_url = f"https://api.github.com/users/{username}/starred"
    starred_response = requests.get(starred_url)
    starred_data = starred_response.json()

    # Calculate the number of likes (starred repositories count)
    likes_count = len(starred_data)

    # Create a dictionary with all the stats
    stats = {
        "username": user_data["login"],
        "name": user_data["name"],
        "public_repos": user_data["public_repos"],
        "commits": commits_count,
        "followers": followers_count,
        "following": following_count,
        "likes": likes_count,
        "forks": forks_count,
        "clones": clones_count,
    }

    return jsonify(stats)


@app.route("/get_github_stats", methods=["POST"])
@login_required
def fetch_github_stats():
    username = current_user.username
    if not username:
        return jsonify({"error": "Please provide a username"}), 400

    return get_github_stats(username)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


app.static_folder = 'static'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
