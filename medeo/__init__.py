from flask import Flask, request,g,redirect, url_for, render_template,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from medeo.config import Config
from flask_babel import Babel
from flask_babelex import Babel
# from flask_sslify import SSLify
# from flask_sitemap import Sitemap

babel = Babel( default_locale='fr')
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    # ext = Sitemap(app=app)
    # sslify = SSLify(app)

    app.config.from_object(Config)
    print(app.config['G_API_KEY'])

    # db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    mail.init_mail(app.config)
    babel.init_app(app)


    from medeo.users.routes import users
    from medeo.posts.routes import posts
    from medeo.main.routes import main
    from medeo.errors.handlers import errors
    from medeo.contacts.routes import contacts
    from medeo.rejoindre.routes import rejoindre
    app.register_blueprint(contacts)
    app.register_blueprint(rejoindre)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    @babel.localeselector
    def get_locale():
        if not g.get('lang_code', None):
            g.lang_code = request.accept_languages.best_match(app.config['LANGUAGES'])
        return g.lang_code

    @app.route('/')
    def start():
        g.lang_code = 'fr'
        return redirect(url_for('main.home'))

    @app.route('/robots.txt')
    def robots_txt():
        return send_from_directory(app.static_folder, 'robots.txt')

    
    
    return app