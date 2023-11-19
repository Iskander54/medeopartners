import os
from dotenv import load_dotenv
# from app import *


class Config:
    load_dotenv()
    LANGUAGES = ['fr', 'en']
    RECAPTCHA_PUBLIC_KEY= os.getenv('CAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY=os.getenv('CAPTCHA_PRIVATE_KEY')

    # Google Cloud SQL (change this accordingly)
    PASSWORD ="**********"
    PUBLIC_IP_ADDRESS ="**.**.***.***"
    DBNAME ="development"
    PROJECT_ID ="mystical-runway-364716"
    INSTANCE_NAME ="medeotax"

    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
    #SQLALCHEMY_TRACK_MODIFICATIONS = True

    ## CONFIG LOCAL 
    # CONFIG LOCAL MAILDEV
    #MAIL_SERVER = 'localhost'
    #MAIL_PORT = 1025
    

    #CONFIG PRO EMAIL
    MAIL_SERVER = os.getenv('EMAIL_SERVER')
    MAIL_PORT = os.getenv('EMAIL_PORT')
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_USE_SSL= False
    MAIL_USE_TLS = True

    RECAPTCHA_OPTIONS= {'theme':'black'}
    G_API_KEY = os.environ.get('G_API_KEY')

    

    

