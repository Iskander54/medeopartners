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





@main.route("/cabinet_historique", defaults={'lang_code':'fr'})
@main.route("/firm_history", defaults={'lang_code':'en'})
def cabinet_historique():
    return render_template('/cabinet/cabinet_historique.html',title='Historique')


@main.route("/firm_associates",defaults={'lang_code':'en'})
@main.route("/cabinet_associes",defaults={'lang_code':'fr'})
def cabinet_associes():
    return render_template('/cabinet/cabinet_associes.html',title='Associés')

@main.route("/firm_reviews",defaults={'lang_code':'en'})
@main.route("/cabinet_temoignages",defaults={'lang_code':'fr'})
def cabinet_temoignages():
    return render_template('/cabinet/cabinet_temoignages.html',title='Témoignages')

@main.route("/firm_joinus",defaults={'lang_code':'en'})
@main.route("/cabinet_nousrejoindre",defaults={'lang_code':'fr'})
def cabinet_nousrejoindre():
    return render_template('/cabinet/cabinet_nousrejoindre.html',title='Nous rejoindre')

@main.route("/audit-council",defaults={'lang_code':'en'})
@main.route("/audit-conseil",defaults={'lang_code':'fr'})
def auditconseil():
    return render_template('/audit-conseil.html',title='Audit - Conseil')

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

@main.route("/taxation-legal",defaults={'lang_code':'en'})
@main.route("/fiscalite-juridique",defaults={'lang_code':'fr'})
def fiscalitejuridique():
    return render_template('/fiscalite-juridique.html',title='Fiscalité - Juridique')

@main.route("/our_expertise",defaults={'lang_code':'en'})
@main.route("/nos_expertises",defaults={'lang_code':'fr'})
def nos_expertises():
    return render_template('nos_expertises.html',title='Nos expertises')

@main.route("/news",defaults={'lang_code':'en'})
@main.route("/actualites",defaults={'lang_code':'fr'})
def actualites():
    return render_template('actualites.html',title='Actualités')

@main.route("/contactus",defaults={'lang_code':'en'})
@main.route("/nouscontacter",defaults={'lang_code':'fr'})
def nouscontacter():
    return render_template('nouscontacter.html',title='Nous contacter')

@main.route("/law",defaults={'lang_code':'en'})
@main.route("/legal",defaults={'lang_code':'fr'})
def legal():
    return render_template('legal.html',title='Nous contacter')

@main.route("/account",defaults={'lang_code':'en'})
@main.route("/espace_clients",defaults={'lang_code':'fr'})
def espace_clients():
    return render_template('espace_clients.html',title='Espace Clients')



##############
# NEWS
##############

@main.route("/news_fiscalite")
def news_fiscalite():
    return render_template('/news/news_fiscalite.html',title='News Fiscalite')

@main.route("/news_juridique")
def news_juridique():
    return render_template('/news/news_juridique.html',title='News Juridique')

@main.route("/news_social")
def news_social():
    return render_template('/news/news_social.html',title='News Social')

@main.route("/news_metiers")
def news_metiers():
    return render_template('/news/news_metiers.html',title='News Metiers')

@main.route("/news_immobiliers")
def news_immobiliers():
    return render_template('/news/news_immobiliers.html',title='News Immobilier')


##############
##############

@main.route("/newstransmissionbailrural")
def newstransmissionbailrural():
    return render_template('/news/fiscalite/transmissionbailrural.html',title='News Fiscalite')

@main.route("/news_fisca_deduire_impayes_clients")
def news_fisca_deduire_impayes_clients():
    return render_template('/news/fiscalite/news_fisca_deduire_impayes_clients.html',title='News Fiscalite')



##############
##############
