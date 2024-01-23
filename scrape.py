##   Template news : template_news.html

### Récuperer le contenu de l'article (titre, description, contenu, image)

### l'article est stocké dans medeo/templates/news/fiscal_juridique_ou_social/nom_de_l'article.html

### L'image est stockée /medeo/static/images/news/fiscal/news_787.jpeg

from bs4 import BeautifulSoup
import requests


liste_articles_to_scrape = ['https://www.lagazettedescommunes.com/893548/les-bases-minimums-de-cfe-un-principe-meconnu/']
response = requests.get(liste_articles_to_scrape[0])

soup = BeautifulSoup(response.text, 'html.parser')

# print(soup)
titre_article = soup.find_all(class_="titleA titleA--1 titleA--lineHeight48")
print(titre_article[0].text)





### Generer un fichier html avec les bons éléments





