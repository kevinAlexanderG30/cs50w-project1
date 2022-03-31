from flask import Flask, session, redirect, render_template, request
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://ffrkfknqbahajw:d84315a7a8fb07644553f98cbd4b1c36db4e4d7a8a78dbe7acc16f4cf8297944@ec2-3-225-213-67.compute-1.amazonaws.com:5432/dc3l910adjg8ve")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # verificamos si el usuario nuevo ingreso en algo en los campos correspondientes
        if not username:
            return render_template("register.html")

        elif not password:
            return render_template("register.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmation = request.form.get("confirmation").strip()

        # verificamos si el usuario nuevo ingreso en algo en los campos correspondientes
        if not request.form.get("username"):
            return render_template("register.html")

        elif not request.form.get("password"):
            return render_template("register.html")

        elif password != confirmation:
            return render_template("register.html")


        # Verificamos si el nombre del usuario esta disponible
        if db.execute("SELECT username FROM users WHERE username = :username", username=username):
            return render_template("register.html")

        # insertamos al nuevo usuario
        rows = db.execute("INSERT INTO users(username, hash) VALUES (:username, :hash)",
                          username=username, hash=generate_password_hash(password))

        # iniciamos session
        session["user_id"] = rows

        return redirect("/")
    else:
       return render_template("register.html")

@app.route("/error")
def error():
    return render_template("403.html")