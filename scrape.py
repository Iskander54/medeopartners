from bs4 import BeautifulSoup
import requests
from jinja2 import Environment, FileSystemLoader
                                   
# URL de l'article à scraper
# Liste initiale
liste_articles_to_scrape = [
    'https://www.lagazettedescommunes.com/893548/les-bases-minimums-de-cfe-un-principe-meconnu/'
    

]

response = requests.get(liste_articles_to_scrape[0])
soup = BeautifulSoup(response.text, 'html.parser')

# Extraction des éléments de l'article (titre, contenu, etc.)
titre_article = soup.find_all(class_="titleA titleA--1 titleA--lineHeight48")[0].text
content_article = soup.find_all(class_="articleChapo")[0].text

# Spécifiez le chemin vers le dossier contenant vos templates
templates_folder = 'medeo/templates/news/'

# Initialisez l'environnement Jinja2 avec un chargeur de système de fichiers
env = Environment(loader=FileSystemLoader('medeo/templates'))
template = env.get_template('news/template_news.html')




# Rendez le modèle avec les données de l'article
html_output = template.render(titre=titre_article, contenu=content_article)

# Spécifiez l'emplacement et le nom du nouveau fichier HTML à créer
chemin_fichier_html = 'medeo/templates/news/lenouvellearticle.html'

# Écrivez le résultat dans le fichier HTML
with open(chemin_fichier_html, 'w', encoding='utf-8') as file:
    file.write(html_output)