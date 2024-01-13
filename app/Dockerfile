FROM python:3.8-slim

RUN python3 -m venv venv

COPY . .

RUN pip install --upgrade pip

RUN pip install nltk

RUN pip install scikit_learn

RUN pip install pandas

RUN pip install -r requirements.txt

RUN pip install PyMuPDF

RUN pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:5000 wsgi:app
