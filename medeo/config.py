# from dotenv import load_dotenv
import os
# from app import *


class Config:
    LANGUAGES = ['fr', 'en']

    # load_dotenv(override=True)
    RECAPTCHA_PUBLIC_KEY= os.getenv('CAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY=os.getenv('CAPTCHA_PRIVATE_KEY')

    # Google Cloud SQL (change this accordingly)
    PASSWORD ="**********"
    PUBLIC_IP_ADDRESS ="**.**.***.***"
    DBNAME ="development"
    PROJECT_ID ="mystical-runway-364716"
    INSTANCE_NAME ="medeotax"

    #SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
    #SQLALCHEMY_TRACK_MODIFICATIONS = True

    ## CONFIG LOCAL 
    # CONFIG LOCAL MAILDEV
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    

    #CONFIG PRO EMAIL
    #MAIL_SERVER = os.environ.get('EMAIL_SERVER')
    #MAIL_PORT = os.environ.get('EMAIL_PORT')
    #MAIL_USE_TLS = True
    #MAIL_USERNAME = os.environ.get('EMAIL_USER')
    #MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    RECAPTCHA_USE_SSL= False
    RECAPTCHA_OPTIONS= {'theme':'black'}
    RECAPTCHA_PUBLIC_KEY= os.getenv('CAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY=os.getenv('CAPTCHA_PRIVATE_KEY')
    # print(os.environ['CAPTCHA_PUBLIC_KEY'])
    # print(os.environ.get('CAPTCHA_PUBLIC_KEY'))
    # print(os.getenv('CAPTCHA_PUBLIC_KEY'))
    # print(os.environ.get('CAPTCHA_PUBLIC_KEY', 'default value'))

    

