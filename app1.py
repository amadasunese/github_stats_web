# app.py
from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a strong secret key
client_id = "3c97eb316b4881e9281c"
client_secret = "a7273ada0fb6854c937279472932ea69b012f141"
redirect_uri = "http://localhost:5000/callback"  # Update this with your actual callback URL

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    # Redirect the user to GitHub for authentication
    auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}"
    return redirect(auth_url)

@app.route("/callback")
def callback():
    # Handle the callback from GitHub and obtain the access token
    code = request.args.get("code")
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        },
        headers={"Accept": "application/json"},
    )
    data = response.json()
    access_token = data["access_token"]

    # Store the access token in the session
    session["access_token"] = access_token

    return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    # Fetch user profile data using the access token
    access_token = session.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    user_data = response.json()

    return render_template("profile.html", user_data=user_data)

if __name__ == "__main__":
    app.run(debug=True)

