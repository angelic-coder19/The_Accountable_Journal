from cs50 import SQL
from flask import Flask, flash, render_template, request, redirect, session
from flask_session import Session
from functools import wraps
import re
from werkzeug.security import generate_password_hash, check_password_hash


# Configure appliaction
app = Flask(__name__)

# Create connection to the database
db = SQL("sqlite:///journal.db")

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Login decorator function for access control
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET', 'POST'])
def index():

    # If the user has registered via a form 'POST'
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        print(name, email, password, confirmation)
        
        # Validation of name and email
        if not (name and name.strip()):
            error = "Enter a psuedo name eg. thoughtful-thinker12"
            return render_template("register.html", error = error)

        elif not (email and email.strip()):
            error = "Enter a valide email"

        # Validate email by using the email regex
        elif re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
            error = "Enter a valid email"
            return render_template("register.html", error = error)
        
        # Validate passwords to ensure they match
        elif not (password and password.strip()):
            error = "Enter a password"
            return render_template("register.html", error=error)
        elif not (confirmation and confirmation.strip()):
            error = "Please confirm your password"
            return render_template("register.html", error=error)
        
        elif str(password) != str(confirmation):
            error = "Your passwords do not match"
            return render_template("register.html", error=error)
        
        # Generate a hash of the password 
        passaword_hash = generate_password_hash(password)

        # Check if the a user with that email already exists 
        if db.execute("SELECT * FROM authors WHERE email = ?", email):
            error = "A user with " + email + " aready exists"
            return render_template("register.html", error=error)
        
        # Check if the entered username is alredy used
        if db.execute("SELECT * FROM authors WHERE name = ?", name):
            error = "Username " + name + " is already taken"
            return render_template("register.html", error=error)

        # If all is well register the user
        db.execute("""
                    INSERT INTO authors (name, email, password)
                    VALUES (?, ?, ?)""", name, email.strip(), passaword_hash
                  )
        
        # Create a new session for the user 
        user_id = db.execute("SELECT id FROM authors WHERE name = ? AND email = ?", name, email.strip())[0]['id']
        session["user_id"] = user_id

        # Send success massage to the dashboard and redirect to homepage
        flash(f"Welcome, {name} <br>  Your journaling journey awaits!") 
        return redirect("/home")

    return render_template("register.html")

@app.route("/home", methods=['GET','POST'])
@login_required
def home():
    # When data is sent from the frontend 
    if request.method == 'POST':
        user_id = session["user_id"]
        data = request.get_json()
        entry = data['entry']
        mood = data['mood']
        iv = data['iv']

        # Enter the mood, author_id and iv of the new entry
        db.execute("INSERT INTO entries (author_id, entry, iv, mood) VALUES (?, ?, ?, ?)", user_id, entry, iv, mood)
        
        # Enter the time of the entry
        entry_id = db.execute("SELECT id FROM entries WHERE iv = ? AND author_id = ?", iv, user_id)[0]['id']
        db.execute("""
                    INSERT INTO dates (entry_id, year, month, day, time)
                    VALUES (
                        ?,
                        CAST(strftime('%Y', 'now') AS INTEGER),
                        CAST(strftime('%m', 'now') AS INTEGER),
                        CAST(strftime('%d', 'now') AS INTEGER),
                        strftime('%H:%M', 'now')
                    )""", entry_id)
        
        flash("Your entery has been added")
        return redirect("home.html")

    return render_template("home.html")

@app.route("/logout")
@login_required
def logout():
    # Clear session inforamtion (user_id)  
    session.clear()
    
    #Redirect to register page
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get('password')
        email = request.form.get('email')

        # Validate email and password
        if not (password and password.strip()):
            error = "Please enter a password"
            return render_template("login.html", error=error)
        elif not (email and email.strip()): 
            error = "Please enter your email"
            return render_template("login.html", error=error)

        # Check if emails match
        db_email = db.execute("SELECT email FROM authors WHERE email = ?", email)[0]['email']
        if not db_email:
            error = "Incorrect email or password"
            return render_template("login.html", error=error)

        # Check if passwords match
        elif check_password_hash(password, db.execute("SELECT password FROM authors WHERE email = ?", email.strip())[0]['password']):
            error = "Incorrect email or password"
            return render_template("login.html", error=error)
        
        # Begin a new session for that user and redirect them to the homepage
        session["user_id"] = db.execute("SELECT id FROM authors WHERE email = ?", email.strip())[0]['id']
        name = db.execute("SELECT name FROM authors WHERE email = ?", email)[0]['name']
        flash(f"Welcome back, {name}!")
        return redirect("/home")

    return render_template("login.html")



