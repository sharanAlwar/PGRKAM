from flask import Flask,redirect,url_for,render_template,request,session,jsonify
import pymongo
from datetime import datetime, timezone
from google.oauth2 import service_account
import gspread
from pymongo import MongoClient
import secrets
import os
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from numpy.linalg import norm
import fitz
from oauth2client.service_account import ServiceAccountCredentials

app = Flask("__name__")
app.secret_key = "Yukesh"

client = MongoClient("mongodb+srv://yukesh:yukesh@adminusers.xf0watp.mongodb.net/?retryWrites=true&w=majority")
db = client["Admin_data"]
collection = db["Users"]
db1 = client["User_data"]
collection1 = db1["User"]
collection2 = db1["Click_events"]


credentials = service_account.Credentials.from_service_account_file(
    "indian-legal-information-d6444bb36676.json",
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

spreadsheet_id1 = '1uvKTwUvb-7wHMJpWzuR-o7ll-Ld5vtLLwxcbeUk1Z4Y'
sheet_name = 'Sheet1'  # Replace with the name of your sheet


spreadsheet_id = '13PIYug6gojkWZVuKGMm0A0H22dlKVSOL-WpQg1VRn_Q'
client = gspread.authorize(credentials)
worksheet = client.open_by_key(spreadsheet_id).sheet1


# Set the upload folder and allowed extensions for uploaded files
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



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
        'date': datetime.now().strftime('%Y-%m-%d'),
        'user_token': session["token"],
        'event': data['event'],
        'page_type': data['page_type'],
        'product_id': data['product_id'],
        'timestamp': data['timestamp']
    }
    collection2.insert_one(log_data)
    # with open('click_logs.txt', 'a') as f:
    #     f.write(str(log_data) + '\n')

    return jsonify({'message': 'Event logged successfully'})



@app.route("/", methods=["POST","GET"])
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

@app.route("/user-alerts")
def user_alerts():
    return render_template("Alerts.html")

@app.route("/custom-data")
def custom_data():
    return render_template("Custom.html")

@app.route("/logout")
def logout():
    return redirect(url_for('login'))

@app.route("/user-login",methods=["POST","GET"])
def user_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = collection1.find_one({"fullname": username, "password": password})
        if user:
            # session["token"] = user["_id"]
            session["token"] = user["Token"]
            session["fname"] = username
            log_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'user_token': session["token"],
                'event': "login",
                'page_type': "login-page",
                'product_id': "",
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
             }
            collection2.insert_one(log_data)
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
        user_token = secrets.token_hex(16)
        collection1.insert_one({"Token":user_token,"fullname": username , "password": password,"email": email,"phone":phone ,"dateOfBirth":dateOfBirth ,"gender":gender ,"address": address,"location": location,"educationLevel": educationLevel,"university":university ,"degree":degree ,"major":major ,"graduationYear": graduationYear,"yearsOfExperience":yearsOfExperience ,"previousEmployer": previousEmployer,"preferredJobLocation":preferredJobLocation ,"programmingLanguages": programmingLanguages,"technicalSkills":technicalSkills,"softSkills": softSkills, "bio":bio })
        return redirect(url_for("user_login"))
    return render_template("User-Register.html")


@app.route('/feedback')
def feedback():
    return render_template('User-Feedback.html')


@app.route('/submit', methods=['POST'])
def submit():
    emoji = request.form.get('emoji')
    feedback = request.form.get('comment')
    print(emoji)
    print(feedback)
    username= session["fname"]
    # Authenticate with Google Sheets API
    gc1 = gspread.authorize(credentials)
    print(username)
    # Open the spreadsheet and select the appropriate sheet
    sh1 = gc1.open_by_key(spreadsheet_id1)
    worksheet1 = sh1.worksheet(sheet_name)

    # Append data to the sheet
    worksheet1.append_row([username,emoji, feedback])

    return render_template('User-Feedback.html')


class ResumeMatcher:

    def __init__(self, job_description, resume):
        self.job_description = job_description
        self.resume = resume
        self.set_of_words = set()
        self.vec_job = []
        self.vec_resume = []
        self.score = 0
        self.stop_words = ['I', 'You', 'they', 'is', 'am', 'are', 'a', 'an', 'the', ',', '.', '\'', 'in', 'to']

    def preprocess(self, text):
        text = text.split(" ")
        text = [i for i in text if i not in self.stop_words]
        return text

    def word_map(self):
        self.set_of_words.update(set(self.job_description))
        self.set_of_words.update(set(self.resume))
        self.set_of_words = sorted(self.set_of_words)
        self.set_of_words = dict.fromkeys(self.set_of_words, 0)

    def vectorize(self, text):
        vec = {key: 0 for key in self.set_of_words}
        for word in text:
            vec[word] += 1
        return pd.DataFrame([vec])

    def dot_product(self):
        self.vec_job = self.vec_job.values.flatten(order='C')
        self.vec_resume = self.vec_resume.values.flatten(order='C')
        self.score = np.dot(self.vec_job, self.vec_resume) / (norm(self.vec_job) * norm(self.vec_resume))

    def calculate_similarity(self):
        self.job_description = self.preprocess(self.job_description)
        self.resume = self.preprocess(self.resume)
        self.word_map()
        self.vec_job = self.vectorize(self.job_description)
        self.vec_resume = self.vectorize(self.resume)
        self.dot_product()
        return self.score

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    return text

