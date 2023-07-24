from flask import Flask, render_template, g, request, redirect, flash, url_for, session
import sqlite3
import bcrypt

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'moha1251'
app.config['DATABASE'] = 'database.db'

# Database initialization
# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(app.config['DATABASE'])
#         g.db.row_factory = sqlite3.Row
#     return g.db

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        g._database = db
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?' , (email,)).fetchone()
        db.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Successful login, set user as logged in
            session['user_id'] = user['id']

            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        # Clear the session to log out the user
        session.clear()
        flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))



@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email is already registered
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email is already registered. Please use a different email.', 'error')
        else:
            # Hash the password before storing it in the database
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert the new user into the database
            cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                           (first_name, last_name, email, hashed_password))
            conn.commit()

            flash('Registration successful. You can now log in with your credentials.', 'success')
            # return redirect('/login')
            return redirect(url_for('index'))

    return render_template('registration.html')

def set_greeting():
    if 'user_id' in session:
        #Fetch user details from db
        db = get_db()
        cursor = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        db.close()

        #personalize user with greeting
        g.greeting = f'Hello, {user["first_name"]}!'
    else:
        #greeting for non-users
        g.greeting = 'Hello, Guest'


@app.before_request
def before_request():
    if 'user_id' in session:
        db = get_db()
        cursor = db.execute('SELECT first_name FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        db.close()

        g.greeting = f'Hello, {user["first_name"]}!'
    else:
        g.greeting = 'Hello, Guest!'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/security', methods=['GET', 'POST'])
def security():
    if request.method == 'POST':

        if 'user_id' in session:
        # Get the user ID from the current user
            user_id = session['user_id']

            # Get the comment text from the form
            comment_text = request.form.get('comment')

            # Create a new Comment object
            comment = Comment(user_id, 'security', comment_text)

            # Save the comment to the database
            comment.save()

            # Redirect back to the security page
            return redirect(url_for('security'))

    # Retrieve existing comments for the security page
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE page = 'security'")
    comments = cursor.fetchall()
    conn.close()

    return render_template('security.html', comments=comments)

@app.route('/quality', methods=['GET', 'POST'])
def quality():
    if request.method == 'POST':
        # Get the user ID from the current user
        user_id = session['user_id']

        # Get the comment text from the form
        comment_text = request.form.get('comment')

        # Create a new Comment object
        comment = Comment(user_id, 'quality', comment_text)

        # Save the comment to the database
        comment.save()

        # Redirect back to the quality page
        return redirect(url_for('quality'))

    # Retrieve existing comments for the quality page
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE page = 'quality'")
    comments = cursor.fetchall()
    conn.close()

    return render_template('quality.html', comments=comments)


@app.route('/usability', methods=['GET', 'POST'])
def usability():
    if request.method == 'POST':
        # Get the user ID from the current user
        user_id = session['user_id']

        # Get the comment text from the form
        comment_text = request.form.get('comment')

        # Create a new Comment object
        comment = Comment(user_id, 'usability', comment_text)

        # Save the comment to the database
        comment.save()

        # Redirect back to the quality page
        return redirect(url_for('usability'))

    # Retrieve existing comments for the quality page
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comments WHERE page = 'usability'")
    comments = cursor.fetchall()
    conn.close()

    return render_template('usability.html', comments=comments)


@app.route('/add_comment', methods=['POST'])
def add_comment():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You must be logged in to leave a comment.', 'error')
            return redirect(url_for('login'))

        user_id = session['user_id']
        page = request.form.get('page')
        comment_text = request.form.get('comment')

        if not user_id or not page or not comment_text:
            flash('Invalid comment data.', 'error')
        else:
            comment = Comment(user_id, page, comment_text)
            comment.save()
            flash('Comment added successfully!', 'success')

    return redirect(request.referrer)


# Comment model
class Comment:
    def __init__(self, user_id, page, comment):
        self.user_id = user_id
        self.page = page
        self.comment = comment

    def save(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (user_id, page, comment) VALUES (?, ?, ?)",
                       (self.user_id, self.page, self.comment))
        conn.commit()

if __name__ == '__main__':
    app.run(debug=True)
