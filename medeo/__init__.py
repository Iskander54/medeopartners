from flask import Flask, request,g,redirect, url_for, render_template,send_from_directory, current_app, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from medeo.config import Config
from flask_babel import Babel
# from flask_babelex import Babel  # Commenté car conflit avec flask_babel
# from flask_sslify import SSLify
# from flask_sitemap import Sitemap
# from flask_migrate import Migrate
from datetime import datetime
import os
# from flask_caching import Cache

babel = Babel( default_locale='fr')
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

# cache = Cache()


def create_app(config_class=Config):
    app = Flask(__name__)
    # ext = Sitemap(app=app)
    # sslify = SSLify(app)

    app.config.from_object(Config)
    
    # Ajouter un filtre markdown pour convertir le contenu des articles
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convertit le markdown en HTML"""
        import re
        if not text:
            return ''
        
        # Convertir les titres
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Convertir les listes à puces
        text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        # Entourer les groupes de <li> avec <ul>
        lines = text.split('\n')
        result = []
        in_list = False
        for line in lines:
            if line.startswith('<li>'):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(line)
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        if in_list:
            result.append('</ul>')
        text = '\n'.join(result)
        
        # Convertir les paragraphes (lignes non vides qui ne sont pas des balises)
        lines = text.split('\n')
        result = []
        current_para = []
        for line in lines:
            line = line.strip()
            if not line:
                if current_para:
                    result.append('<p>' + ' '.join(current_para) + '</p>')
                    current_para = []
                result.append('')
            elif line.startswith('<'):
                if current_para:
                    result.append('<p>' + ' '.join(current_para) + '</p>')
                    current_para = []
                result.append(line)
            else:
                current_para.append(line)
        if current_para:
            result.append('<p>' + ' '.join(current_para) + '</p>')
        text = '\n'.join(result)
        
        # Convertir le gras **text**
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        return text
    print("=== CONFIGURATION EMAIL ===")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"MAIL_PASSWORD: {'***' if app.config.get('MAIL_PASSWORD') else 'None'}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print("==========================")

    # Configuration du cache
    # app.config['CACHE_TYPE'] = 'simple'
    # app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    # cache.init_app(app)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    from medeo.users.routes import users
    from medeo.posts.routes import posts
    from medeo.main.routes import main
    from medeo.errors.handlers import errors
    from medeo.contacts.routes import contacts
    from medeo.rejoindre.routes import rejoindre
    from medeo.blog.routes import blog
    from medeo.chatbot.routes import chatbot
    
    app.register_blueprint(contacts)
    app.register_blueprint(rejoindre)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(blog)
    app.register_blueprint(chatbot)

    def get_locale():
        if not g.get('lang_code', None):
            g.lang_code = request.accept_languages.best_match(app.config['LANGUAGES'])
        return g.lang_code

    babel.init_app(app, locale_selector=get_locale)

    @app.route('/')
    def start():
        g.lang_code = 'fr'
        return redirect(url_for('main.home'))

    @app.route('/robots.txt')
    def robots_txt():
        return send_from_directory(app.static_folder, 'robots.txt')
    
    @app.route('/android-chrome-192x192.png')
    @app.route('/android-chrome-512x512.png')
    def android_chrome_icons():
        """Redirige les requêtes d'icônes Android vers les favicons"""
        filename = request.path.split('/')[-1]
        return send_from_directory(
            app.static_folder + '/images/favicon_io',
            filename,
            mimetype='image/png'
        )
    
    @app.route('/api/analytics', methods=['POST'])
    def analytics():
        """Endpoint pour recevoir les données analytics (sans préfixe de langue)"""
        try:
            data = request.get_json()
            
            # Log des événements analytics
            current_app.logger.info(f"Analytics event: {data.get('event')} - {data.get('url')}")
            
            # Ici vous pouvez ajouter le stockage en base de données
            # ou l'envoi vers un service externe
            
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            current_app.logger.error(f"Analytics error: {str(e)}")
            return make_response(jsonify({'status': 'error', 'message': str(e)}), 500)

    @app.route('/sitemap.xml')
    @app.route('/fr/sitemap.xml')
    # @cache.cached(timeout=3600)  # Cache 1 heure
    def sitemap():
        """Génère un sitemap XML dynamique"""
        from medeo.main.routes import get_static_pages
        
        # Pages statiques
        static_pages = get_static_pages()
        
        # Articles de blog statiques (templates HTML)
        blog_articles = [
            {
                'slug': 'tva-obligations-declaratives-dirigeants',
                'lastmod': '2026-01-12',
                'priority': '0.8'
            },
            {
                'slug': 'creation-entreprise-erreurs-comptables-fiscales-premiere-annee',
                'lastmod': '2026-01-12',
                'priority': '0.8'
            }
        ]
        
        # Générer le XML avec xmlns:xhtml pour hreflang
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        
        # Pages statiques avec versions FR et EN
        for page in static_pages:
            url_fr = page["url"]
            url_en = url_fr.replace('/fr/', '/en/').replace('/accueil', '/home').replace('/votre_cabinet', '/your_firm').replace('/notre_expertise', '/our_expertise').replace('/nouscontacter', '/contactus').replace('/actualites', '/news')
            
            xml += f'  <url>\n'
            xml += f'    <loc>https://www.medeo-partners.com{url_fr}</loc>\n'
            xml += f'    <lastmod>{page.get("lastmod", datetime.now().strftime("%Y-%m-%d"))}</lastmod>\n'
            xml += f'    <changefreq>{page.get("changefreq", "monthly")}</changefreq>\n'
            xml += f'    <priority>{page.get("priority", "0.8")}</priority>\n'
            # Ajouter hreflang si c'est une page FR
            if '/fr/' in url_fr:
                xml += f'    <xhtml:link rel="alternate" hreflang="fr" href="https://www.medeo-partners.com{url_fr}"/>\n'
                xml += f'    <xhtml:link rel="alternate" hreflang="en" href="https://www.medeo-partners.com{url_en}"/>\n'
                xml += f'    <xhtml:link rel="alternate" hreflang="x-default" href="https://www.medeo-partners.com{url_fr}"/>\n'
            xml += f'  </url>\n'
        
        # Page d'accueil du blog
        xml += f'  <url>\n'
        xml += f'    <loc>https://www.medeo-partners.com/fr/blog/</loc>\n'
        xml += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        xml += f'    <changefreq>weekly</changefreq>\n'
        xml += f'    <priority>0.7</priority>\n'
        xml += f'    <xhtml:link rel="alternate" hreflang="fr" href="https://www.medeo-partners.com/fr/blog/"/>\n'
        xml += f'    <xhtml:link rel="alternate" hreflang="en" href="https://www.medeo-partners.com/en/blog/"/>\n'
        xml += f'    <xhtml:link rel="alternate" hreflang="x-default" href="https://www.medeo-partners.com/fr/blog/"/>\n'
        xml += f'  </url>\n'
        
        # Articles de blog statiques
        for article in blog_articles:
            xml += f'  <url>\n'
            xml += f'    <loc>https://www.medeo-partners.com/fr/blog/article/{article["slug"]}</loc>\n'
            xml += f'    <lastmod>{article["lastmod"]}</lastmod>\n'
            xml += f'    <changefreq>monthly</changefreq>\n'
            xml += f'    <priority>{article["priority"]}</priority>\n'
            xml += f'    <xhtml:link rel="alternate" hreflang="fr" href="https://www.medeo-partners.com/fr/blog/article/{article["slug"]}"/>\n'
            xml += f'    <xhtml:link rel="alternate" hreflang="en" href="https://www.medeo-partners.com/en/blog/article/{article["slug"]}"/>\n'
            xml += f'    <xhtml:link rel="alternate" hreflang="x-default" href="https://www.medeo-partners.com/fr/blog/article/{article["slug"]}"/>\n'
            xml += f'  </url>\n'
        
        xml += '</urlset>'
        
        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
        return response

    
    return app