import os
from dotenv import load_dotenv

class ConfigLocal:
    load_dotenv()
    LANGUAGES = ['fr', 'en']
    RECAPTCHA_PUBLIC_KEY = os.getenv('CAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('CAPTCHA_PRIVATE_KEY')

    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    
    # Configuration pour développement local avec SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///medeo/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CONFIG LOCAL MAILDEV
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False

    RECAPTCHA_OPTIONS = {'theme': 'black'}
    G_API_KEY = os.environ.get('G_API_KEY') 