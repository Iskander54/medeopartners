#!/usr/bin/env python3
"""
Script d'automatisation de génération de contenu avec OpenAI
Génère des articles optimisés SEO pour le blog comptabilité/fiscalité
"""

import openai
import json
import sys
import os
from datetime import datetime, timedelta
import time
from slugify import slugify
import requests
from bs4 import BeautifulSoup
import re

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from medeo import create_app, db
from medeo.models import BlogArticle, BlogCategory, BlogTag, User, ContentCalendar

class AIContentGenerator:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.app = create_app()
        
    def generate_article_content(self, topic, keywords, category, target_length=1500):
        """Génère le contenu d'un article avec OpenAI"""
        
        prompt = f"""
Tu es un expert comptable et fiscal français. Rédige un article de blog optimisé SEO sur le sujet suivant :

SUJET : {topic}

MOT-CLÉ PRINCIPAL : {keywords.get('primary', '')}
MOTS-CLÉS SECONDAIRES : {', '.join(keywords.get('secondary', []))}
CATÉGORIE : {category}
LONGUEUR CIBLE : {target_length} mots

REQUIS :
1. Structure claire avec balises HTML (h2, h3, p, ul, li, strong)
2. Introduction accrocheuse
3. Contenu informatif et pratique
4. FAQ à la fin
5. Optimisation SEO naturelle
6. Ton professionnel mais accessible
7. Exemples concrets et cas pratiques
8. Conformité aux règles françaises

FORMAT DE RÉPONSE :
- Titre H1 accrocheur
- Contenu structuré avec balises HTML
- Pas de préambule ou conclusion générique
- Contenu directement utilisable
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Tu es un expert comptable français spécialisé en fiscalité et comptabilité. Tu rédiges des articles de blog optimisés SEO pour un cabinet d'expertise comptable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Nettoyer le contenu
            content = self.clean_content(content)
            
            return content
            
        except Exception as e:
            print(f"Erreur génération contenu : {e}")
            return None

    def generate_meta_data(self, title, content, keywords):
        """Génère les métadonnées SEO"""
        
        prompt = f"""
Génère les métadonnées SEO pour cet article :

TITRE : {title}
CONTENU : {content[:500]}...
MOT-CLÉ PRINCIPAL : {keywords.get('primary', '')}

Génère :
1. Meta title (60 caractères max)
2. Meta description (160 caractères max)
3. Excerpt (200 caractères max)
4. Focus keyword
5. Secondary keywords (liste)

