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

    # SECRET_KEY : AUCUNE valeur par défaut, volontairement.
    # La valeur qui traînait ici ('5791628bb...') est celle d'un tutoriel Flask
    # public : n'importe qui peut forger un cookie de session signé avec, donc
    # se faire passer pour n'importe quel utilisateur connecté. Un démarrage
    # qui échoue bruyamment vaut mieux qu'une prod silencieusement forgeable.
    # Vaut None si la variable est absente : create_app() refuse alors de
    # démarrer (cf. medeo/__init__.py). La validation est faite là-bas et non
    # ici, pour qu'un simple `import medeo.config` reste possible.
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Durcissement des cookies de session
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', '1') != '0'
    SESSION_COOKIE_HTTPONLY = True   # illisible depuis JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # bloque l'envoi en CSRF cross-site
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # CSP bloquante plutôt que Report-Only (cf. medeo/security.py).
    CSP_ENFORCE = os.getenv('CSP_ENFORCE') == '1' 
    # Configuration base de données
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///medeo/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ## CONFIG LOCAL 
    # CONFIG LOCAL MAILDEV (pour développement local)
    # MAIL_SERVER = 'localhost'
    # MAIL_PORT = 1025
    # MAIL_USERNAME = None
    # MAIL_PASSWORD = None
    # MAIL_USE_SSL = False
    # MAIL_USE_TLS = False
    

    #CONFIG PRO EMAIL (pour production)
    MAIL_SERVER = os.getenv('EMAIL_SERVER')
    MAIL_PORT = os.getenv('EMAIL_PORT')
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    
    # Configuration temporaire pour Gmail sans validation en deux étapes
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USERNAME = 'contact@medeo-partners.com'
    # MAIL_PASSWORD = 'votre_mot_de_passe_normal'
    # MAIL_USE_SSL = False
    # MAIL_USE_TLS = True

    RECAPTCHA_OPTIONS= {'theme':'black'}
    G_API_KEY = os.environ.get('G_API_KEY')

    

    

