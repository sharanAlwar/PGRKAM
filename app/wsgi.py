from flask import Flask,redirect,url_for,render_template,request,session,jsonify,flash
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
from email.message import EmailMessage
import smtplib
import time
from google.oauth2 import service_account
import googleapiclient.discovery
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

app = Flask("__name__")
app.secret_key = "Yukesh"

client = MongoClient("mongodb+srv://yukesh:yukesh@adminusers.xf0watp.mongodb.net/?retryWrites=true&w=majority")
db = client["Admin_data"]
collection = db["Users"]
db1 = client["User_data"]
collection1 = db1["User"]
collection2 = db1["Click_events"]

login_attempts = 0
locked_out = False
lockout_start_time = 0
LOCKOUT_DURATION = 120


credentials = service_account.Credentials.from_service_account_file(
    "indian-legal-information-d6444bb36676.json",
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

spreadsheet_id1 = '1uvKTwUvb-7wHMJpWzuR-o7ll-Ld5vtLLwxcbeUk1Z4Y'
sheet_name = 'Sheet1' 


spreadsheet_id = '13PIYug6gojkWZVuKGMm0A0H22dlKVSOL-WpQg1VRn_Q'
client = gspread.authorize(credentials)
worksheet = client.open_by_key(spreadsheet_id).sheet1

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
    return render_template("User-Jobs.html",uname = session["fname"])

@app.route('/data', methods=['GET'])
def get_data():
    page = int(request.args.get('page', 1))
    selected_post_name = request.args.get('post_name', '')
    rows_per_page = request.args.get('rows_per_page', 20)

    paginated_data = get_filtered_and_paginated_data(selected_post_name, page, rows_per_page)
    total_rows = len(get_filtered_and_paginated_data(selected_post_name, 1, 'all'))

    total_pages = (total_rows + int(rows_per_page) - 1) // int(rows_per_page)

    return jsonify({'data': paginated_data, 'total_pages': total_pages})


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



@app.route("/admin", methods=["POST","GET"])
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

# @app.route("/user-login",methods=["POST","GET"])
# def user_login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         user = collection1.find_one({"fullname": username, "password": password})
#         if user:
#             # session["token"] = user["_id"]
#             session["token"] = user["Token"]
#             session["fname"] = username
#             log_data = {
#                 'date': datetime.now().strftime('%Y-%m-%d'),
#                 'user_token': session["token"],
#                 'event': "login",
#                 'page_type': "login-page",
#                 'product_id': "",
#                 'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
#              }
#             collection2.insert_one(log_data)
#             return redirect(url_for('job_post'))
#     return render_template("User-Login.html")


@app.route("/",methods=["POST","GET"])
def user_login():
    global login_attempts
    global locked_out
    global lockout_start_time

    if locked_out:
        current_time = time.time()
        if current_time - lockout_start_time >= LOCKOUT_DURATION:
            locked_out = False
            login_attempts = 0
            lockout_start_time = 0
        else:
            
            flash(f"Unable to log in. Please wait {int(lockout_start_time + LOCKOUT_DURATION - current_time)} seconds.")
            return render_template('User-Login.html')

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = collection1.find_one({"fullname": username, "password": password})
        if user:
            # session["token"] = user["_id"]
            login_attempts = 0
            session["token"] = user["Token"]
            session["fname"] = username
            session["num"] = user["Index"]
            log_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'user_token': session["token"],
                'event': "login",
                'page_type': "login-page",
                'product_id': "",
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
             }
            collection2.insert_one(log_data)
            return redirect(url_for('job_post'))
        else:
            login_attempts += 1

            if login_attempts >= 2:
                locked_out = True
                lockout_start_time = time.time()
                user1 = collection1.find_one({"fullname": username})
                sender_email = 'optimizeprime007@gmail.com'
                sender_password = 'qtohvqsovpjpptzk'
                receiver_email = user1["email"]
                # task_description = data['task_description']
                print(receiver_email)
                em = EmailMessage()
                em['From'] = sender_email
                em['To'] = receiver_email
                em['Subject'] = 'Login Failed'
                em.set_content(f"Your Login has failed multiple times. You have locked out temporarily")

                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, em.as_string())
                server.quit()
    return render_template("User-Login.html")


