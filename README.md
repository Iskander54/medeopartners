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

## TRANSLATIONS
routing and translations already implemented

### Translation / language-versionning
#### Fask-babel,babel 
check requirements.txt

#### HOWTO
1- Scan files specified for  text to translate 
`pybabel extract -F babel.cfg -o messages.pot .`

2- Create translation file where we will manually translate text
`pybabel init -i messages.pot -d medeo/translations -l en`

translate text in that file

3- Compile all of the translation
`pybabel compile -d medeo/translations`

messages.mo is created

## Gcloud
`gcloud auth login` : Ouvre une fenetre navigateur pour s'authentifier sur google et sur le projet
`gcloud projects list` : Pour voir tout les gcloud project
`gcloud config set project mystical-runway-364716` (Pour Medeo Partners)
`gcloud app deploy` : Déploie l'application dans l'AppEngine
`gcloud app browse` : Ouvre Chrome pour afficher l'application via l'url appengine-mystique


Pour le custom domain DNS sur l'app Engine: https://www.youtube.com/watch?v=iqAku7kveO8&t=8s


## RUN
- go to config.py and :
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    #MAIL_SERVER = os.environ.get('EMAIL_SERVER')
    #MAIL_PORT = os.environ.get('EMAIL_PORT')

- First install packages : $ pip install -r requirements.txt
- Run loccally : python run.py


## Docker
- got to config and :
    #MAIL_SERVER = 'localhost'
    #MAIL_PORT = 1025
    MAIL_SERVER = os.environ.get('EMAIL_SERVER')
    MAIL_PORT = os.environ.get('EMAIL_PORT')
- docker build -t medeo .
- docker run -d -p 5000:5000  medeo