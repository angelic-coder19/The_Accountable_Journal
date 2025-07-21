from cs50 import SQL
from flask import Flask, flash, render_template, request, redirect, session, jsonify
from flask_session import Session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from psycopg.rows import dict_row
import re
import os
import psycopg


# Configure appliaction
app = Flask(__name__)

# Create connection to Postgres DB using environemnt variables from .env file
load_dotenv()

# Check for Heroku DATABASE_URL 
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Make the connection for the production envirionment
    conn = psycopg.connect(DATABASE_URL, autocommit= True, row_factory=dict_row)
else:
    # Connect to local database environment 
    conn = psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"), 
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        row_factory=dict_row  # This ensures we get back a list of dicts from queries
    )

# Create connection to the database
db = SQL("sqlite:///journal.db")

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Global list to store search results
search_results = []

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
        elif re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', email) is None:
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

        """
        # Check if the a user with that email already exists 
        if db.execute("SELECT * FROM authors WHERE email = ?", email):
            error = "A user with " + email + " aready exists"
            return render_template("register.html", error=error)
        """

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM authors WHERE email = %s;", (email,))
            user_email = cur.fetchone()
        if user_email:
            flash(f"A user with {email} already exists")
            return redirect("/")
        """
        # Check if the entered username is alredy used
        if db.execute("SELECT * FROM authors WHERE name = ?", name):
            error = "Username " + name + " is already taken"
            return render_template("register.html", error=error)
        """
        
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM authors WHERE name = %s;", (name,))
            inititial_user = cur.fetchone()
        if inititial_user:
            error = "A user with " + name + " is already taken "
            return render_template("register.html", error=error)
        """
        # If all is well register the user
        db.execute(""
                    INSERT INTO authors (name, email, password)
                    VALUES (?, ?, ?)"", name, email.strip(), passaword_hash
                  )
        """
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO authors (name, email, password)
                        VALUES (%s, %s, %s);""", (name, email.strip(), passaword_hash))
            conn.commit() 
        
        """
        # Create a new session for the user 
        user_id = db.execute("SELECT id FROM authors WHERE name = ? AND email = ?", name, email.strip())[0]['id']
        """

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM authors WHERE name = %s and email = %s;", (name, email.strip()))
            user_id = cur.fetchone()["id"]

        session["user_id"] = user_id

        # Send success massage to the dashboard and redirect to homepage
        flash(f"Welcome, {name} <br>  Your journaling journey awaits!") 
        return redirect("/home")

    return render_template("register.html")

@app.route("/make_entry", methods=['GET','POST'])
@login_required
def make_entry():
    # When data is sent from the frontend 
    if request.method == 'POST':
        user_id = session["user_id"]
        # Get the entry input from the front end 
        data = request.get_json()
        entry = data['entry']
        mood = data['mood']
        iv = data['iv']

        # Enter the mood, author_id and iv of the new entry
        """
        db.execute("INSERT INTO entries (author_id, entry, iv, mood) VALUES (?, ?, ?, ?)", user_id, entry, iv, mood)
        """
        with conn.cursor() as cur:
            cur.execute("INSERT INTO entries (author_id, entry, iv, mood) VALUES (%s, %s, %s, %s);", (user_id, entry, iv, mood))
            conn.commit()

        # Enter the time of the entry
        """
        entry_id = db.execute("SELECT id FROM entries WHERE iv = ? AND author_id = ?", iv, user_id)[0]['id']
        """
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM entries WHERE iv = %s AND author_id = %s;",
                         (iv, user_id)
            )
            entry_id = cur.fetchone()["id"]
        with conn.cursor() as cur:    
            cur.execute("""
                        INSERT INTO dates (entry_id, year, month, day, time)
                        VALUES (
                            %s,
                            EXTRACT(YEAR FROM CURRENT_TIMESTAMP)::INTEGER,
                            EXTRACT(MONTH FROM CURRENT_TIMESTAMP)::INTEGER,
                            EXTRACT(DAY FROM CURRENT_TIMESTAMP)::INTEGER,
                            TO_CHAR(CURRENT_TIMESTAMP, 'HH24:MI')
                        );""", (entry_id,))
            conn.commit()
        flash("Your entery has been added")
        # Return redirect route after success
        return jsonify({'status': 'success', 'redirect': '/home'})

    # When the home page is reached
    return render_template("make_entry.jinja2")

@app.route("/logout")
@login_required
def logout():
    # Clear session inforamtion (user_id)  
    session.clear()
    
    #Redirect to register page
    flash("You were Successfully logged out <br> Goodbye")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached this route via POST by filling in a form 
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
        """
        rows = db.execute(
            "SELECT * FROM authors WHERE email = ?", email
        ) 
        """
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM authors WHERE email = %s", (email,))
            rows = cur.fetchall()

        # Ensure that the user exists and the password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]['password'], password
        ):
            error = "Incorrect email and/or password" 
            return render_template("login.html", error=error)

        # Begin a new session for that user and redirect them to the homepage
        session["user_id"] = rows[0]['id']
        name = rows[0]['name']
        flash(f"Welcome back, {name}!")
        return redirect("/home")

    return render_template("login.html")

@app.route("/info", methods=['GET','POST'])
@login_required
def info():
    """ Query for all the Entries and allow for search operations """ 

    # When the page is simply requested, send the enties to frontend
    """
    info = db.execute(""
                    SELECT entry, iv, id, mood, year, month, day, time
                    FROM entries
                    JOIN dates ON entries.id = dates.entry_id
                    WHERE entries.id IN 
                    (
                        SELECT id 
                        FROM entries 
                        WHERE author_id = ?
                    )"", 12
    )
    """
    index = 1
    #for inf in info:
    """
    with conn.cursor() as cur:
        cur.execute("INSERT INTO entries (entry, iv, mood, author_id) VALUES (%s, %s, %s, %s);",(inf["entry"], inf["iv"], inf["mood"], session["user_id"]))
        conn.commit()
    
    with conn.cursor() as cur2:
        cur2.execute("INSERT INTO dates (year, month, day, time, entry_id) VALUES (%s, %s, %s, %s, %s);", 
                    (inf["year"], inf["month"], inf["day"], inf["time"], index))
        conn.commit()
    index += 1
    """
    # Find out if a user is logged in
    user_id = session.get("user_id")
    if user_id:
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT entry, iv, mood, year, month, day, time
                    FROM entries
                    JOIN dates ON entries.id = dates.entry_id
                    WHERE entries.id IN 
                    (
                        SELECT id 
                        FROM entries 
                        WHERE author_id = %s
                    )
                    ORDER BY id DESC;""", (user_id,)
            )
            info = cur.fetchall()

        return jsonify(info)
    else:
        return jsonify([])

