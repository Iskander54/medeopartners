from flask import render_template, request, Blueprint

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    return render_template('home.html')

@main.route("/cabinet_historique")
def cabinet_historique():
    return render_template('/cabinet/cabinet_historique.html',title='Historique')

@main.route("/cabinet_valeurs")
def cabinet_valeurs():
    return render_template('/cabinet/cabinet_valeurs.html',title='Valeurs')

@main.route("/cabinet_associes")
def cabinet_associes():
    return render_template('/cabinet/cabinet_associes.html',title='Associés')

@main.route("/cabinet_temoignages")
def cabinet_temoignages():
    return render_template('/cabinet/cabinet_temoignages.html',title='Témoignages')

@main.route("/cabinet_nousrejoindre")
def cabinet_nousrejoindre():
    return render_template('/cabinet/cabinet_nousrejoindre.html',title='Nous rejoindre')

@main.route("/audit-conseil")
def auditconseil():
    return render_template('/audit-conseil.html',title='Audit - Conseil')

@main.route("/conseil_optimisation")
def conseil_optimisation():
    return render_template('/conseil_optimisation.html',title='Conseil Optimisation')

@main.route("/audit")
def audit():
    return render_template('/audit.html',title='Audit')

@main.route("/expertise_comptable")
def expertise_comptable():
    return render_template('/expertise_comptable.html',title='Expertise Comptable')

@main.route("/fiscalite-juridique")
def fiscalitejuridique():
    return render_template('/fiscalite-juridique.html',title='Fiscalité - Juridique')

@main.route("/nos_expertises")
def nos_expertises():
    return render_template('nos_expertises.html',title='Nos expertises')


@main.route("/actualites")
def actualites():
    return render_template('actualites.html',title='Actualités')

@main.route("/nouscontacter")
def nouscontacter():
    return render_template('nouscontacter.html',title='Nous contacter')

@main.route("/legal")
def legal():
    return render_template('legal.html',title='Nous contacter')

@main.route("/espace_clients")
def espace_clients():
    return render_template('espace_clients.html',title='Espace Clients')



##############
#      NEWS
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


