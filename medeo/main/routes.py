from flask import render_template, request, Blueprint, g, current_app, abort, url_for, redirect
from flask_babel import _, refresh
main = Blueprint('main', __name__, url_prefix='/<lang_code>')


@main.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@main.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@main.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match(
                '/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)

    dfl = request.url_rule.defaults
    if 'lang_code' in dfl:
        if dfl['lang_code'] != request.full_path.split('/')[1]:
            abort(404)


@main.route("/accueil", defaults={'lang_code': 'fr'})
def home():
    page = request.args.get('page', 1, type=int)
    return render_template('home.html', apikey=current_app.config['G_API_KEY'])


@main.route("/votre_cabinet", defaults={'lang_code': 'fr'})
def votre_cabinet():
    return render_template('votre_cabinet.html', title='Votre cabinet', apikey=current_app.config['G_API_KEY'])


@main.route("/notre_expertise", defaults={'lang_code': 'fr'})
def notre_expertise():
    return render_template('notre_expertise.html', title='Notre expertise', apikey=current_app.config['G_API_KEY'])


@main.route("/actualites", defaults={'lang_code': 'fr'})
def actualites():
    return render_template('actualites.html', title='Actualités', apikey=current_app.config['G_API_KEY'])


@main.route("/nouscontacter", defaults={'lang_code': 'fr'})
def nouscontacter():
    return render_template('nouscontacter.html', title='Nous contacter', apikey=current_app.config['G_API_KEY'])


@main.route("/espace_clients", defaults={'lang_code': 'fr'})
def espace_clients():
    return render_template('espace_clients.html', title='Espace Clients', apikey=current_app.config['G_API_KEY'])


@main.route("/conseil_optimisation", defaults={'lang_code': 'fr'})
def conseil_optimisation():
    return render_template('/conseil_optimisation.html', title='Conseil Optimisation', apikey=current_app.config['G_API_KEY'])


@main.route("/audit", defaults={'lang_code': 'fr'})
def audit():
    return render_template('/audit.html', title='Audit', apikey=current_app.config['G_API_KEY'])


@main.route("/expertise_comptable", defaults={'lang_code': 'fr'})
def expertise_comptable():
    return render_template('/expertise_comptable.html', title='Expertise Comptable', apikey=current_app.config['G_API_KEY'])


@main.route("/legal", defaults={'lang_code': 'fr'})
def legal():
    return render_template('/legal.html', title='Mentions Légales', apikey=current_app.config['G_API_KEY'])


############################
# NEWS
############################

# FISCAL
##############

@main.route("news_template")
def news_template():
    return render_template('/news/news_template.html', title='News Template', apikey=current_app.config['G_API_KEY'])


@main.route("news_1234")
def news_1234():
    return render_template('/news/fiscal/news_1234.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_787")
def news_787():
    return render_template('/news/fiscal/news_787.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_1112")
def news_1112():
    return render_template('/news/fiscal/news_1112.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_4456")
def news_4456():
    return render_template('/news/fiscal/news_4456.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_5555")
def news_5555():
    return render_template('/news/fiscal/news_5555.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_1212")
def news_1212():
    return render_template('/news/fiscal/news_1212.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_4322")
def news_4322():
    return render_template('/news/fiscal/news_4322.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


@main.route("news_1200")
def news_1200():
    return render_template('/news/fiscal/news_1200.html', title='Fiscal', apikey=current_app.config['G_API_KEY'])


# SOCIAL
##############

@main.route("news_1")
def news_1():
    return render_template('/news/social/news_1.html', title='Social', apikey=current_app.config['G_API_KEY'])


@main.route("news_2")
def news_2():
    return render_template('/news/social/news_2.html', title='Social', apikey=current_app.config['G_API_KEY'])


@main.route("news_3")
def news_3():
    return render_template('/news/social/news_3.html', title='Social', apikey=current_app.config['G_API_KEY'])


@main.route("news_4")
def news_4():
    return render_template('/news/social/news_4.html', title='Social', apikey=current_app.config['G_API_KEY'])


# JURIDIQUE
##############

@main.route("news_12")
def news_12():
    return render_template('/news/juridique/news_12.html', title='Juridique', apikey=current_app.config['G_API_KEY'])


############################
#  END NEWS
############################