@app.route("/key")
@login_required
def key():
    """ Send the encryption key to the frontend for use """
    """
    key = db.execute("SELECT key FROM keys")[0]["key"]
    """
    with conn.cursor() as cur: 
        cur.execute("SELECT key FROM keys;")
        key = cur.fetchone()["key"]

    return jsonify(key)

@app.route("/home", methods=['POST', 'GET'])
@login_required
def home():
    """ Allow the user to search for information that they have """
    global search_results
    
    # Collect all the 'searchables' and make them ready to both templates
    """
    searchables = db.execute(""
                    SELECT mood, year, month, day
                    FROM entries
                    JOIN dates ON entries.id = dates.entry_id
                    WHERE entries.id IN 
                    (
                        SELECT id 
                        FROM entries 
                        WHERE author_id = ?
                    )
                    ORDER BY id DESC"", session["user_id"]
    )
    """
    with conn.cursor() as cur: 
        cur.execute("""
                    SELECT mood, year, month, day
                    FROM entries
                    JOIN dates ON entries.id = dates.entry_id
                    WHERE entries.id IN 
                    (
                        SELECT id 
                        FROM entries 
                        WHERE author_id = %s
                    )
                    ORDER BY id DESC;""", (session["user_id"],)
        )
        searchables = cur.fetchall()

    # Make empty lists for each of the searchables
    moods = [] 
    years = [] 
    months = []
    days = []

    # Iterate over each of the dicts in the searchables list and append the individual lists 
    for searchable in searchables:
        # Append only distict items into each searchable
        if searchable["mood"] not in moods:
            moods.append(searchable["mood"])

        if searchable["year"] not in years:
            years.append(searchable["year"])

        if searchable["month"] not in months: 
            months.append(searchable["month"])

        if searchable["day"] not in days:
            days.append(searchable["day"])

    # If the user searches for a specific entry by filining in the form
    if request.method == "POST":
        # Get the search parameters from the form
        mood = request.form.get('mood')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        
        # Render a message if no parameter has been passed
        if (not mood) and (not month) and (not year) and (not day):
            flash("You have not passed any parameters into your search")
            return redirect("/home")
        # Initialize a query 
        query = """
            SELECT entry, iv, mood, month, day, time, year
            FROM entries 
            JOIN dates ON entries.id = dates.entry_id 
            WHERE entries.id IN (
                SELECT id FROM entries 
                WHERE author_id = %s
            )   
        """
        # Initialise list of values for placeholders if a searcha parameter is given
        values = [session["user_id"]]

        # Append filters conditionally 
        if year and year != 'year':
            query += " AND year = %s"
            values.append(int(year))
        else:
            query += " AND year = year"

        if month and month != 'month':
            query += " AND month = %s"
            values.append(int(month))
        else:
            query += " AND month = month"
        
        if day and day != 'day':
            query += " AND day = %s"
            values.append(int(day))
        else: 
            query += " AND day = day"

        if mood:
            query += " AND mood = %s"
            values.append(mood)
        else:
            query += " AND mood = mood"
        
        with conn.cursor() as cur:
            cur.execute(query + ";", values)
            results = cur.fetchall()   
        
        # Inform the user if no results are found
        if len(results) == 0:
            flash("No entries were found from your search parameters")
            return redirect("/home")            

        # Append the results to the global array 
        search_results = results
        return render_template("search_results.jinja2", moods=moods, years=years, days=days, months=months )

    # If page id accessed via GET, Render the template and give the 'searchables'
    return render_template("search.jinja2", moods=moods, years=years, days=days, months=months)

