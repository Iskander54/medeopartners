import os
from dotenv import load_dotenv

load_dotenv()

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_DEFAULT_DB = f"sqlite:///{os.path.join(_BASE_DIR, 'medeo', 'site.db')}"

class ConfigLocal:
    LANGUAGES = ['fr', 'en']
    RECAPTCHA_PUBLIC_KEY = os.getenv('CAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('CAPTCHA_PRIVATE_KEY')

    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    # Configuration pour développement local avec SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', _DEFAULT_DB)
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