# @app.route("/user-register",methods=["POST","GET"])
# def user_register():
#     if request.method == "POST":
#         username = request.form["fullName"]
#         password = request.form["password"]
#         email = request.form["email"]
#         phone = request.form["phone"]
#         dateOfBirth = request.form["dateOfBirth"]
#         gender = request.form["gender"]
#         address = request.form["address"]
#         location = request.form["location"]
#         educationLevel = request.form["educationLevel"]
#         university = request.form["university"]
#         degree = request.form["degree"]
#         major = request.form["major"]
#         graduationYear = request.form["graduationYear"]
#         yearsOfExperience = request.form["yearsOfExperience"]
#         previousEmployer = request.form["previousEmployer"]
#         preferredJobLocation = request.form["preferredJobLocation"]
#         programmingLanguages = request.form["programmingLanguages"]
#         technicalSkills = request.form["technicalSkills"]
#         softSkills = request.form["softSkills"]
#         bio = request.form["bio"]
#         user_token = secrets.token_hex(16)
#         collection1.insert_one({"Token":user_token,"fullname": username , "password": password,"email": email,"phone":phone ,"dateOfBirth":dateOfBirth ,"gender":gender ,"address": address,"location": location,"educationLevel": educationLevel,"university":university ,"degree":degree ,"major":major ,"graduationYear": graduationYear,"yearsOfExperience":yearsOfExperience ,"previousEmployer": previousEmployer,"preferredJobLocation":preferredJobLocation ,"programmingLanguages": programmingLanguages,"technicalSkills":technicalSkills,"softSkills": softSkills, "bio":bio })
#         return redirect(url_for("user_login"))
#     return render_template("User-Register.html")
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
        adsource = request.form["adsource"]
        user_token = secrets.token_hex(16)
        # db1.collection2.findOne({}, {sort:{$natural:-1}})
        last_inserted_document = collection1.find_one(sort=[("_id", pymongo.DESCENDING)])
        collection1.insert_one({"Token":user_token,"fullname": username , "password": password,"email": email,"phone":phone ,"dateOfBirth":dateOfBirth ,"gender":gender ,"address": address,"location": location,"educationLevel": educationLevel,"university":university ,"degree":degree ,"major":major ,"graduationYear": graduationYear,"yearsOfExperience":yearsOfExperience ,"previousEmployer": previousEmployer,"preferredJobLocation":preferredJobLocation ,"programmingLanguages": programmingLanguages,"technicalSkills":technicalSkills,"softSkills": softSkills, "bio":bio ,"Source":adsource , "Index": (last_inserted_document["index"]+1)})
        return redirect(url_for("user_login"))
    return render_template("User-Register.html")


@app.route('/feedback')
def feedback():
    # fname = session["name"]
    return render_template('User-Feedback.html',uname = session["fname"])


@app.route('/submit', methods=['POST'])
def submit():
    import pandas as pd
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

    nltk.download('punkt')
    nltk.download('stopwords')
    emoji = request.form.get('emoji')
    feedback = request.form.get('comment')
    print(emoji)
    print(feedback)
    username= session["fname"]

    gc1 = gspread.authorize(credentials)
    print(username)

    sh1 = gc1.open_by_key(spreadsheet_id1)
    worksheet1 = sh1.worksheet(sheet_name)

    worksheet1.append_row([username,emoji, feedback])

    worksheet = gc1.open_by_key(spreadsheet_id1).sheet1  # You can replace 'sheet1' with the name of your specific worksheet

    all_values = worksheet.get_all_values()

    df = pd.DataFrame(all_values[1:], columns=all_values[0])
    column_name = "Comment"
    regex_pattern = "[^a-zA-Z0-9, ']"

    df[column_name] = df[column_name].replace(regex_pattern, '', regex=True)
    df['Comment'].fillna('', inplace=True)
    df['preprocessed_comment'] = df['Comment'].str.lower().replace(r'[^\w\s]', '', regex=True)

    df['comment_tokens'] = df['preprocessed_comment'].apply(word_tokenize)

    stop_words = set(stopwords.words('english'))
    df['filtered_comment_tokens'] = df['comment_tokens'].apply(lambda tokens: [word for word in tokens if word not in stop_words])
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    import pandas as pd

    sid = SentimentIntensityAnalyzer()
    df['comment_sentiment_score'] = df['preprocessed_comment'].apply(lambda x: sid.polarity_scores(x)['compound'])
    df['emoji_score'] = 0.0
    df.loc[df['Emoji'] == 'Sad', 'emoji_score'] = -1.0
    df.loc[df['Emoji'] == 'Happy', 'emoji_score'] = 1.0
    df.loc[df['Emoji'] == 'Neutral', 'emoji_score'] = 0.0
    df['combined_sentiment_score'] = (df['comment_sentiment_score'] + df['emoji_score']) / 2
    df['sentiment'] = df['combined_sentiment_score'].apply(lambda x: 'Positive' if x > 0 else 'Negative' if x < 0 else 'Neutral')
    df=df[['Username','Emoji','Comment','comment_sentiment_score','emoji_score','combined_sentiment_score','sentiment']]
    from oauth2client.service_account import ServiceAccountCredentials
    import pandas as pd

    # Assuming df is your pandas DataFrame
    # Replace 'indian-legal-information-d6444bb36676.json' with your actual JSON key file
    

    
    worksheet_index = 1  # Replace with the index of the worksheet you want to update

    # Open the worksheet
    worksheet = gc1.open_by_key(spreadsheet_id1).get_worksheet(worksheet_index)

    # Prepare data for update
    data_to_update = df.values.tolist()

    # Clear existing data in the worksheet
    worksheet.clear()

    # Update the worksheet
    worksheet.update([df.columns.values.tolist()] + data_to_update)


    return render_template('User-Feedback.html')


