from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Step 2: Create an Application Instance
app = Flask(__name__)

# Step 3: Configure Your Database (SQLite in this example)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'

# Step 4: Initialize the Database
db = SQLAlchemy(app)

# Step 5: Define Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# Step 6: Create Database Tables
with app.app_context():
    db.create_all()

# Step 7: Start Your Application
if __name__ == '__main__':
    app.run(debug=True)
