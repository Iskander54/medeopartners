import os
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse

# Liste des URL à scraper
liste_articles_to_scrape = [
    'https://www.lagazettedescommunes.com/893548/les-bases-minimums-de-cfe-un-principe-meconnu/',
    'https://www.lagazettedescommunes.com/909413/reforme-de-la-dgf-le-chantier-est-relance/',
    'https://www.lagazettedescommunes.com/909102/la-cour-des-comptes-denonce-la-situation-des-finances-publiques-en-2024/'
]

# Spécifiez le chemin vers le dossier contenant vos templates
env = Environment(loader=FileSystemLoader('medeo/templates'))
template = env.get_template('news/template_news.html')

# Dossier pour enregistrer les images
dossier_images_base = 'medeo/static/images/news/'
dossier_templates_base = 'medeo/templates/news/'

# Boucle pour parcourir chaque URL dans la liste
for i, url in enumerate(liste_articles_to_scrape):
    # Récupérer le contenu de l'article
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraction des éléments de l'article (titre, contenu, image, etc.)
    category_article = soup.find_all(class_="superTag")[0].text
    titre_article = soup.find_all(class_="titleA titleA--1 titleA--lineHeight48")[0].text
    content_article = soup.find_all(class_="articleChapo")[0].text

    # Créer un dossier pour la catégorie s'il n'existe pas
    dossier_images_category = f'{dossier_images_base}{category_article.lower()}/'
    dossier_templates_category = f'{dossier_templates_base}{category_article.lower()}/'
    os.makedirs(dossier_images_category, exist_ok=True)
    os.makedirs(dossier_templates_category, exist_ok=True)

    # Récupérer l'URL de l'image en utilisant la balise figure et la classe articleImage
    figure_tag = soup.find('figure', class_='articleImage')
    if figure_tag and 'data-original' in figure_tag.img.attrs:
        image_url_absolute = figure_tag.img['data-original']
        image_response = requests.get(image_url_absolute)

        # Utiliser le titre de l'article pour nommer l'image
        titre_url = '-'.join(urlparse(url).path.split('/')[2].split('-')[1:-1])
        image_filename = f'{dossier_images_category}{titre_url}.jpg'
        with open(image_filename, 'wb') as image_file:
            image_file.write(image_response.content)
        
        # Chemin pour afficher dans le HTML
        image_filename_html = f'../static/images/news/{category_article.lower()}/{titre_url}.jpg'
    else:
        image_filename_html = None

    # Remplacer les tirets par des underscores dans le titre de l'article
    titre_url = titre_url.replace('-', '_')

    # Rendre le modèle avec les données de l'article et l'URL de l'image locale
    html_output = template.render(category=category_article, titre=titre_article, contenu=content_article, image_url=image_filename_html)

    html_output = f'{{% extends "layout.html" %}}\n{{% block content %}}\n{html_output}\n{{% endblock content %}}'

    # Écrire le résultat dans le fichier HTML dans le dossier de la catégorie
    fichier_html = f'{dossier_templates_category}{titre_url}article{i + 1}.html'
    with open(fichier_html, 'w', encoding='utf-8') as file:
        file.write(html_output)

    # Ajouter la route dans le fichier temp_urls.py
    with open('medeo/main/temp_urls.py', 'a', encoding='utf-8') as temp_file:
        temp_file.write(f'    @main.route("/{titre_url}")\n')
        temp_file.write(f'    def {titre_url}():\n')
        temp_file.write(f'            return render_template("/news/{category_article.lower()}/{titre_url}.html", title="News Template")\n')