#!/usr/bin/env python3
"""
Script de recherche de mots-clés SEO pour le blog comptabilité/fiscalité
Utilise des sources gratuites et des techniques de recherche avancées
"""

import requests
import json
import time
import csv
from datetime import datetime
import re
from urllib.parse import quote_plus
import sys
import os

class SEOKeywordResearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_google_suggestions(self, keyword, lang='fr'):
        """Récupère les suggestions Google pour un mot-clé"""
        suggestions = []
        try:
            url = f"http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': keyword,
                'hl': lang
            }
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                suggestions = data[1] if len(data) > 1 else []
        except Exception as e:
            print(f"Erreur suggestions Google pour {keyword}: {e}")
        return suggestions

    def get_related_keywords(self, keyword):
        """Récupère les mots-clés liés via différentes sources"""
        related = []
        
        # Suggestions Google
        suggestions = self.get_google_suggestions(keyword)
        related.extend(suggestions)
        
        # Variations avec "comment", "guide", "2024", etc.
        variations = [
            f"comment {keyword}",
            f"guide {keyword}",
            f"{keyword} 2024",
            f"{keyword} entreprise",
            f"{keyword} particulier",
            f"expert {keyword}",
            f"conseil {keyword}",
            f"optimisation {keyword}",
            f"régime {keyword}",
            f"calcul {keyword}"
        ]
        related.extend(variations)
        
        return list(set(related))

    def estimate_search_volume(self, keyword):
        """Estimation basique du volume de recherche (1-5)"""
        # Logique simple basée sur la longueur et la complexité
        if len(keyword.split()) == 1:
            return 5  # Mots-clés courts = plus populaires
        elif len(keyword.split()) == 2:
            return 4
        elif len(keyword.split()) == 3:
            return 3
        else:
            return 2

    def estimate_difficulty(self, keyword):
        """Estimation de la difficulté SEO (1-100)"""
        # Logique basée sur la concurrence estimée
        if any(word in keyword.lower() for word in ['comment', 'guide', '2024']):
            return 30  # Moins concurrentiel
        elif len(keyword.split()) >= 4:
            return 20  # Longue traîne = moins concurrentiel
        else:
            return 70  # Mots-clés courts = plus concurrentiels

    def research_keywords_for_category(self, category_name, base_keywords):
        """Recherche de mots-clés pour une catégorie"""
        print(f"\n🔍 Recherche de mots-clés pour : {category_name}")
        
        all_keywords = []
        
        for base_keyword in base_keywords:
            print(f"  - Analysant : {base_keyword}")
            
            # Mots-clés principaux
            main_keyword = {
                'keyword': base_keyword,
                'category': category_name,
                'search_volume': self.estimate_search_volume(base_keyword),
                'difficulty': self.estimate_difficulty(base_keyword),
                'cpc': 2.5,  # Estimation CPC
                'type': 'primary'
            }
            all_keywords.append(main_keyword)
            
            # Mots-clés liés
            related = self.get_related_keywords(base_keyword)
            for related_keyword in related[:10]:  # Limiter à 10 suggestions
                related_data = {
                    'keyword': related_keyword,
                    'category': category_name,
                    'search_volume': self.estimate_search_volume(related_keyword),
                    'difficulty': self.estimate_difficulty(related_keyword),
                    'cpc': 1.8,
                    'type': 'related'
                }
                all_keywords.append(related_data)
            
            time.sleep(1)  # Pause pour éviter le rate limiting
        
        return all_keywords

    def save_keywords_to_csv(self, keywords, filename):
        """Sauvegarde les mots-clés dans un fichier CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['keyword', 'category', 'search_volume', 'difficulty', 'cpc', 'type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for keyword in keywords:
                writer.writerow(keyword)
        
        print(f"✅ Mots-clés sauvegardés dans {filename}")

    def generate_content_ideas(self, keywords):
        """Génère des idées de contenu basées sur les mots-clés"""
        print("\n📝 Idées de contenu générées :")
        
        content_ideas = []
        
        for keyword in keywords:
            if keyword['search_volume'] >= 3:  # Mots-clés avec volume suffisant
                idea = {
                    'title': f"Guide complet : {keyword['keyword']}",
                    'keyword': keyword['keyword'],
                    'type': 'guide',
                    'priority': 'high' if keyword['search_volume'] >= 4 else 'medium'
                }
                content_ideas.append(idea)
                
                # Idées supplémentaires
                if 'comment' in keyword['keyword']:
                    idea2 = {
                        'title': f"Comment {keyword['keyword'].replace('comment ', '')} : étapes pratiques",
                        'keyword': keyword['keyword'],
                        'type': 'tutorial',
                        'priority': 'medium'
                    }
                    content_ideas.append(idea2)
        
        return content_ideas

def main():
    """Fonction principale"""
    print("=== RECHERCHE DE MOTS-CLÉS SEO - BLOG COMPTABILITÉ ===\n")
    
    seo_research = SEOKeywordResearch()
    
    # Définition des catégories et mots-clés de base
    categories = {
        'Comptabilité Générale': [
            'comptabilité générale',
            'plan comptable',
            'écritures comptables',
            'bilan comptable',
            'compte de résultat',
            'grand livre',
            'journal comptable',
            'amortissements',
            'provisions',
            'immobilisations'
        ],
        'Fiscalité des Entreprises': [
            'TVA',
            'impôt sur les sociétés',
            'CVAE',
            'CFE',
            'fiscalité entreprise',
            'optimisation fiscale',
            'déductibilité',
            'régime fiscal',
            'imposition entreprise',
            'taxes entreprise'
        ],
        'Fiscalité des Particuliers': [
            'impôt sur le revenu',
            'IFI',
            'LMNP',
            'optimisation fiscale',
            'défiscalisation',
            'niches fiscales',
            'déclaration impôts',
            'calcul impôts',
            'réduction impôts',
            'fiscalité patrimoniale'
        ],
        'Social et Paie': [
            'DSN',
            'cotisations sociales',
            'bulletin de paie',
            'droit social',
            'paie',
            'charges sociales',
            'URSSAF',
            'retraite',
            'assurance maladie',
            'congés payés'
        ],
        'Audit et Contrôle': [
            'audit comptable',
            'audit légal',
            'commissariat aux comptes',
            'contrôle interne',
            'conformité',
            'audit fiscal',
            'vérification comptable',
            'certification comptable',
            'audit social',
            'contrôle URSSAF'
        ],
        'Droit des Sociétés': [
            'statuts société',
            'fusion entreprise',
            'apport société',
            'transformation société',
            'droit des sociétés',
            'création entreprise',
            'dissolution société',
            'liquidation',
            'conseil juridique',
            'formalités entreprises'
        ],
        'Comptabilité Internationale': [
            'IFRS',
            'US GAAP',
            'consolidation',
            'comptabilité internationale',
            'reporting international',
            'normes comptables',
            'conversion comptable',
            'filiales étrangères',
            'comptabilité groupe',
            'standards internationaux'
        ],
        'Tech et Outils Comptables': [
            'logiciel comptable',
            'automatisation comptabilité',
            'Power BI',
            'transformation digitale',
            'comptabilité cloud',
            'intelligence artificielle comptabilité',
            'blockchain comptabilité',
            'RPA comptabilité',
            'ERP comptable',
            'outils comptables'
        ]
    }
    
    all_keywords = []
    
    # Recherche pour chaque catégorie
    for category_name, base_keywords in categories.items():
        keywords = seo_research.research_keywords_for_category(category_name, base_keywords)
        all_keywords.extend(keywords)
    
    # Sauvegarde des résultats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"keywords_research_{timestamp}.csv"
    seo_research.save_keywords_to_csv(all_keywords, filename)
    
    # Génération d'idées de contenu
    content_ideas = seo_research.generate_content_ideas(all_keywords)
    
    # Sauvegarde des idées de contenu
    ideas_filename = f"content_ideas_{timestamp}.json"
    with open(ideas_filename, 'w', encoding='utf-8') as f:
        json.dump(content_ideas, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Idées de contenu sauvegardées dans {ideas_filename}")
    
    # Statistiques
    print(f"\n📊 Statistiques :")
    print(f"- Total mots-clés analysés : {len(all_keywords)}")
    print(f"- Idées de contenu générées : {len(content_ideas)}")
    print(f"- Mots-clés haute priorité : {len([k for k in all_keywords if k['search_volume'] >= 4])}")
    
    print(f"\n🎯 Prochaines étapes :")
    print("1. Analyser les mots-clés haute priorité")
    print("2. Créer du contenu pour les mots-clés ciblés")
    print("3. Optimiser les pages existantes")
    print("4. Surveiller les performances dans Google Search Console")

if __name__ == '__main__':
    main() 