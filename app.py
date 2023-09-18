#!/usr/bin/python3
# This is application that provides insightful statistics about GitHub repositories.
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, RegistrationLog, UsageLog, History
import requests
import re
from datetime import datetime
from flask import request
from werkzeug.utils import secure_filename
import os
import matplotlib.pyplot as plt
import io
import base64
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../users.db'
app.secret_key = 'a97380abc78efeea392f4af3a04339ee'

# Initialize db in the app context
db.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    profession = db.Column(db.String(80))
    telephone = db.Column(db.String(20))
    profile_photo = db.Column(db.String(255))  # Store the file path here
    __table_args__ = {'extend_existing': True}

    def __init__(self, username, password, name=None, email=None, profession=None, telephone=None, profile_photo=None):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.profession = profession
        self.telephone = telephone
        self.profile_photo = profile_photo

    def __repr__(self):
        return f'<User {self.username}>'

# Define a RegistrationLog model to log user registrations
class RegistrationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_description = db.Column(db.String(255))
    __table_args__ = {'extend_existing': True}

    def __init__(self, user_id, event_description):
        self.user_id = user_id
        self.event_description = event_description

# Define a UsageLog model to log user interactions and usage
class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_description = db.Column(db.String(255))
    __table_args__ = {'extend_existing': True}

    def __init__(self, user_id, event_description):
        self.user_id = user_id
        self.event_description = event_description

# Adding History model
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<History {self.username}>'

# ... Rest of your routes and main code
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
    # Log the registration event
    registration_log = RegistrationLog(user_id=user.id, event_description="User registered")
    db.session.add(registration_log)
    db.session.commit()


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

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the URL to scrape from the request
    url = request.form.get('url')

    if not url:
        return jsonify({"error": "URL not provided"}), 400

    # Make an HTTP request to the URL
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch the web page"}), 500

    # Parse the HTML content of the page using BeautifulSoup
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Perform web scraping here
    # Extract data from the HTML using BeautifulSoup methods

    # Example: Extract all the <a> tags from the page
    links = soup.find_all('a')
    link_texts = [link.get_text() for link in links]

    # Create a JSON response with the scraped data
    scraped_data = {
        "url": url,
        "links": link_texts
    }

    return jsonify(scraped_data)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define a function to handle file uploads
def upload_profile_photo():
    if 'profile_photo' in request.files:
        profile_photo = request.files['profile_photo']
        if profile_photo.filename != '':
            # Securely save the uploaded file
            filename = secure_filename(profile_photo.filename)
            profile_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Save the file path to the user model in the database
            current_user.profile_photo = filename
            db.session.commit()

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

    # Create a bar chart to visualize commits, forks, and clones
    labels = ["Commits", "Forks", "Clones"]
    values = [commits_count, forks_count, clones_count]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values)
    plt.xlabel("GitHub Metrics")
    plt.ylabel("Count")
    plt.title(f"GitHub Stats for {username}")
    plt.tight_layout()

    # Save the plot as an image in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()

    # Convert the image to base64
    graph_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Create a dictionary with all the stats and the graph image
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
        "graph_image": graph_image  # Add the graph image to the response
    }

    return jsonify(stats)

@app.route("/get_github_stats", methods=["POST"])
@login_required
def fetch_github_stats():
    username = current_user.username
    if not username:
        return jsonify({"error": "Please provide a username"}), 400

    return get_github_stats(username)


app.static_folder = 'static'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