Format JSON :
{{
    "meta_title": "...",
    "meta_description": "...",
    "excerpt": "...",
    "focus_keyword": "...",
    "secondary_keywords": ["...", "..."]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert SEO spécialisé en comptabilité."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            
            # Extraire le JSON
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return None
                
        except Exception as e:
            print(f"Erreur génération métadonnées : {e}")
            return None

    def clean_content(self, content):
        """Nettoie et formate le contenu"""
        # Supprimer les préambules inutiles
        content = re.sub(r'^.*?(<h[1-6]>)', r'\1', content, flags=re.DOTALL)
        
        # Nettoyer les balises HTML
        content = content.strip()
        
        # S'assurer que le contenu commence par un titre
        if not content.startswith('<h'):
            content = f'<h1>{content.split(".")[0]}</h1>\n{content}'
        
        return content

    def extract_title_from_content(self, content):
        """Extrait le titre du contenu HTML"""
        soup = BeautifulSoup(content, 'html.parser')
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        return "Article généré automatiquement"

    def create_article_from_calendar(self, calendar_item):
        """Crée un article à partir d'un élément du calendrier éditorial"""
        
        with self.app.app_context():
            # Récupérer la catégorie
            category = BlogCategory.query.get(calendar_item.category_id)
            if not category:
                print(f"Catégorie non trouvée pour {calendar_item.title}")
                return None
            
            # Récupérer un auteur
            author = User.query.first()
            if not author:
                print("Aucun utilisateur trouvé")
                return None
            
            # Préparer les mots-clés
            keywords = {
                'primary': calendar_item.target_keywords.split(',')[0] if calendar_item.target_keywords else '',
                'secondary': calendar_item.target_keywords.split(',')[1:] if calendar_item.target_keywords else []
            }
            
            # Générer le contenu
            print(f"Génération du contenu pour : {calendar_item.title}")
            content = self.generate_article_content(
                calendar_item.title,
                keywords,
                category.name
            )
            
            if not content:
                print("Échec de la génération du contenu")
                return None
            
            # Extraire le titre
            title = self.extract_title_from_content(content)
            
            # Générer les métadonnées
            meta_data = self.generate_meta_data(title, content, keywords)
            
            # Créer l'article
            article = BlogArticle(
                title=title,
                slug=slugify(title),
                excerpt=meta_data.get('excerpt', calendar_item.content_brief) if meta_data else calendar_item.content_brief,
                content=content,
                focus_keyword=meta_data.get('focus_keyword', keywords['primary']) if meta_data else keywords['primary'],
                secondary_keywords=json.dumps(meta_data.get('secondary_keywords', keywords['secondary'])) if meta_data else json.dumps(keywords['secondary']),
                meta_title=meta_data.get('meta_title', title) if meta_data else title,
                meta_description=meta_data.get('meta_description', calendar_item.content_brief) if meta_data else calendar_item.content_brief,
                status='published',
                published_at=datetime.now(),
                category_id=category.id,
                author_id=author.id,
                reading_time=len(content.split()) // 200
            )
            
            db.session.add(article)
            db.session.commit()
            
            # Mettre à jour le statut du calendrier
            calendar_item.status = 'published'
            db.session.commit()
            
            print(f"✅ Article créé : {title}")
            return article

    def generate_weekly_content(self):
        """Génère le contenu hebdomadaire automatiquement"""
        
        with self.app.app_context():
            # Récupérer les éléments du calendrier pour cette semaine
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=7)
            
            calendar_items = ContentCalendar.query.filter(
                ContentCalendar.planned_date.between(start_date, end_date),
                ContentCalendar.status == 'planned'
            ).all()
            
            print(f"Génération de {len(calendar_items)} articles pour cette semaine...")
            
            for item in calendar_items:
                try:
                    self.create_article_from_calendar(item)
                    time.sleep(2)  # Pause entre les générations
                except Exception as e:
                    print(f"Erreur pour {item.title}: {e}")
                    continue

    def scrape_news_for_inspiration(self, category_name, max_articles=5):
        """Scrape les actualités pour inspiration (respectant la légalité)"""
        
        # Sources autorisées pour inspiration
        sources = {
            'fiscal': [
                'https://www.impots.gouv.fr/portail/',
                'https://www.legifrance.gouv.fr/',
                'https://www.insee.fr/'
            ],
            'comptable': [
                'https://www.anc.gouv.fr/',
                'https://www.ordre-experts-comptables.fr/'
            ]
        }
        
        articles = []
        
        for source_url in sources.get(category_name.lower(), []):
            try:
                response = requests.get(source_url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraire les titres et liens (sans copier le contenu)
                headlines = soup.find_all(['h1', 'h2', 'h3'], limit=3)
                
                for headline in headlines:
                    title = headline.get_text().strip()
                    if title and len(title) > 20:
                        articles.append({
                            'title': title,
                            'source': source_url,
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                
                time.sleep(1)  # Respecter les robots.txt
                
            except Exception as e:
                print(f"Erreur scraping {source_url}: {e}")
                continue
        
        return articles[:max_articles]

    def create_content_calendar_items(self, num_items=10):
        """Crée des éléments dans le calendrier éditorial"""
        
        topics = [
            {
                'title': 'Les nouvelles règles de TVA en 2024 : ce qui change pour votre entreprise',
                'category': 'Fiscalité des Entreprises',
                'keywords': 'TVA 2024, nouvelles règles TVA, fiscalité entreprise'
            },
            {
                'title': 'Comment optimiser sa comptabilité avec les outils digitaux',
                'category': 'Tech et Outils Comptables',
                'keywords': 'comptabilité digitale, outils comptables, automatisation'
            },
            {
                'title': 'Guide complet des amortissements comptables en 2024',
                'category': 'Comptabilité Générale',
                'keywords': 'amortissements comptables, immobilisations, plan comptable'
            },
            {
                'title': 'Optimisation fiscale pour les particuliers : les solutions légales',
                'category': 'Fiscalité des Particuliers',
                'keywords': 'optimisation fiscale, défiscalisation, niches fiscales'
            },
            {
                'title': 'Les obligations comptables des petites entreprises en 2024',
                'category': 'Comptabilité Générale',
                'keywords': 'obligations comptables, petites entreprises, comptabilité'
            }
        ]
        
        with self.app.app_context():
            for i, topic in enumerate(topics):
                # Trouver la catégorie
                category = BlogCategory.query.filter_by(name=topic['category']).first()
                if not category:
                    continue
                
                # Créer l'élément du calendrier
                calendar_item = ContentCalendar(
                    title=topic['title'],
                    content_brief=f"Article sur {topic['title'].lower()}",
                    target_keywords=topic['keywords'],
                    category_id=category.id,
                    planned_date=datetime.now().date() + timedelta(days=i*3),  # Un article tous les 3 jours
                    status='planned'
                )
                
                db.session.add(calendar_item)
            
            db.session.commit()
            print(f"✅ {len(topics)} éléments ajoutés au calendrier éditorial")

def main():
    """Fonction principale"""
    print("=== GÉNÉRATEUR DE CONTENU IA - BLOG COMPTABILITÉ ===\n")
    
    # Configuration
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Variable d'environnement OPENAI_API_KEY non définie")
        return
    
    generator = AIContentGenerator(api_key)
    
    # Menu interactif
    while True:
        print("\nOptions disponibles :")
        print("1. Générer le contenu hebdomadaire automatiquement")
        print("2. Créer des éléments dans le calendrier éditorial")
        print("3. Scraper les actualités pour inspiration")
        print("4. Générer un article spécifique")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5) : ")
        
        if choice == '1':
            generator.generate_weekly_content()
            
        elif choice == '2':
            num_items = int(input("Nombre d'éléments à créer (défaut: 10) : ") or "10")
            generator.create_content_calendar_items(num_items)
            
        elif choice == '3':
            category = input("Catégorie (fiscal/comptable) : ")
            articles = generator.scrape_news_for_inspiration(category)
            print(f"\n📰 {len(articles)} articles trouvés :")
            for article in articles:
                print(f"- {article['title']} (source: {article['source']})")
                
        elif choice == '4':
            topic = input("Sujet de l'article : ")
            category = input("Catégorie : ")
            primary_keyword = input("Mot-clé principal : ")
            secondary_keywords = input("Mots-clés secondaires (séparés par des virgules) : ").split(',')
            
            keywords = {
                'primary': primary_keyword,
                'secondary': [k.strip() for k in secondary_keywords]
            }
            
            content = generator.generate_article_content(topic, keywords, category)
            if content:
                print(f"\n✅ Contenu généré ({len(content)} caractères)")
                print("=" * 50)
                print(content[:500] + "...")
                
        elif choice == '5':
            print("Au revoir !")
            break
            
        else:
            print("Choix invalide")

if __name__ == '__main__':
    main() 