# **The Accountable Journal:**

The Accountable Journal is the future of journaling. It was built with one goal <i>make journaling addictive and fun</i>

This document will attempt to breakdown and explain the design choices.
>[!NOTE] 
> This document will refer to "The Accountable Journal" as "the app" for simplicity
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
      # Send success message to the dashboard and redirect to homepage
      flash(f"Welcome, {name} <br>  Your journaling journey awaits🌟!") 
      return redirect("/home")
      ```
    + `session`
      This flask object that allows us to track information about the app. <br>
      This primary information that this object contains is about the user currently interacting with the app. 
      The object contains a key called the user_id `session["user_id"]<br> 
      This key will contain the current user's id which is the unique number assigned to each user when they create an account or when they log in<br>
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
        The return values of this function are especially useful in conditional expressions as demonstrated further in this documents.
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
1. `/register`
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
        - It is also worth noting that the app is designed to have only unique usernames and emails per user. This implies that part of the validation checks involve querying the database for a username or email that the user has entered; If a username/email is found then registration cannot be done. 
        - Security-wise, this route uses `generate_passsord_hash` to convert passwords to their hashed equivilents before storing into the database. 
2. `/make_entry`
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
        >[!NOTE]
        >POST requests sent via a fetch on the client side differ greatly from traditionl POST request sent from form submission. 
        This is is the reason why this route returns json with success status and redirect instructions rather than a traditional `redirect` funciton with a destination. 
3. `/login`
    + This route simply renders an html form with password and username fields when accessed via `GET`. 
    + When accessed via `POST`, The route will confirm that the user exists in the database, and then checks whether the passwords for that user match using `check_password_hash()` function.
4. `/info`
    This is another key route that is essiential for core functionallity. Its role is to simply query the database for all the information (entries) that the current user has, and return it as a json object. It is worth noting that this the return value of the query must be a python list of dicts (where each dict is a single entry information with keys representing field such as time, mood .etc). This is crutial for the client to be able iterate over each of the entries and carry out decryption and rendering efficiently and uniformly on each entry. 
    The return value of this route is conditional in that it requires context due to the rather poor design choice made early in development. 
    + The route returns `info` when a user is logged in and their `id` is set in the `session['user_id']` superglobal object.
    + Other wise, the route returns an empty json object when the homepage is reached and a user is not logged in yet. 
5. `/key`
    The function of this route is to send the crutial encryption key to the client to allow for the decryption of entries to take place.<br>
    It is worth noting that this key must be the right key and must not be tampered with or manipulated at any cost.
6. `/home`
    This is route serves as the users's homepage once they are logged in. This route allows both GET and POST http request methods
    + via `GET`
        The route renders the the _search.jinja2_ template. This serves as the canvas upon which the client renders each of the user's entries. 
        Further, the _search.jinja2_ template that is rendered has an html form (with an action leading to this route) that allows the user to search their entries based on year, date, mood, and month. In order to reduce user input even as they attempt to search their entreis, the app enables the user to simply select from a list of options that the user has.<br> 
        To illustrate, a user who has only made entries in the years 2024 and 2025, in the months july and october, and has moods angry, sad, and happy, Their search options for year, month, and mood will be limited to only to: 
        1. years:  2024, 2025
        2. month: July, October
        3. mood: angry, sad, happy
        This clever design choice was aimed at ensuring that most search queries to the server are successful and to improve the user experience. 
        *How is this achieved?*
        The above coviniece was acheived through a rather complex conditional qeuery construction. 
        _search.jinja2_ template teakes in a list of what the developer calls _"searchables"_ that are simply the options the user has to search from (mood, day, month and year). 
        To bigin with, the very top of this side of the query involves querying the database for these _searchables_ for a user. 
        ```
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
        ```
        The next step is to create empty lists that _jinja_ will use.
        `moods = [], years = [], months = [], days = []`
        Then iterate over each of the dicts in the python list and append each of the related values in their respective lists:
        ```
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
        ```
        As seen in the example above a conditional check is done to ensure that the options are unique. 
        Finally these _searchables_ are passed to the _search.jinja2_ template as select dropdown options for the user to choose from. 
        `return render_template("search.jinja2", moods=moods, years=years, days=days, months=months)`
    + via `POST`
        This route can be reached via this method when a search has been been made. 
        This route user the search parameters passed by the user in the form to conditionally build up a query that will return an entry based on those search parameters.
        A list of parameters is initiated with the `session["user_id"]` as the default value ensuring that the results are unique to that user:
        ```
        # Initialise list of values for placeholders if a searcha parameter is given
        values = [session["user_id"]]
        ```
        >[!IMPORTANT]
        >`psycopg` allows the use of both _list_ s and _tuple_ s to be passed to queries as positional arguments.<br>
        > In this context a _list_ is used due to its **mutable** nature that is, it can be appeneded to as opposed to _tuple_ s which are **immutabel** and thus retain their state.        
        The conditional building of the query and the parameters    through `values` is Illustrated:
        ```
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
        ```
    >[!TIP]
    >PostgresSQL using `psycopg` by default requires positional arguments to be passed t o queries as _tuples_ or _lists_. This is convinient for building conditionally adding filters or search parameters. 
    >SQLite using `db.execute` from `cs50` library on the other hand requires that positional arguments are passed in the more tradional way. While the same code can be used in this context, when finally executing this query, the `*` operater must be used to sort of 'unpack' the filters so that they can be stand alone positional arguments.  

    The final step on this route, is to update the global list `search_results` with the result of the compound query:
    `search_results = results`
    >[!NOTE]
    >Due to the fact that routes that are accessed via `POST` cannot send back json to the client on the same route, the return value of this route is simply the _search\_results.jinja2_ template.
