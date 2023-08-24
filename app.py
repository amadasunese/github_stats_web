from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GITHUB_API_BASE_URL = "https://api.github.com"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user/<username>')
def get_user_profile(username):
    # Fetch user profile data from GitHub API
    user_url = f"{GITHUB_API_BASE_URL}/users/{username}"
    response = requests.get(user_url)
    if response.status_code == 200:
        user_data = response.json()
        return jsonify(user_data)
    else:
        return jsonify(error_message="User not found"), 404

@app.route('/api/repositories/<username>')
def get_user_repositories(username):
    # Fetch user repositories from GitHub API
    repositories_url = f"{GITHUB_API_BASE_URL}/users/{username}/repos"
    response = requests.get(repositories_url)
    if response.status_code == 200:
        repositories_data = response.json()
        return jsonify(repositories_data)
    else:
        return jsonify(error_message="User not found"), 404

@app.route('/api/repository/<username>/<repo_name>')
def get_repository_details(username, repo_name):
    # Fetch repository details from GitHub API
    repository_url = f"{GITHUB_API_BASE_URL}/repos/{username}/{repo_name}"
    response = requests.get(repository_url)
    if response.status_code == 200:
        repository_data = response.json()
        return jsonify(repository_data)
    else:
        return jsonify(error_message="Repository not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