# class ResumeMatcher:

#     def __init__(self, job_description, resume):
#         self.job_description = job_description
#         self.resume = resume
#         self.set_of_words = set()
#         self.vec_job = []
#         self.vec_resume = []
#         self.score = 0
#         self.stop_words = ['I', 'You', 'they', 'is', 'am', 'are', 'a', 'an', 'the', ',', '.', '\'', 'in', 'to']

#     def preprocess(self, text):
#         text = text.split(" ")
#         text = [i for i in text if i not in self.stop_words]
#         return text

#     def word_map(self):
#         self.set_of_words.update(set(self.job_description))
#         self.set_of_words.update(set(self.resume))
#         self.set_of_words = sorted(self.set_of_words)
#         self.set_of_words = dict.fromkeys(self.set_of_words, 0)

#     def vectorize(self, text):
#         vec = {key: 0 for key in self.set_of_words}
#         for word in text:
#             vec[word] += 1
#         return pd.DataFrame([vec])

#     def dot_product(self):
#         self.vec_job = self.vec_job.values.flatten(order='C')
#         self.vec_resume = self.vec_resume.values.flatten(order='C')
#         self.score = np.dot(self.vec_job, self.vec_resume) / (norm(self.vec_job) * norm(self.vec_resume))

#     def calculate_similarity(self):
#         self.job_description = self.preprocess(self.job_description)
#         self.resume = self.preprocess(self.resume)
#         self.word_map()
#         self.vec_job = self.vectorize(self.job_description)
#         self.vec_resume = self.vectorize(self.resume)
#         self.dot_product()
#         return self.score

# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page_num in range(doc.page_count):
#         page = doc[page_num]
#         text += page.get_text()
#     return text

# job_listings_data = [
#     {'title': 'Data Analyst', 'description': 'A data analyst is responsible for organizing data related to sales numbers, market research, logistics, linguistics, or other behaviors. They utilize technical expertise to ensure data is accurate and high-quality. Data is then analyzed, designed, and presented in a way that assists individuals, businesses, and organizations make better decisions.Using automated tools to extract data from primary and secondary sourcesRemoving corrupted data and fixing coding errors and related problemsDeveloping and maintaining databases, and data systems – reorganizing data in a readable format Performing analysis to assess the quality and meaning of dataFilter Data by reviewing reports and performance indicators to identify and correct code problemsUsing statistical tools to identify, analyze, and interpret patterns and trends in complex data sets could be helpful for the diagnosis and predictionAssigning numerical value to essential business functions so that business performance can be assessed and compared over periods of time.Analyzing local, national, and global trends that impact both the organization and the industryPreparing reports for the management stating trends, patterns, and predictions using relevant dataWorking with programmers, engineers, and management heads to identify process improvement opportunities, propose system modifications, and devise data governance strategies. Preparing final analysis reports for the stakeholders to understand the data-analysis steps, enabling them to take important decisions based on various facts and trends. Another integral element of the data analyst job description is EDA or Exploratory Data Analysis Project. In such data analyst projects, the analyst needs to scrutinize data to recognize and identify patterns. The next thing data analysts do is use data modeling techniques to summarize the overall features of data analysis'},
#     {'title': 'Software Engineer', 'description': 'We are looking for a passionate Software Engineer to design, develop and install software solutions.Software Engineer responsibilities include gathering user requirements, defining system functionality and writing code in various languages, like Java, Ruby on Rails or .NET programming languages (e.g. C++ or JScript.NET.) Our ideal candidates are familiar with the software development life cycle (SDLC) from preliminary system analysis to tests and deployment.Ultimately, the role of the Software Engineer is to build high-quality, innovative and fully performing software that complies with coding standards and technical design.Proven workexperience as a Software Engineer or Software DeveloperExperience designing interactive applicationsAbility to develop software in Java, Ruby on Rails, C++ or other programming languagesExcellent knowledge of relational databases, SQL and ORM technologies (JPA2, Hibernate)Experience developing web applications using at least one popular web framework (JSF, Wicket, GWT, Spring MVC)Experience with test-driven developmentProficiency in software engineering toolsAbility to document requirements and specifications'},
    