7. `/results`
    This is the route that is responsible for sending search results to the client via a simple fetch API. 
    It can only able reached via `GET`. It converts the global list (`search_results`) containing the entries as dicts. 
    Note that the `search_results` global is initially an empy list and is updated by the `/home` route when a user makes an entry. 
8. `/stats`
    The function of this route is to collect statistical information about the user to serve as analytics. The stats collected by this route are:
    + `moods` - distinct moods that the user has ever entered
    + `times` - the number of times that each mood occurs
    + `longest_entry`- the longest entry in terms of length
    The `moods` and `times` are especially important and must be in alignment in terms of index as they are used by JavaScript to display this data into a nice piechart using the _chart.js_ library.
    The above is achieved through querying for the moods and the number of times each of those moods occur. This is easily achieved using SQL:
    ```
    with conn.cursor() as cur:
        cur.execute("""
                SELECT mood, COUNT(mood) AS times 
                FROM entries
                WHERE author_id = %s
                GROUP BY mood""", (session["user_id"],)
        )
        information = cur.fetchall()
    ```
    Thereafter, the stats json object is then appended with the appropriate lists:
    ```
    stats = {"moods": [], "times": [], "longest_entry": []}
    for info in information:
        stats["moods"].append(info["mood"])
        stats["times"].append(info["times"])
    ```
    Finding the longest entry follows, SQL built in functionality makes this easy using `LENGTH` function that can return an integer lengthe of a column of type `TEXT`:
    ```
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
    ```
    The above nested query returns information about the entry with the highest word count. 
    Finally, the `stats` json object with the requierd field is sent to the client via a simple fetch API. 
## **script.js** - Client-Side Orchestrator

This JavaScript file handles all client-side functionality including encryption/decryption, dynamic rendering, and user interactions. The code is wrapped in a `DOMContentLoaded` event listener to ensure execution only after the DOM is fully loaded.

### Core Utility Functions

1. **Date & Formatting Helpers**
   ```
   function getStringDate(month)
   function ordinalIndicator(date)
   ```
    + Converts numeric months (1-12) to human-readable strings
    + Adds proper ordinal suffixes (st, nd, rd, th) to dates
    + Essential for consistent date display across the application

2. **Visual Styling**
    `function getBGcolor(mood)`
    Returns mood-specific background colors for entry cards
    + Angry - bright red #f40a04 
    + Happy - bright Yellow #fff200
    + Sad - Sad deep blue #5c6bc0
    + Calm - Tourqouise #47ffeb
    + Anxious - Light pink #ef8a8a
    + Lonely - Pale violet #ce83d8
    + Confident - Light blue #0fb4FA
    + Meh - Pale gray #858585
    + Hopeful - Orange #ff6f02
    + Tired - Bluish gray #90a4ae
    + Greateful - Olive green #aeee23
    + Inspired - Deep purpule #c71585
    Uses a vibrant color palette to create visual emotional mapping
    Defaults to white for undefined moods, Which may never happen give the robustness of the system. 

3. **Cryptography Functions**
```
function base64ToBytes(base64string)
function bytesTobase64(buffer)
async function decryptEntry(cipherEntry, iv)
```
Handles conversion between Base64 and byte arrays
Implements AES-GCM decryption using Web Crypto API
Works with server-provided encryption key for end-to-end encryption

### Key Functionality
1. **Entry Rendering System**
```
async function renderEntries(entries, id)
```
Dynamically generates entry cards with:
+ Formatted dates/times
+ Decrypted content
+ Mood-specific styling

2. **Delete functionality**
+ Implements a placeholder loading pattern for better UX
+ Handles empty state gracefully by rendring an image with a link

3. **Encryption Workflow** 
+ Retrieves encryption key from /key endpoint
+ Prepares key for client-side crypto operations
+ Encrypts entries before submission with:

Random initialization vector (IV)

AES-GCM algorithm

Base64 encoding for transmission

4. **Form Handling**
+ Validates journal entries (requires both text and mood selection)
+ Calculates word count during composition
+ Handles submission via fetch API to /make_entry

5. **Data Management**
+ Fetches entries from /info endpoint
+ Processes search results from /results
+ Implements entry deletion with confirmation

### Statistical Visualization
```
// Chart.js Configuration
const config = {
    type: 'doughnut',
    data: { /* ... */ },
    options: { /* ... */ }
}
```
+ Generates interactive mood distribution charts
+ Dynamically colors chart segments using getBGcolor()
+ Displays key metrics:
    1. Total entry count
    2. Most common mood
    3. Longest entry (word count)

### Error Handling
+ Comprehensive try-catch blocks throughout
+ Graceful degradation for:
    1. Missing DOM elements
    2. Empty data states
    3. Cryptographic operations

Security Notes
>[!CAUTION]

>Encryption keys are never stored in client-side code
>All journal entries are encrypted before transmission
>IVs are generated fresh for each entry
>Cryptographic operations use Web Crypto API (browser-native)

Performance Considerations
1570ms delay for placeholder animation

Batch DOM updates to minimize reflows

Efficient query selectors

Async/await pattern for non-blocking operations

Future Improvements
Client-side timezone handling for entries

Animation optimization

Progressive enhancement for older browsers

Additional mood color mappings
