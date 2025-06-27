from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
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
#session(app)

# Login decorator function for access control
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
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

        if not (email and email.strip()):
            error = "Enter a valide email"

        # Validate email by using the email regex
        if re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
            error = "Enter a valid email"
            return render_template("register.html", error = error)
        
        # Validate passwords to ensure they match
        if not (password and password.strip()):
            error = "Enter a password"
            return render_template("register.html", error=error)
        if not (confirmation and confirmation.strip()):
            error = "Please confirm your password"
            return render_template("register.html", error=error)
        
        if str(password) != str(confirmation):
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
        error = "You have been registered"
        return render_template("register.html", error=error)

    return render_template("register.html")