# ]

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# def update_results_google_sheets(job_title, filename, similarity_score):
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     credentials = ServiceAccountCredentials.from_json_keyfile_name('indian-legal-information-d6444bb36676.json', scope)

#     gc = gspread.authorize(credentials)
#     spreadsheet_key = '1n_pTVTb0mzF1IDbensHAuFvE1LCQJw0UVWU1tmd75AI'
#     worksheet = gc.open_by_key(spreadsheet_key).get_worksheet(0)

#     existing_data = worksheet.get_all_records()

#     new_data = {'Name': session["fname"],'Job_Title': job_title, 'Filename': filename, 'Similarity_Score': similarity_score}
#     existing_data.append(new_data)

#     keys_list = list(new_data.keys())
#     values_list = list(new_data.values())
#     worksheet.append_rows([values_list], value_input_option='USER_ENTERED')

# @app.route("/job-s")
# def job_s():
#     return render_template("User_j.html")

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


def send_email(to, subject, body,filename=None, attachment_content=None):

    sender_email = 'optimizeprime007@gmail.com'
    sender_password = 'qtohvqsovpjpptzk'
    print(to)
    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = to
    em['Subject'] = subject
    em.set_content(body)
    if filename and attachment_content:
        em.add_attachment(attachment_content, maintype='application', subtype='pdf', filename=filename)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to, em.as_string())
    server.quit()


def update_results_google_sheets_and_send_email(job_title, filename, similarity_score, email):
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('indian-legal-information-d6444bb36676.json', scope)

    gc = gspread.authorize(credentials)
    spreadsheet_key = '1n_pTVTb0mzF1IDbensHAuFvE1LCQJw0UVWU1tmd75AI'
    worksheet = gc.open_by_key(spreadsheet_key).get_worksheet(0)

    
    existing_data = worksheet.get_all_records()

    
    new_data = {'Job_Title': job_title, 'Filename': filename, 'Similarity_Score': similarity_score}
    existing_data.append(new_data)
    
    keys_list = list(new_data.keys())
    values_list = list(new_data.values())
    worksheet.append_rows([values_list], value_input_option='USER_ENTERED')

    subject = f"Application for {job_title}"
    body = f"You have received resume for the position of {job_title}.\n\nSimilarity Score: {similarity_score}"

    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as content_file:
        content = content_file.read()

    send_email(email, subject, body, filename, content)
    


@app.route('/job_listings', methods=['GET'])
def job_listings():
    return render_template('User-JobListings.html', job_listings_data=job_listings_data, error=None)

@app.route('/submit_resume/<job_title>', methods=['POST'])
def submit_resume(job_title):
   
    if 'file' not in request.files:
        return render_template('User-JobListings.html', error='No file part', job_listings_data=job_listings_data)

    file = request.files['file']

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

        # Update results to Google Sheets and send email
        update_results_google_sheets_and_send_email(job_title, filename, similarity_score*100, 'rmsubramanian2@gmail.com')

    return redirect(url_for('job_listings'))


