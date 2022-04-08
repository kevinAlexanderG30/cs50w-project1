from select import select
from turtle import title
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from pkg_resources import fixup_namespace_packages
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from api import api1

from helpers import login_required

app = Flask(__name__)

# Check for environment variable
#if not ("postgresql://ffrkfknqbahajw:d84315a7a8fb07644553f98cbd4b1c36db4e4d7a8a78dbe7acc16f4cf8297944@ec2-3-225-213-67.compute-1.amazonaws.com:5432/dc3l910adjg8ve"):
    # raise RuntimeError("DATABASE_URL is not set")

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

@app.route("/libro")
@login_required
def libro():
    return render_template("libro.html")


@app.route("/",methods=["GET", "POST"])
@login_required
def index():
    busquedaLibro = request.args.get("busquedaLibro")

    if not busquedaLibro:
        return render_template("index.html")
        
    busquedaLibro = (f"%{busquedaLibro}%")
        
    resultado = db.execute("SELECT * FROM books WHERE isbn ILIKE :busquedaLibro OR \
        lower(title) ILIKE lower(:busquedaLibro) OR lower(author) ILIKE lower(:busquedaLibro) OR year ILIKE :busquedaLibro order by year desc", 
            {"busquedaLibro": busquedaLibro }).fetchall()
       
    # print(f"{resultado}")

    return render_template("libro.html", resultado=resultado)
    

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
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        # print(f"{rows}")

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
        if not username:
            return render_template("register.html")

        elif not password:
            return render_template("register.html")

        elif password != confirmation:
            return render_template("register.html")


        # Verificamos si el nombre del usuario esta disponible
        consulta = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchall()
        print(f"{consulta}")
        
        if len(consulta) != 0:
            print("Ho0la")
            return render_template("register.html")
        
        print("Hola")
        
        # insertamos al nuevo usuario
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash) RETURNING id",
                            {"username": username, "hash": generate_password_hash(password)}).fetchone()

        db.commit()

       # print("XDD")
        # iniciamos session00000
        print(rows[0])
        session["user_id"] = rows[0]
        # print("Hola1")

        return redirect("/")
    else:
       return render_template("register.html")


@app.route("/paginaDeLibro/<string:isbn>", methods=["GET", "POST"])
def paginaDeLibro(isbn):
    isbn = isbn
    resultado = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
    print(f"{resultado}")

    return render_template("paginaDeLibro.html", resultado=resultado)

@app.route("/api/<string:isbn>", methods=["GET", "POST"])
def api(isbn):
    isbn1 = isbn
    isbn1 = api1(isbn1)
    selector = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchall()
    # print(isbn)
    lista = []

    for i in selector:
        lista.append(list(i))
    print(f"{lista}")
    title = lista[0][2]
    year = lista[0][4]
    isbn = lista[0][1]
    author = lista[0][3]
    average_score = isbn1["items"][0]["volumeInfo"]["averageRating"]
    review_count = isbn1["items"][0]["volumeInfo"]["ratingsCount"]
    #title = isbn["items"][0]["volumeInfo"]["title"]
    #author  = isbn["items"][0]["volumeInfo"]["authors"]
    #year = isbn["items"][0]["volumeInfo"]["authors"]
    # print(title)
    return jsonify({"author": author, "year": year, "isbn": isbn, "title": title, "average_score": average_score, "review_count": review_count })


@app.route("/error")
def error():
    return render_template("403.html")
