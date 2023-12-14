from flask import Flask,redirect,url_for,render_template,request,session,jsonify
import pymongo
import datetime
from google.oauth2 import service_account
import gspread
from pymongo import MongoClient

app = Flask("__name__")
app.secret_key = "Yukesh"

client = MongoClient("mongodb+srv://yukesh:yukesh@adminusers.xf0watp.mongodb.net/?retryWrites=true&w=majority")
db = client["Admin_data"]
collection = db["Users"]
db1 = client["User_data"]
collection1 = db1["User"]


credentials = service_account.Credentials.from_service_account_file(
    "indian-legal-information-d6444bb36676.json",
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

spreadsheet_id = '13PIYug6gojkWZVuKGMm0A0H22dlKVSOL-WpQg1VRn_Q'
client = gspread.authorize(credentials)
worksheet = client.open_by_key(spreadsheet_id).sheet1


def get_column_names():
    all_data = worksheet.get_all_values()
    header = all_data[0]
    return header

def get_filtered_and_paginated_data(selected_post_name, page, rows_per_page):
    all_data = worksheet.get_all_values()
    header = all_data[0]
    data = all_data[1:]

    if selected_post_name:
        post_name_column_index = header.index('Post Name')
        # Convert both the search term and data to lowercase for case-insensitive comparison
        data = [row for row in data if row[post_name_column_index].lower() == selected_post_name.lower()]

    page = int(page)

    if rows_per_page == 'all':
        paginated_data = data
    else:
        rows_per_page = int(rows_per_page)
        start_row = (page - 1) * rows_per_page
        end_row = start_row + rows_per_page
        paginated_data = data[start_row:end_row]

    return paginated_data


@app.route("/job-post")
def job_post():
    return render_template("User-Jobs.html")

@app.route('/data', methods=['GET'])
def get_data():
    page = int(request.args.get('page', 1))
    selected_post_name = request.args.get('post_name', '')
    rows_per_page = request.args.get('rows_per_page', 20)

    paginated_data = get_filtered_and_paginated_data(selected_post_name, page, rows_per_page)
    total_rows = len(get_filtered_and_paginated_data(selected_post_name, 1, 'all'))

    total_pages = (total_rows + int(rows_per_page) - 1) // int(rows_per_page)

    return jsonify({'data': paginated_data, 'total_pages': total_pages})


# click event code


@app.route('/log_click_event', methods=['POST'])
def log_click_event():
    data = request.get_json()
    data['user_id'] = "Yukesh"
    log_data = {
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'user_token': data['user_token'],
        'event': data['event'],
        'page_type': data['page_type'],
        'product_id': data['product_id'],
        'timestamp': data['timestamp']
    }
    with open('click_logs.txt', 'a') as f:
        f.write(str(log_data) + '\n')

    return jsonify({'message': 'Event logged successfully'})





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

@app.route("/user-login",methods=["POST","GET"])
def user_login():
    if request.method == "POST":
        return render_template("User-Home.html")
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
    app.run(host='0.0.0.0',port=8080,debug=True)