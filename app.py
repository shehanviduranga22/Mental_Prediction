#pip install numpy pandas scikit-learn nltk tensorflow flask mysql-connector-python matplotlib 

import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, jsonify, url_for
from helper import preprocessing, vectorizer, get_prediction
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError

app = Flask(__name__)
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "mindmirror-development-key")

mongo_uri = os.environ.get("MONGODB_URI")
mongo_client = MongoClient(
    mongo_uri,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
) if mongo_uri else None
accounts = mongo_client["mindmirror"]["accounts"] if mongo_client else None

@app.route("/")
def index():
    return render_template(
        "index.html",
        account_error=request.args.get("account_error"),
        account_message=request.args.get("account_message"),
        login_error=request.args.get("login_error")
    )

@app.route("/login")
def login():
    return redirect(url_for("index") + "#login")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/account")
def account():
    return redirect(url_for("index") + "#register")

@app.route("/error")
def error():
    return render_template("error.html")

@app.route('/predict', methods=['POST'])
def predict():
    text = request.form['search']
    preprocessed_txt = preprocessing(text)
    vectorized_txt = vectorizer(preprocessed_txt)
    prediction, instruction = get_prediction(vectorized_txt)
    
    return jsonify({
        "prediction": prediction,
        "instruction": instruction
    })

@app.route("/accountCreate", methods=["POST"])
def signup():
    username = request.form["loginUserName"]
    email = request.form["loginEmail"]
    password = request.form["loginPassword"]

    if username=="" or email=="" or password=="":
        return redirect(url_for("index", account_error="Please fill in all fields.") + "#register")

    if accounts is None:
        return redirect(url_for("index", account_error="MongoDB is not configured. Set MONGODB_URI first.") + "#register"), 503

    try:
        accounts.create_index("userName", unique=True)
        accounts.insert_one({
            "userName": username,
            "email": email,
            "userPassword": generate_password_hash(password)
        })
    except DuplicateKeyError:
        return redirect(url_for("index", account_error="That username already exists.")+ "#register")
    except OperationFailure as error:
        message = "MongoDB authentication failed. Check the Atlas username and URL-encoded password." if "auth" in str(error).lower() else "MongoDB rejected the account request."
        return redirect(url_for("index", account_error=message) + "#register"), 503
    except PyMongoError:
        return redirect(url_for("index", account_error="Unable to save the account right now.") + "#register"), 503

    return redirect(url_for("index", account_message="Account created successfully.") + "#login")

    

@app.route("/newlogin", methods=["POST"])
def newlogin():
    userName = request.form["loginUserName"]
    password = request.form["loginPassword"]

    if accounts is None:
        return redirect(url_for("index", login_error="MongoDB is not configured. Set MONGODB_URI first.") + "#login"), 503

    try:
        user = accounts.find_one({"userName": userName})
    except OperationFailure as error:
        message = "MongoDB authentication failed. Check the Atlas username and URL-encoded password." if "auth" in str(error).lower() else "MongoDB rejected the login request."
        return redirect(url_for("index", login_error=message) + "#login"), 503
    except PyMongoError:
        return redirect(url_for("index", login_error="Unable to connect to the account database.") + "#login"), 503

    stored_password = user.get("userPassword", "") if user else ""
    valid_password = check_password_hash(stored_password, password) if stored_password.startswith(("scrypt:", "pbkdf2:")) else stored_password == password

    if user and valid_password:
        return render_template("index.html", user=userName)

    return redirect(url_for("index", login_error="Invalid username or password.") + "#login")

   


if __name__ == "__main__":
    app.run(debug=True)