job_listings_data = [
    {'title': 'Data Analyst', 'description': 'A data analyst is responsible for organizing data related to sales numbers, market research, logistics, linguistics, or other behaviors. They utilize technical expertise to ensure data is accurate and high-quality. Data is then analyzed, designed, and presented in a way that assists individuals, businesses, and organizations make better decisions.Using automated tools to extract data from primary and secondary sourcesRemoving corrupted data and fixing coding errors and related problemsDeveloping and maintaining databases, and data systems – reorganizing data in a readable format Performing analysis to assess the quality and meaning of dataFilter Data by reviewing reports and performance indicators to identify and correct code problemsUsing statistical tools to identify, analyze, and interpret patterns and trends in complex data sets could be helpful for the diagnosis and predictionAssigning numerical value to essential business functions so that business performance can be assessed and compared over periods of time.Analyzing local, national, and global trends that impact both the organization and the industryPreparing reports for the management stating trends, patterns, and predictions using relevant dataWorking with programmers, engineers, and management heads to identify process improvement opportunities, propose system modifications, and devise data governance strategies. Preparing final analysis reports for the stakeholders to understand the data-analysis steps, enabling them to take important decisions based on various facts and trends. Another integral element of the data analyst job description is EDA or Exploratory Data Analysis Project. In such data analyst projects, the analyst needs to scrutinize data to recognize and identify patterns. The next thing data analysts do is use data modeling techniques to summarize the overall features of data analysis'},
    {'title': 'Software Engineer', 'description': 'We are looking for a passionate Software Engineer to design, develop and install software solutions.Software Engineer responsibilities include gathering user requirements, defining system functionality and writing code in various languages, like Java, Ruby on Rails or .NET programming languages (e.g. C++ or JScript.NET.) Our ideal candidates are familiar with the software development life cycle (SDLC) from preliminary system analysis to tests and deployment.Ultimately, the role of the Software Engineer is to build high-quality, innovative and fully performing software that complies with coding standards and technical design.Proven workexperience as a Software Engineer or Software DeveloperExperience designing interactive applicationsAbility to develop software in Java, Ruby on Rails, C++ or other programming languagesExcellent knowledge of relational databases, SQL and ORM technologies (JPA2, Hibernate)Experience developing web applications using at least one popular web framework (JSF, Wicket, GWT, Spring MVC)Experience with test-driven developmentProficiency in software engineering toolsAbility to document requirements and specifications'},
    
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def update_results_google_sheets(job_title, filename, similarity_score):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('indian-legal-information-d6444bb36676.json', scope)

    gc = gspread.authorize(credentials)
    spreadsheet_key = '1n_pTVTb0mzF1IDbensHAuFvE1LCQJw0UVWU1tmd75AI'
    worksheet = gc.open_by_key(spreadsheet_key).get_worksheet(0)

    # Get existing data
    existing_data = worksheet.get_all_records()

    # Prepare data to append
    new_data = {'Name': session["fname"],'Job_Title': job_title, 'Filename': filename, 'Similarity_Score': similarity_score}
    existing_data.append(new_data)

    # Convert dict_keys to list before updating the worksheet
    keys_list = list(new_data.keys())
    values_list = list(new_data.values())
    worksheet.append_rows([values_list], value_input_option='USER_ENTERED')


@app.route('/job_listings', methods=['GET'])
def job_listings():
    return render_template('User-JobListings.html', job_listings_data=job_listings_data, error=None)

@app.route('/submit_resume/<job_title>', methods=['POST'])
def submit_resume(job_title):
    # Check if the post request has the file part
    if 'file' not in request.files:
        return render_template('User-JobListings.html', error='No file part', job_listings_data=job_listings_data)

    file = request.files['file']

    # If the user does not select a file, the browser also submits an empty part without a filename
    if file.filename == '':
        return render_template('User-JobListings.html', error='No selected file', job_listings_data=job_listings_data)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Retrieve the job description for the selected job title
        job_description = next(job['description'] for job in job_listings_data if job['title'] == job_title)

        # Perform ML model
        resume_text = extract_text_from_pdf(file_path)
        matcher = ResumeMatcher(job_description, resume_text)
        similarity_score = matcher.calculate_similarity()

        # Update results to Google Sheets
        update_results_google_sheets(job_title, filename, similarity_score)

    return redirect(url_for('job_listings'))



if __name__=="__main__":
    app.run(host='0.0.0.0',port=8080,debug=True)