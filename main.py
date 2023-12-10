from flask import Flask,redirect,url_for,render_template,request,session
import pymongo
from pymongo import MongoClient

app = Flask("__name__")
app.secret_key = "Yukesh"

client = MongoClient("mongodb+srv://yukesh:yukesh@adminusers.xf0watp.mongodb.net/?retryWrites=true&w=majority")
db = client["Admin_data"]
collection = db["Users"]
db1 = client["User_data"]
collection1 = db1["User"]

@app.route("/admin")
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        name = request.form["userName"]
        password = request.form["password"]
        user = collection.find_one({"name": name, "password": password})
        if user:
            session["username"] = name
            return redirect(url_for('dashboard'))
    return render_template('Login.html')

@app.route("/dashboard")
def dashboard():
    return render_template("Home.html")

@app.route("/logout")
def logout():
    return redirect(url_for('login'))

@app.route("/user-login")
def user_login():
    return render_template("User-Login.html")

@app.route("/user-register",methods=["POST","GET"])
def user_register():
    if request.method == "POST":
        username = request.form["fullName"]
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]
        dateOfBirth = request.form["dateOfBirth"]
        gender = request.form["gender"]
        address = request.form["address"]
        location = request.form["location"]
        educationLevel = request.form["educationLevel"]
        university = request.form["university"]
        degree = request.form["degree"]
        major = request.form["major"]
        graduationYear = request.form["graduationYear"]
        yearsOfExperience = request.form["yearsOfExperience"]
        previousEmployer = request.form["previousEmployer"]
        preferredJobLocation = request.form["preferredJobLocation"]
        programmingLanguages = request.form["programmingLanguages"]
        technicalSkills = request.form["technicalSkills"]
        softSkills = request.form["softSkills"]
        bio = request.form["bio"]
        collection1.insert_one({"fullname": username , "password": password,"email": email,"phone":phone ,"dateOfBirth":dateOfBirth ,"gender":gender ,"address": address,"location": location,"educationLevel": educationLevel,"university":university ,"degree":degree ,"major":major ,"graduationYear": graduationYear,"yearsOfExperience":yearsOfExperience ,"previousEmployer": previousEmployer,"preferredJobLocation":preferredJobLocation ,"programmingLanguages": programmingLanguages,"technicalSkills":technicalSkills,"softSkills": softSkills, "bio":bio })
        return "SUbmitted form"
    return render_template("User-Register.html")

if __name__=="__main__":
    app.run(debug=True)