from flask import render_template, Response, request, Blueprint, g, current_app, abort, url_for, redirect, make_response, send_from_directory, jsonify
from flask_babel import _,refresh

main = Blueprint('main', __name__, url_prefix='/<lang_code>')

@main.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@main.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

@main.before_request
def enforce_www():
    """Additional check for www and HTTPS (backup to global middleware)"""
    # This is a backup check - the global middleware in __init__.py should handle this
    # But we keep this as a safety net for the main blueprint
    if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
        return None
    
    host = request.host
    scheme = request.scheme
    
    # Only redirect if not already on www.medeo-partners.com with HTTPS
    if host != 'www.medeo-partners.com' or scheme != 'https':
        if host == 'medeo-partners.com' or (not host.startswith('www.') and 'medeo-partners.com' in host):
            new_url = f"https://www.medeo-partners.com{request.full_path}"
            return redirect(new_url, code=301)
    
    return None
        
@main.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)

    dfl = request.url_rule.defaults
    if 'lang_code' in dfl:
        if dfl['lang_code'] != request.full_path.split('/')[1]:
            abort(404)



@main.route("/accueil", defaults={'lang_code':'fr'})
@main.route("/home", defaults={'lang_code':'en'})
def home():
    page = request.args.get('page', 1, type=int)
    return render_template('home.html',apikey=current_app.config['G_API_KEY'])

@main.route("/your_firm",defaults={'lang_code':'en'})
@main.route("/votre_cabinet",defaults={'lang_code':'fr'})
def votre_cabinet():
    return render_template('votre_cabinet.html',title='Votre Cabinet d\'Expertise Comptable et Conseil Fiscal', active_page='votre_cabinet')


@main.route("/our_expertise",defaults={'lang_code':'en'})
@main.route("/notre_expertise",defaults={'lang_code':'fr'})
def notre_expertise():
    return render_template('notre_expertise.html',title='Expertise en Comptabilité, Fiscalité et Gestion',active_page='notre_expertise')


@main.route("/news",defaults={'lang_code':'en'})
@main.route("/actualites",defaults={'lang_code':'fr'})
def actualites():
    active_page = 'actualites'
    return render_template('actualites.html',title='Actualités et Insights sur la Comptabilité et la Fiscalité', active_page='actualites')

@main.route("/contactus",defaults={'lang_code':'en'})
@main.route("/nouscontacter",defaults={'lang_code':'fr'})
def nouscontacter():
    active_page = 'nouscontacter'
    return render_template('nouscontacter.html',title='Contactez-Nous pour toute expertise en comptabilité ou audit', active_page='nouscontacter')

@main.route("/account",defaults={'lang_code':'en'})
@main.route("/espace_clients",defaults={'lang_code':'fr'})
def espace_clients():
    return render_template('espace_clients.html',title='Espace Clients')

# Redirections pour éviter les 404
@main.route("/en/espace_clients")
def redirect_espace_clients_en():
    """Redirige /en/espace_clients vers /en/account"""
    return redirect(url_for('main.espace_clients', lang_code='en'), code=301)

@main.route("/en/nos_services")
def redirect_nos_services_en():
    """Redirige /en/nos_services vers /en/our_services"""
    return redirect(url_for('main.nos_services', lang_code='en'), code=301)

@main.route("/council_optimization",defaults={'lang_code':'en'})
@main.route("/conseil_optimisation",defaults={'lang_code':'fr'})
def conseil_optimisation():
    return render_template('/conseil_optimisation.html',title='Conseils en Optimisation Fiscale et Financière',active_page='conseil_optimisation')

@main.route("/auditing",defaults={'lang_code':'en'})
@main.route("/audit",defaults={'lang_code':'fr'})
def audit():
    return render_template('/audit.html',title='Spécialistes en Audit Financier et Conformité',active_page='audit')

@main.route("/accounting",defaults={'lang_code':'en'})
@main.route("/expertise_comptable",defaults={'lang_code':'fr'})
def expertise_comptable():
    return render_template('/expertise_comptable.html',title='Spécialistes en Comptabilité et Optimisation Fiscale',active_page='expertise_comptable')

@main.route("/legal",defaults={'lang_code':'en'})
@main.route("/mentions_legales",defaults={'lang_code':'fr'})
def legal():
    return render_template('/legal.html',title='Mentions Légales')

@main.route("/our_services",defaults={'lang_code':'en'})
@main.route("/nos_services",defaults={'lang_code':'fr'})
def nos_services():
    return render_template('nos_services.html',title='Nos Services - Expertise Comptable, Audit et Conseil',active_page='nos_services')

# Route pour la recherche (retourne 404 car pas implémentée)
@main.route("/search")
def search():
    """Route pour la recherche - retourne 404 car non implémentée"""
    abort(404)


############################
# NEWS
############################


@main.route("news_detail")
def news_detail():
    return render_template('/news/news_detail.html',title='News Details')

# FISCAL
##############


@main.route("news_1234")
def news_1234():
    return render_template('/news/fiscal/news_1234.html',title='Fiscal')


@main.route("news_787")
def news_787():
    return render_template('/news/fiscal/news_787.html',title='Fiscal')


