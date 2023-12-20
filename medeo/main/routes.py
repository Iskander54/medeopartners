from flask import render_template, Response,request, Blueprint, g,current_app, abort,url_for,redirect,render_template_string,make_response,send_from_directory,current_app, send_from_directory
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
    return render_template('home.html',apikey=current_app.config['G_API_KEY'])

@main.route("/your_firm",defaults={'lang_code':'en'})
@main.route("/votre_cabinet",defaults={'lang_code':'fr'})
def votre_cabinet():
    return render_template('votre_cabinet.html',title='Votre cabinet', active_page='votre_cabinet')


@main.route("/our_expertise",defaults={'lang_code':'en'})
@main.route("/notre_expertise",defaults={'lang_code':'fr'})
def notre_expertise():
    return render_template('notre_expertise.html',title='Notre expertise',active_page='notre_expertise')


@main.route("/news",defaults={'lang_code':'en'})
@main.route("/actualites",defaults={'lang_code':'fr'})
def actualites():
    active_page = 'actualites'
    print("ICI 1")
    print(active_page)
    return render_template('actualites.html',title='Actualités', active_page='actualites')

@main.route("/contactus",defaults={'lang_code':'en'})
@main.route("/nouscontacter",defaults={'lang_code':'fr'})
def nouscontacter():
    active_page = 'nouscontacter'
    print("ICI 2")
    print(active_page)
    return render_template('nouscontacter.html',title='Nous contacter', active_page='nouscontacter')

@main.route("/account",defaults={'lang_code':'en'})
@main.route("/espace_clients",defaults={'lang_code':'fr'})
def espace_clients():
    return render_template('espace_clients.html',title='Espace Clients')

@main.route("/council_optimization",defaults={'lang_code':'en'})
@main.route("/conseil_optimisation",defaults={'lang_code':'fr'})
def conseil_optimisation():
    return render_template('/conseil_optimisation.html',title='Conseil Optimisation',active_page='conseil_optimisation')

@main.route("/auditing",defaults={'lang_code':'en'})
@main.route("/audit",defaults={'lang_code':'fr'})
def audit():
    return render_template('/audit.html',title='Audit',active_page='audit')

@main.route("/accounting",defaults={'lang_code':'en'})
@main.route("/expertise_comptable",defaults={'lang_code':'fr'})
def expertise_comptable():
    return render_template('/expertise_comptable.html',title='Expertise Comptable',active_page='expertise_comptable')

@main.route("/legal",defaults={'lang_code':'en'})
@main.route("/legal",defaults={'lang_code':'fr'})
def legal():
    return render_template('/legal.html',title='Mentions Légales')



############################
# NEWS
############################


@main.route("news_detail")
def news_detail():
    return render_template('/news/news_detail.html',title='News Details')

# FISCAL
##############

@main.route("news_template")
def news_template():
    return render_template('/news/news_template.html',title='News Template')


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



@main.route('/robots.txt')
def robots_txt():
    # return Response("User-agent: *\nDisallow: ", content_type='text/plain')
    return send_from_directory(current_app.static_folder, 'robots.txt')

@main.route('/sitemap.xml')
def sitemap():
    host_components = request.host.split('.')
    domain = f"{host_components[-2]}.{host_components[-1]}"  # assuming a domain like www.example.com
    url_root = request.url_root[:-1]  # remove trailing slash

    # List of routes to include in the sitemap
    static_urls = [
        {'loc': url_for('main.home', _external=True)},
        {'loc': url_for('main.votre_cabinet', _external=True)},
        {'loc': url_for('main.notre_expertise', _external=True)},
        {'loc': url_for('main.expertise_comptable', _external=True)},
        {'loc': url_for('main.audit', _external=True)},
        {'loc': url_for('main.conseil_optimisation', _external=True)},
        {'loc': url_for('main.actualites', _external=True)},
        {'loc': url_for('main.nouscontacter', _external=True)},
    ]

    # Optional: Add dynamic URLs, like news details
    # for news_id in range(1, 100):  # Example: iterate over a range of news IDs
    #     static_urls.append({'loc': url_for('main.news_detail', news_id=news_id, _external=True)})

    xml_sitemap = render_template_string('''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            {% for url in urls %}
                <url><loc>{{ url.loc }}</loc></url>
            {% endfor %}
        </urlset>''', urls=static_urls)

    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"    

    return response