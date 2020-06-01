import os
import requests
from flask import Flask, session,jsonify,render_template,request,redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['JSON_SORT_KEYS'] = False

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("Login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/fetchallusers")
def fetchallusers():
    users = db.execute("SELECT userid, user_first_last_name, username,user_password FROM users").fetchall()
    return render_template("allusers.html", users=users)

@app.route("/search",methods=["POST"])
def search():
    un = request.form.get("un")
    password = request.form.get("password")
    users = db.execute("SELECT username,user_password FROM users").fetchall()
    if db.execute("SELECT * FROM users WHERE username = :username and " +
                    "user_password=user_password", {"username": un,"user_password":password}).rowcount != 0:
                    session["user_name"] = un
                    return render_template("search.html" , username = session["user_name"])

    return render_template("Login.html")

@app.route("/after_register",methods=["POST"])
def after_register():
    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")

    if db.execute("SELECT * FROM users WHERE username = :username and " +
                    "user_password=user_password", {"username": username,"user_password":password}).rowcount != 0:
                    return "user already exist"

    db.execute("insert into users values(nextval('users_userid_seq'),'"+ name + "','" + username + "','"+password+"')")
    db.commit()
    session["user_name"] = username
    return render_template("search.html",username=username)

@app.route("/logout")
def logout():
    session["user_name"] = None
    return render_template("login.html")

@app.route("/serachbook")
def searchbook():
    # the search is allowed only when user is looged in
    if session["user_name"] is None:
        return "Please Login to continue <a href='/'>Login here</a>"

    # get seach parameter from foem
    isbn1   = request.args.get("isbn")
    author1 = request.args.get("author")
    tittle1 = request.args.get("tittle")
    books = []

    if tittle1 is None or tittle1 == "":
        tittle1 = "xxxxxxxxx"
    if author1 is None or author1 == "":
        author1 = "xxxxxxxx"
    if isbn1 is None or isbn1 == "":
        isbn1 = "xxxxxxxxx"

    books = db.execute("select isbn , author , title ,year from books where title ILike '%"+tittle1+"%' or author ILike '%"+author1+"%' or isbn ILike '%"+isbn1+"%'").fetchall()

    if len(books)>0:
        return render_template("serachbook.html",books=books,username = session["user_name"],numResullts=len(books))
    else :
        return "Book not found"

@app.route("/bookdetails/<string:isbn>")
def book_details(isbn):

    # removing leading and trailing spaces
    isbn = isbn.strip()

    # Good read API call
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "yM7UXmuNKO35yw4vO93TA", "isbns": isbn})
    if res.status_code != 200:
        raise Exception(f"ERROR: API request unsuccessful, Status code return = {res.status_code}")

    # converting response into json
    data = res.json()

    # we only need total ratings and average rating
    work_ratings_count = data["books"][0]["work_ratings_count"]
    average_rating =  data["books"][0]["average_rating"]

    # Fetching other book details from our database
    book_det = db.execute("select isbn , author , title ,year from books where isbn='"+isbn+"'").fetchone()
    book_rev = db.execute("select username , rating, review_text from reviews where isbn = :isbn",
                {"isbn":isbn}).fetchall()
    book_allow_rev = True
    # one user can review books only once.
    if db.execute("select username from reviews where username = :username and  isbn = :isbn",
                    { "username":session["user_name"] , "isbn":isbn}).rowcount >  0 :
                    book_allow_rev = False
            
    return render_template("book_detail.html",book_det=book_det,username = session["user_name"],
                                book_rev=book_rev,book_allow_rev=book_allow_rev,work_ratings_count=work_ratings_count,average_rating=average_rating)

@app.route("/bookdetails/submit_review/")
def submit_review():
    user_name = session["user_name"]
    rating = request.args.get("rating")
    review_text = request.args.get("review_text")
    isbn = request.args.get("isbn")

    review_present =  db.execute("select isbn from reviews where username = :user_name",
                            {"user_name":user_name}).fetchone()
    if review_present is not None:
        return "you have already submited the review"

    else:
        db.execute("INSERT INTO reviews (username, rating,review_text,isbn) VALUES (:user_name, :rating, :review_text , :isbn)",
            {"user_name":user_name , "rating": rating , "review_text":review_text,"isbn":isbn})
        db.commit()
        return redirect(f"/bookdetails/{ isbn }")

@app.route("/bookdetails/edit/<string:isbn>/<string:username>")
def edit(isbn,username):
    review_details =  db.execute("select rating, review_text, isbn from reviews where isbn=:isbn and username=:username",{"isbn":isbn,"username":username}).fetchone()
    return render_template("editReview.html",username=username,review_details = review_details)

@app.route("/edit_review")
def edit_review():
    user_name = session["user_name"]
    rating = request.args.get("rating")
    review_text = request.args.get("review_text")
    isbn = request.args.get("isbn")

    #update review
    db.execute("update reviews set review_text = :review_text, rating = :rating where username = :username " +
                    "and isbn = :isbn",{"review_text":review_text , "rating":rating ,"username":user_name ,"isbn" : isbn })
    db.commit()
    return redirect(f"/bookdetails/{ isbn }")

@app.route("/bookdetails/delete/<string:isbn>/<string:username>")
def delete(isbn,username):


    #delete review
    db.execute("delete from reviews where isbn =:isbn and username =:username",{"isbn":isbn, "username":username})

    #commit
    db.commit()
    return redirect(f"/bookdetails/{ isbn }")

@app.route("/api/<string:isbn>")
def api_isbn(isbn):

    #make sure book exits
    book = db.execute("select isbn , author , title ,year from books where isbn=:isbn",{"isbn":isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 422

    # Good read API call
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "yM7UXmuNKO35yw4vO93TA", "isbns": isbn})

    # check whether the call to api is successful or not
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    # converting response into json
    data = res.json()

    # we only need total work review count and average rating
    work_reviews_count = data["books"][0]["work_reviews_count"]
    average_rating =  data["books"][0]["average_rating"]

    # returning a json respond to the caller
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": isbn,
        "review_count": work_reviews_count,
        "average_score": average_rating
        })

@app.route("/layout")
def layout():
    return render_template("layout.html")
