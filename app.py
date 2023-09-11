from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import re

app = Flask(__name__)

# Define routes for different pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register')
def register():
    return render_template('register.html')

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
def fetch_github_stats():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Please provide a username"}), 400

    return get_github_stats(username)


if __name__ == '__main__':
    app.run(debug=True)