@app.route("/job-suggest")
def job_suggest():
    SPREADSHEET_ID = '14P045y2lkW2Ommab7R9ZVUY6P1ELMG-WtVNqfmOhENM'

    credentials = service_account.Credentials.from_service_account_file(
        "indian-legal-information-d6444bb36676.json",
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )


    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

    range_name = f'K:U'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = result.get('values', [])


    if not values:
        return 'No data found.'

    index = session["num"]
    # Assuming the index is the first column (column A)
    data_for_index = [rows for rows in values if rows and rows[0].isdigit() and int(rows[0]) == index]

    # print(type(data_for_index[0]))

    return render_template('User-Suggestions.html', index=index, data=data_for_index)
    # return render_template("User-Suggestions.html")


# @app.route('/job_listings', methods=['GET'])
# def job_listings():
#     return render_template('User-JobListings.html', job_listings_data=job_listings_data, error=None , uname = session["fname"])

# @app.route('/submit_resume/<job_title>', methods=['POST'])
# def submit_resume(job_title):

#     if 'file' not in request.files:
#         return render_template('User-JobListings.html', error='No file part', job_listings_data=job_listings_data)

#     file = request.files['file']

#     if file.filename == '':
#         return render_template('User-JobListings.html', error='No selected file', job_listings_data=job_listings_data)

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)

#         job_description = next(job['description'] for job in job_listings_data if job['title'] == job_title)

#         resume_text = extract_text_from_pdf(file_path)
#         matcher = ResumeMatcher(job_description, resume_text)
#         similarity_score = matcher.calculate_similarity()

#         update_results_google_sheets(job_title, filename, similarity_score)

#     return redirect(url_for('job_listings'))


@app.route("/todo")
def todo():
    return render_template("Todo.html")


@app.route('/sendemail', methods=['POST'])
def send_email1():
    try:
        data = request.json

        sender_email = 'optimizeprime007@gmail.com'
        sender_password = 'qtohvqsovpjpptzk'
        receiver_email = data['assignee_email']
        task_description = data['task_description']
        print(receiver_email)
        em = EmailMessage()
        em['From'] = sender_email
        em['To'] = receiver_email
        em['Subject'] = 'Task Assignment'
        em.set_content(f"You have been assigned a new task: {task_description}")

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, em.as_string())
        server.quit()

        return jsonify({'status': 'success', 'message': 'Email sent successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    

@app.route("/system-update")
def system_update():
    return render_template("Update.html")

@app.route("/feedbacks")
def user_feed():
    return render_template("Feedback.html")


@app.route("/career-path",methods=["POST","GET"])
def career_path():
    if request.method == "POST":
        state = request.form["state"]
        qualification = request.form["qualification"]
        skills = request.form["skills"]
        experience = request.form["experience"]
        job_title = request.form["job_title"]
        company = request.form["company"]
        industry = request.form["industry"]
        certifications = request.form["certifications"]
        desired_industry = request.form["desired_industry"]
        print(state)

        job_name = career(state,qualification,skills,experience,job_title,company,industry,certifications,desired_industry)
        print(job_name[0])
        return render_template("User-Career.html", job_role = str(job_name[0]))
    return render_template("User-Career.html")

df=pd.read_csv('career_datas.csv')
df=df.drop(['Name','Username'],axis=True)
df=df.fillna('NA')
x=df.copy()
x=x.drop('Desired Job Title',axis=True)
y=df['Desired Job Title']
from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
y=le.fit_transform(y)
x=pd.get_dummies(x)
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(x,y,random_state=42,test_size=0.2)
from sklearn.ensemble import RandomForestClassifier
clf=RandomForestClassifier()
clf.fit(x_train,y_train)

def career(state,qualification,skills,Experience,job_title,Company,Industry,Certifications,Desired_Industry):
  df=pd.DataFrame({
      'State':state,
      'Qualification':qualification,
      'Skills':skills,
      'Experience':Experience,
      'Current Job Title':job_title,
      'Current Company':Company,
      'Industry':Industry,
      'Certifications':Certifications,
      'Desired Industry':Desired_Industry
  },index=[0])
  print(df)

  x=pd.get_dummies(df)
  df_new_encoded = x.reindex(columns=x_train.columns, fill_value=0)
  print(df_new_encoded)

  ypred=clf.predict(df_new_encoded)
  print(ypred)
  print(le.inverse_transform(ypred))
  return le.inverse_transform(ypred)



if __name__=="__main__":
    app.run(debug=True)