@main.route("news_1112")
def news_1112():
    return render_template('/news/fiscal/news_1112.html',title='Fiscal')

@main.route("news_4456")
def news_4456():
    return render_template('/news/fiscal/news_4456.html',title='Fiscal')


@main.route("news_5555")
def news_5555():
    return render_template('/news/fiscal/news_5555.html',title='Fiscal')


@main.route("news_1212")
def news_1212():
    return render_template('/news/fiscal/news_1212.html',title='Fiscal')


@main.route("news_4322")
def news_4322():
    return render_template('/news/fiscal/news_4322.html',title='Fiscal')

@main.route("news_1200")
def news_1200():
    return render_template('/news/fiscal/news_1200.html',title='Fiscal')




# SOCIAL
##############

@main.route("news_1")
def news_1():
    return render_template('/news/social/news_1.html',title='Social')


@main.route("news_2")
def news_2():
    return render_template('/news/social/news_2.html',title='Social')


@main.route("news_3")
def news_3():
    return render_template('/news/social/news_3.html',title='Social')


@main.route("news_4")
def news_4():
    return render_template('/news/social/news_4.html',title='Social')


# JURIDIQUE
##############

@main.route("news_12")
def news_12():
    return render_template('/news/juridique/news_12.html',title='Juridique')





############################
#  END NEWS
############################



# @app.route('/robots.txt')
# def robots_txt():
#     # return Response("User-agent: *\nDisallow: ", content_type='text/plain')
#     # return send_from_directory(current_app.static_folder, 'robots.txt')
#     # return send_from_directory(current_app.static_folder, 'fr/robots.txt')
#     return send_from_directory(current_app.static_folder, 'robots.txt')


@main.route('/api/analytics', methods=['POST'])
def analytics():
    """Endpoint pour recevoir les données analytics"""
    try:
        data = request.get_json()
        
        # Log des événements analytics
        current_app.logger.info(f"Analytics event: {data.get('event')} - {data.get('url')}")
        
        # Ici vous pouvez ajouter le stockage en base de données
        # ou l'envoi vers un service externe
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        current_app.logger.error(f"Analytics error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/api/lead-magnet', methods=['POST'])
def lead_magnet():
    """Endpoint pour gérer les soumissions de lead magnets"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['magnetId', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Champ requis manquant: {field}'}), 400
        
        # Log de la soumission
        current_app.logger.info(f"Lead magnet submission: {data.get('magnetId')} - {data.get('email')}")
        
        # Ici vous pouvez ajouter :
        # - Stockage en base de données
        # - Envoi d'email de confirmation
        # - Intégration avec un CRM
        # - Envoi vers un service d'email marketing
        
        # Exemple d'envoi d'email (à implémenter)
        # send_lead_magnet_email(data)
        
        return jsonify({'status': 'success', 'message': 'Lead enregistré avec succès'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Lead magnet error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_static_pages():
    """Retourne la liste des pages statiques avec leurs métadonnées SEO"""
    return [
        {
            "url": "/fr/accueil",
            "changefreq": "weekly",
            "priority": "1.0",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/home",
            "changefreq": "weekly", 
            "priority": "1.0",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/votre_cabinet",
            "changefreq": "monthly",
            "priority": "0.9",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/your_firm",
            "changefreq": "monthly",
            "priority": "0.9", 
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/notre_expertise",
            "changefreq": "monthly",
            "priority": "0.9",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/our_expertise",
            "changefreq": "monthly",
            "priority": "0.9",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/expertise_comptable",
            "changefreq": "monthly",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/accounting",
            "changefreq": "monthly",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/audit",
            "changefreq": "monthly",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/auditing",
            "changefreq": "monthly",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/conseil_optimisation",
            "changefreq": "monthly",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/council_optimization",
            "changefreq": "monthly",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/nos_services",
            "changefreq": "monthly",
            "priority": "0.9",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/our_services",
            "changefreq": "monthly",
            "priority": "0.9",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/actualites",
            "changefreq": "weekly",
            "priority": "0.7",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/news",
            "changefreq": "weekly",
            "priority": "0.7",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/nouscontacter",
            "changefreq": "monthly",
            "priority": "0.6",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/contactus",
            "changefreq": "monthly",
            "priority": "0.6",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/espace_clients",
            "changefreq": "monthly",
            "priority": "0.5",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/account",
            "changefreq": "monthly",
            "priority": "0.5",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/fr/blog",
            "changefreq": "daily",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        },
        {
            "url": "/en/blog",
            "changefreq": "daily",
            "priority": "0.8",
            "lastmod": "2024-01-15"
        }
    ]

# Route catch-all pour gérer les URLs invalides avec emails ou autres patterns (DOIT être la dernière route)
@main.route("/<path:path>")
def catch_invalid_urls(path):
    """Gère les URLs invalides avec emails ou autres patterns invalides - DOIT être la dernière route"""
    # Si l'URL contient un @, c'est probablement un email mal formé dans l'URL
    if '@' in path:
        current_app.logger.warning(f"URL invalide avec email détectée: /{path}")
        abort(404)
    # Pour toutes les autres URLs non matchées, retourner 404
    abort(404)