@app.route("/delete", methods=['POST'])
@login_required
def delete():
    """ Deleting entries """
    time = request.get_json()["del_time"]
    mood = request.get_json()["del_mood"]

    """
    # Get the id of the entry given the inforamtion from the frontend
    id = db.execute(f""
        SELECT id 
        FROM entries
        WHERE mood = ? AND author_id = {session["user_id"]}
        INTERSECT 
        SELECT entry_id 
        FROM dates 
        WHERE time = ?"", mood, time
    )[0]["id"]
    """
    with conn.cursor() as cur:
        cur.execute("""
        SELECT id 
        FROM entries
        WHERE mood = %s AND author_id = %s
        INTERSECT 
        SELECT entry_id 
        FROM dates 
        WHERE time = %s;""", (mood, session["user_id"], time)
        )
        id = cur.fetchone()["id"]
    """
    # Delete the rows with that id from both tables
    db.execute(f"DELETE FROM entries WHERE id = {id}")
    """
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM entries WHERE id = {id};")
        conn.commit()

    # flash a success message 
    flash("Your entry has been successfully deleted")
    return redirect("/home")

@app.route("/results")
@login_required
def results():

    return jsonify(search_results)

# A filter to make months more readable 
def getStringMonth(month):
    match month:
        case 1:
            return "January"
        case 2: 
            return "February"
        case 3: 
            return "March"
        case 4:
            return "April"
        case 5:
            return "May"
        case 6:
            return "June"
        case 7:
            return "July"
        case 8:
            return "August"
        case 9:
            return "September"
        case 10:
            return "October"
        case 11:
            return "November"
        case 12:
            return "December"
        case _:
            return month

# Custom jinja filter to convert months in numbers to strings 
app.jinja_env.filters["getStringMonth"] = getStringMonth


"""
STATS 
- Overall number of entries made by a user.
    * Query for the all the entries made by that user
    * Something like COUNT (*) AS num_entries

- Pie chart showing percentage of entries by mood
    * Learn chart JavaScript Library that does visualization:
    * Feed this library with the all the moods by that user: 
    * something like SELECT mood FROM entries

- Most verbose or Consise or detailed entry
    * We can do this in two ways, on the frontend with a function 
        in Javascrip that can count the number of words
    * Or we can cleanly find the longest entry in the database and select just that entry
    * Something like SELECT entry FROM entries WHERE (some condition to check for the longest sentence)

- Most expressive day
    * This one could be done best on the frontend after encryption has happended
    * A JavaScript Algorithm can check how many emojis an entry has 

    
It is best if all this info is passed in a single JSON object once
check if JSON can have child object within.
 - Yes JSON can have baby JSON perfect for this
 - Use a single python list called "stats" this object will have 4 fields to begin with
   * first key value pair is for number of commments first
        It is better to find the entry count on the client side for more dymanism 
   * first key value pair will be a baby JSON object called "moods" to store all the moods 
        This object will collect all the number of instances of each mood 
        * It will all come from a query that aggregates all the moods 
        * This then will be the baby json object called moods that will be ready fro rendering

"""

@app.route("/stats")
@login_required
def stats():

    # Query for the numbers of each of the moods that user has 
    """
    information = db.execute(""
                SELECT mood, COUNT(mood) AS times 
                FROM entries
                WHERE author_id = ?
                GROUP BY mood"", session["user_id"]
    )
    """
    with conn.cursor() as cur:
        cur.execute("""
                SELECT mood, COUNT(mood) AS times 
                FROM entries
                WHERE author_id = %s
                GROUP BY mood""", (session["user_id"],)
        )
        information = cur.fetchall()
    
    # Stats dict to store each mood and corresponding count
    stats = {"moods": [], "times":[], "longest_entry": []}
    for info in information:
        stats["moods"].append(info["mood"])
        stats["times"].append(info["times"])

    # Find the longest entry from the database 
    """
    longest_entry = db.execute(""
            SELECT entry, iv, mood, year, month, day, time
            FROM entries
            JOIN dates ON entries.id = dates.entry_id
            WHERE LENGTH(entries.entry) = (
                SELECT MAX(LENGTH(entry)) 
                FROM entries 
                WHERE author_id = ?
            )
    "", session["user_id"]                           
    )[0]
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT entry, iv, mood, year, month, day, time
            FROM entries
            JOIN dates ON entries.id = dates.entry_id
            WHERE LENGTH(entries.entry) = (
                SELECT MAX(LENGTH(entry)) 
                FROM entries 
                WHERE author_id = %s
            )
        """, (session["user_id"],)
        )
        longest_entry = cur.fetchone()

    # Add the longest entry to the stas json object
    stats["longest_entry"].append(longest_entry)
 
    return jsonify(stats)   

@app.route("/analytics")
@login_required
def analytics():
    # Simply render the analytics template

    return render_template("analytics.jinja2")