from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests

app = Flask(__name__)

# Define routes for different pages
@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register')
def register():
    return render_template('register.html')

# Define an API route to fetch GitHub stats (you can keep this as it is)
@app.route('/get_github_stats', methods=['POST'])
def get_github_stats():
    username = request.json['username']
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url)
    data = response.json()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
