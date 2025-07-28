# **The Accountable Journal:**

The Accountable Journal is the future of journaling. It was built with one goal <i>make journaling addictive and fun</i>

This document will attempt to breakdown and explain the design choices.
>[!NOTE] 
> This documentat will refer to "The Accountable Journal" as "the app" for simpliciy
## Getting Started 
1. Clone this repo using `git clone`
2. Create a virtual environment
3. Add a `.env` file with required environment variables such as database name and password on your local machine. 
    >[!TIP]
    > If you plan on hosting this locally on your machine, you may find it more useful to use a SQLite database which is very easy to setup and manage queries with using `SQL` from the `cs50` library.
    > However, this app uses a PostgreSQL database due to its easy integration with cloud based hosting services such as Heroku and Vercel.<br>
    >Your can <b>NOT</b> use SQLite on cloud based hosting services due to its file type nature.
5. Run: `python main.py` if you have completed all the above steps successfully.


## main.py
This is the main python script that is the controller for the whole system. main.py uses functions from different libraries. 
### libraries
The following are the libraries and imports and their uses:
1. `flask` 
    This is the core library or a "mini-framework" enabling the use of python for web-programming, the app imports several functions from the `flask` library, these are:
    + `Flask` 
      this enables us to convert the following python script into a fully functioning flask application, basically allowing python to be put on the server. this was done using the following one liner:
      ```
      # Configure application
      app = Flask(__name__)
      ```
    + `flash` 
      This enables the sending of user feedback based on some action. For example, when a user has entered and incorrect password or email they will get a message at the top of their screen. illustrated:
      ```
      flash("Incorrect email and/or password")
      return redirect("/login")
      ``` 
      In other context where redirection is not done server-side, the flash function also works if the response on the server is json to redirect on the server side:
      ```
      flash("Your entery has been added")
      # Return redirect route after success
      return jsonify({'status': 'success', 'redirect': '/home'})
      ```
    + `render_template`
      This function quite literally "renders templates". Used to mosty for GET request to simply render an html or jinja templates.
    + `request`
      This is a useful object that allows the app to get information from http packets. This information could be  the method such as GET or POST, form data, json content. some example usage:
      ```
      if request.method == 'POST':          # Checks the http method
            mood = request.form.get('mood') # Gets the value in the http form
      ```
    + `redirect`
      This function allows users to navigated to another route on the app after a certain action.<br>
      Example usage after a successfull login:
      ```
      # Send success massage to the dashboard and redirect to homepage
      flash(f"Welcome, {name} <br>  Your journaling journey awaits🌟!") 
      return redirect("/home")
      ```
    + `session`
      This flask object that allows us to track information about the app. <br>
      This primary information that this object contains is about the user currently interacting with the app. 
      The object contains a key called the user_id `session["user_id"]<br> 
      This key will contain the current user's id which is the unique number assined to each user when they create an account or when they log in<br>
    + `jsonify`
      This is a useful self discriptive function that can convert any python dictionary(dict) or list into json. <br>
      This is esspecially useful for sending information to the client via fetch request request. Example usage in the /key route:
      ```
        # Return success message
        return jsonify({"message":"Your entry has been deleted successfully🚩"})
      ```
      The above example converts a python dict into json that the client can interprate and use. 
2. `flask_session` 
    From this library, the app uses `Session`.
    This allows to configure session information about the app. This configuration included permanence of the session, and session type to use a filesystem as opposed to signed cookies.
    Example usage from the app:
    ```
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    ```
3. `flask_talisman`
    The app imports `wraps` from this library. `wraps` allows us to "decorate" functions. which is wrapping one function within another function.
    This is especially useful in the allowing certain routes to require login. 
4. `werkzeug.security` 
    from this library, the app imports two functions 
    + `generate_password_hash` 
        This funcition is obviously used create a hashed version of a password that the user enters. this is used in the `/register` route to store a hashed version of the password for security reasons. <br>
        >[!CAUTION]
        > Passwords must never be stored as plain text for obvious security reasons, thus the use of the `generate_password_hash` is strongly recommended when storing user passwords
    + `check_password_hash`
        This high level function is used to compare whether a given string password's hash is the same as a pre made hash.
        It takes in a string password and a hash as inputs and returns a boolean value `true` (if the passwords match)  and `false` (if the passwords do not match).
        The return values of this function are especially useful in conditional expressions as demostrated further in this documents.
4. `dotenv`
    this library gives the app access to the `load_dotenv` function. This function is useful for getting environment variables that are hidden in a `.env` file. 
    This function uses the `os` object to get access to the `.env` file. Example usage:
    ```
    load_dotenv()
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    ```
5. `psycopg` & `psycopg.rows`
    psycopg (derived from "Psyco Postgres") is the DBMS (Database Management System). It allows the app to interact with the database by carrying our queries. 
    `pyscopg.rows` allows results of every query to be returned as a list of dicts (where each dict represents a row in the table) as opposed to the default tuples. 
    This choice was especially useful for indexing and iterating through the results of the queries. 
### Key routes
The app currently has 12 routes that all serve very crutial functions. This document will explain the features and functions of some of the most important routes and the design choices behind them.
1. `register`
    This route can be reached via GET and POST http request. <br>
    + via `GET` 
        When accessed via GET, the route returns the `resiter.html` template. This template has a form that has fields through which a user can enter infromation to set up an account. 
    + via `POST`
        This route can be accessed via an http `POST` request when a user fills in the form to register for a new account. The form sends a POST request to the server on this route for processing. 
        Input validation is crutial at this point as it is the information that is entered at this point that will be used for other services going forward. That said, various input validation techniques are used in this route. Some of the key ones include:
        - Use of the `strip()` method from the python standard library to trim whitespace from emails and usernames. This function is especially helpful for ensuring that usernames or emails that that only differ by a railing or leading space are not recognized as different. 
        - Use of `re` object with `match()` method to use check if the entered email is valid. illustrated:
            ```
            # Validate email by using the email regex
        elif re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', email) is None:
            flash("Oops! That email wasn't quite right <br> please enter a valid email")
            return redirect("/register")
            ```
        - Security-wise, this route uses `generate_passsord_hash` to convert passwords to their hashed equivilents before storing into the database. 
2. `make_entry`
    + via `GET`
        When accessed via `GET`, the route simply renders a page with a text area that can allow users to enter their entry and radio buttons to allow them to select a single mood. 
        It is worth noting that the form on the make_entry page is not a traditional form and is submitted via a fetch request on the client side to allow for **encryption** of the entry to take place. 
    + via `POST`
        This route is accessed via this method when a fetch request has been sent from the client with json containing information about the entry that has been made. As such the `request.json()` function is used to get the required fields. 
        This route receives three values from the client
        1. `data['entry']` - The encrypted base64 entry
        2. `data['mood']` - The selected mood
        3. `data['iv']` - The initialization vector obtained when from the encryption algorigthm that is used in the **decryption** of the users's entry. 
        One of the goals of the app is to improve journaling altogether; that means eliminating the amount of data that the user enters when they make a jouranl entry. Particularly, little details such as the time and date the entry was made. That said, the app enters chronological informaion about the entry automanically through a query used to enter this infomation about the user's entry uses server's date and time so that the user does not have to enter this information manually themselves. Illustrated:  
        ```
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
        ```
        As shown in the example, each unit of time (year, month, day, time) is fragmented and singled out to ensure that journal entries are searchable and can be grouped. Further, fields `month`, `date` and `year` are stored as `INTEGER`s to ensure that entries can be arranged based on earliest, latest and other aggregate functions such as `MAX` or `MIN` can be carried out. 
        >[!CAUTION]
        >Considering the fact that the _time_ field is obtained from the server, inaccuracies may arise as the default time-zone used by the server is by default **UTC**. 
        >Future improvements will attempt using time provided by the client's browser using the `Date` javascipt object.
        
        Finally once an entry has been successfully been saved to the database, this route returns a json object that serves as a response to the initial fetch request throught which this route was reached. illustrated:
        ```
        flash("Your entery has been added")
        # Return redirect route after success
        return jsonify({'status': 'success', 'redirect': '/home'})
        ```
        This was in important design choice in that       
