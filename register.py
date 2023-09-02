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
