import os
import secrets
from dotenv import load_dotenv

load_dotenv()

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_DEFAULT_DB = f"sqlite:///{os.path.join(_BASE_DIR, 'medeo', 'site.db')}"

class ConfigLocal:
    LANGUAGES = ['fr', 'en']
    RECAPTCHA_PUBLIC_KEY = os.getenv('CAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('CAPTCHA_PRIVATE_KEY')

    # Clé de développement uniquement. Générée aléatoirement à chaque
    # démarrage si SECRET_KEY n'est pas fournie : aucune valeur en dur ne peut
    # donc se retrouver en production par copier-coller. Effet de bord assumé
    # en local : les sessions sont perdues à chaque redémarrage.
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)

    # En local on sert en http : un cookie Secure ne serait jamais envoyé et
    # la connexion échouerait silencieusement.
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    CSP_ENFORCE = False

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