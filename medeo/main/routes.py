from flask import render_template, request, Blueprint, g,current_app, abort,url_for,redirect
from flask_babel import _,refresh
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
    return render_template('home.html')

@main.route("/your_firm",defaults={'lang_code':'en'})
@main.route("/votre_cabinet",defaults={'lang_code':'fr'})
def votre_cabinet():
    return render_template('votre_cabinet.html',title='Votre cabinet')


@main.route("/our_expertise",defaults={'lang_code':'en'})
@main.route("/notre_expertise",defaults={'lang_code':'fr'})
def notre_expertise():
    return render_template('notre_expertise.html',title='Notre expertise')


@main.route("/news",defaults={'lang_code':'en'})
@main.route("/actualites",defaults={'lang_code':'fr'})
def actualites():
    return render_template('actualites.html',title='Actualités')

@main.route("/contactus",defaults={'lang_code':'en'})
@main.route("/nouscontacter",defaults={'lang_code':'fr'})
def nouscontacter():
    return render_template('nouscontacter.html',title='Nous contacter')

@main.route("/account",defaults={'lang_code':'en'})
@main.route("/espace_clients",defaults={'lang_code':'fr'})
def espace_clients():
    return render_template('espace_clients.html',title='Espace Clients')

@main.route("/council_optimization",defaults={'lang_code':'en'})
@main.route("/conseil_optimisation",defaults={'lang_code':'fr'})
def conseil_optimisation():
    return render_template('/conseil_optimisation.html',title='Conseil Optimisation')

@main.route("/auditing",defaults={'lang_code':'en'})
@main.route("/audit",defaults={'lang_code':'fr'})
def audit():
    return render_template('/audit.html',title='Audit')

@main.route("/accounting",defaults={'lang_code':'en'})
@main.route("/expertise_comptable",defaults={'lang_code':'fr'})
def expertise_comptable():
    return render_template('/expertise_comptable.html',title='Expertise Comptable')

@main.route("/legal",defaults={'lang_code':'en'})
@main.route("/legal",defaults={'lang_code':'fr'})
def legal():
    return render_template('/legal.html',title='Mentions Légales')



############################
# NEWS
############################

# FISCAL
##############

@main.route("/news/fiscal/news_1234")
def news_1234():
    return render_template('/news/fiscal/news_1234.html',title='Fiscal')


@main.route("/news/fiscal/news_787")
def news_787():
    return render_template('/news/fiscal/news_787.html',title='Fiscal')


@main.route("/news/fiscal/news_1112")
def news_1112():
    return render_template('/news/fiscal/news_1112.html',title='Fiscal')

@main.route("/news/fiscal/news_4456")
def news_4456():
    return render_template('/news/fiscal/news_4456.html',title='Fiscal')


@main.route("/news/fiscal/news_5555")
def news_5555():
    return render_template('/news/fiscal/news_5555.html',title='Fiscal')


@main.route("/news/fiscal/news_1212")
def news_1212():
    return render_template('/news/fiscal/news_1212.html',title='Fiscal')


@main.route("/news/fiscal/news_4322")
def news_4322():
    return render_template('/news/fiscal/news_4322.html',title='Fiscal')

@main.route("/news/fiscal/news_1200")
def news_1200():
    return render_template('/news/fiscal/news_1200.html',title='Fiscal')




# SOCIAL
##############

@main.route("/news/social/news_1")
def news_1():
    return render_template('/news/social/news_1.html',title='Social')


@main.route("/news/social/news_2")
def news_2():
    return render_template('/news/social/news_2.html',title='Social')


@main.route("/news/social/news_3")
def news_3():
    return render_template('/news/social/news_3.html',title='Social')


@main.route("/news/social/news_4")
def news_4():
    return render_template('/news/social/news_4.html',title='Social')


# JURIDIQUE
##############

@main.route("/news/juridique/news_12")
def news_12():
    return render_template('/news/juridique/news_12.html',title='Juridique')





############################
#  END NEWS
############################