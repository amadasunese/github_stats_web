from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from .models import db, User, RegistrationLog, UsageLog, History
import requests
import re
from datetime import datetime
from flask import request
from werkzeug.utils import secure_filename
import os
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../users.db'
# Initialize db in the app context
db.init_app(app)

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
