# medeo
Python 3.7.3
Flask 2.2.2
Werkzeug 2.2.2

# Prerequisite
maildev running local for smtp server (port 1025)

# DB
from medeo import create_app()
app = create_app()
app.app_context().push()
from medeo import db
db.create_all()

# Run commands :

## Pre-requisites
Make sure you have your IP address whitelisted on gcp.
Make sure the config.py has the right variable

## RUN
- go to config.py and :
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    #MAIL_SERVER = os.environ.get('EMAIL_SERVER')
    #MAIL_PORT = os.environ.get('EMAIL_PORT')

- First install packages : $ pip install -r requirements.txt
- Run loccally : python run.py


# Docker
- got to config and :
    #MAIL_SERVER = 'localhost'
    #MAIL_PORT = 1025
    MAIL_SERVER = os.environ.get('EMAIL_SERVER')
    MAIL_PORT = os.environ.get('EMAIL_PORT')
- docker build -t medeo .
- docker run -d -p 5000:5000  medeo

# Gcloud
gcloud auth login : Ouvre une fenetre navigateur pour s'authentifier sur google et sur le projet
gcloud app deploy : Déploie l'application dans l'AppEngine
gcloud app browse : Ouvre Chrome pour afficher l'application via l'url appengine-mystique
