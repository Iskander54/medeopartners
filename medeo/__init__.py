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
    from medeo.mesoutils import mesoutils
    
    app.register_blueprint(contacts)
    app.register_blueprint(rejoindre)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(blog)
    app.register_blueprint(chatbot)
    app.register_blueprint(mesoutils)

    def get_locale():
        if not g.get('lang_code', None):
            g.lang_code = request.accept_languages.best_match(app.config['LANGUAGES'])
        return g.lang_code

    babel.init_app(app, locale_selector=get_locale)
    
    @app.before_request
    def normalize_url():
        """Normalize URLs globally: force HTTPS and www"""
        # Skip for static files, robots.txt, sitemap, and health checks
        if request.endpoint in ['static', 'robots_txt', 'sitemap', 'android_chrome_icons']:
            return None
        
        # Only process in production (not localhost)
        if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
            return None
        
        host = request.host
        scheme = request.scheme
        
        # Normalize to www.medeo-partners.com with HTTPS
        needs_redirect = False
        new_host = host
        
        # Check and fix www
        if host == 'medeo-partners.com':
            new_host = 'www.medeo-partners.com'
            needs_redirect = True
        elif host.startswith('medeo-partners.com:'):
            # Handle with port
            new_host = host.replace('medeo-partners.com', 'www.medeo-partners.com')
            needs_redirect = True
        
        # Force HTTPS
        if scheme != 'https':
            needs_redirect = True
        
        if needs_redirect:
            new_url = f"https://www.medeo-partners.com{request.full_path}"
            return redirect(new_url, code=301)
        
        return None

    @app.route('/')
    def start():
        g.lang_code = 'fr'
        return redirect(url_for('main.home'))

    @app.route('/robots.txt')
    def robots_txt():
        return send_from_directory(app.static_folder, 'robots.txt')

    @app.route('/3a8fe26a40ad3a0570b5cd15f2ca5222.txt')
    def indexnow_key():
        """Fichier de vérification IndexNow pour Bing/Yandex."""
        return send_from_directory(app.static_folder, '3a8fe26a40ad3a0570b5cd15f2ca5222.txt',
                                   mimetype='text/plain')
    
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
    def sitemap():
        """Génère un sitemap XML dynamique avec hreflang et articles DB."""
        from medeo.main.routes import get_static_pages
        from medeo.models import BlogArticle

        DOMAIN = 'https://www.medeo-partners.com'
        today = datetime.now().strftime('%Y-%m-%d')

        def url_entry(loc_fr, loc_en, lastmod, changefreq='monthly', priority='0.8'):
            return (
                f'  <url>\n'
                f'    <loc>{DOMAIN}{loc_fr}</loc>\n'
                f'    <lastmod>{lastmod}</lastmod>\n'
                f'    <changefreq>{changefreq}</changefreq>\n'
                f'    <priority>{priority}</priority>\n'
                f'    <xhtml:link rel="alternate" hreflang="fr" href="{DOMAIN}{loc_fr}"/>\n'
                f'    <xhtml:link rel="alternate" hreflang="en" href="{DOMAIN}{loc_en}"/>\n'
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}{loc_fr}"/>\n'
                f'  </url>\n'
            )

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'

        # Pages statiques avec hreflang FR/EN
        for page in get_static_pages():
            url_fr = page['url']
            if '/fr/' not in url_fr:
                continue
            url_en = (url_fr
                      .replace('/fr/', '/en/')
                      .replace('/accueil', '/home')
                      .replace('/votre_cabinet', '/your_firm')
                      .replace('/notre_expertise', '/our_expertise')
                      .replace('/nouscontacter', '/contactus')
                      .replace('/actualites', '/news')
                      .replace('/nos_services', '/our_services')
                      .replace('/expertise_comptable', '/accounting')
                      .replace('/conseil_optimisation', '/council_optimization')
                      .replace('/espace_clients', '/account'))
            xml += url_entry(url_fr, url_en,
                             page.get('lastmod', today),
                             page.get('changefreq', 'monthly'),
                             page.get('priority', '0.8'))

        # Page index blog
        xml += url_entry('/fr/blog/', '/en/blog/', today, 'weekly', '0.8')

        # Articles statiques legacy (toujours inclus)
        static_slugs = [
            ('loi-finances-2026-impact-entreprise',         '2026-01-12', '0.9'),
            ('tva-obligations-declaratives-dirigeants',      '2026-01-12', '0.8'),
            ('creation-entreprise-erreurs-comptables-fiscales-premiere-annee', '2026-01-12', '0.8'),
        ]
        seen_slugs = {s[0] for s in static_slugs}

        for slug, lastmod, priority in static_slugs:
            xml += url_entry(f'/fr/blog/article/{slug}', f'/en/blog/article/{slug}',
                             lastmod, 'monthly', priority)

        # Articles DB publiés (exclure les slugs statiques déjà listés)
        try:
            db_articles = BlogArticle.query.filter_by(status='published').order_by(
                BlogArticle.published_at.desc()
            ).all()
            for art in db_articles:
                if art.slug in seen_slugs:
                    continue
                lastmod_art = (art.updated_at or art.published_at or datetime.now()).strftime('%Y-%m-%d')
                xml += url_entry(f'/fr/blog/article/{art.slug}', f'/en/blog/article/{art.slug}',
                                 lastmod_art, 'monthly', '0.8')
        except Exception as e:
            current_app.logger.warning(f'Sitemap: impossible de charger les articles DB: {e}')

        xml += '</urlset>'

        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
        return response

    
    return app