#!/usr/bin/env python3
"""
Script de monitoring SEO pour le blog comptabilité/fiscalité
Surveille les performances, les mots-clés et génère des rapports
"""

import requests
import json
import csv
import time
from datetime import datetime, timedelta
import sys
import os
from bs4 import BeautifulSoup
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from medeo import create_app, db
from medeo.models import BlogArticle, KeywordResearch

class SEOMonitor:
    def __init__(self):
        self.app = create_app()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def check_article_seo(self, article):
        """Vérifie l'optimisation SEO d'un article"""
        issues = []
        score = 100
        
        # Vérifier la longueur du titre
        if len(article.title) < 30:
            issues.append("Titre trop court")
            score -= 10
        elif len(article.title) > 60:
            issues.append("Titre trop long")
            score -= 5
            
        # Vérifier la meta description
        if article.meta_description:
            if len(article.meta_description) < 120:
                issues.append("Meta description trop courte")
                score -= 10
            elif len(article.meta_description) > 160:
                issues.append("Meta description trop longue")
                score -= 5
        else:
            issues.append("Meta description manquante")
            score -= 15
            
        # Vérifier le mot-clé principal
        if not article.focus_keyword:
            issues.append("Mot-clé principal manquant")
            score -= 20
            
        # Vérifier la longueur du contenu
        content_length = len(article.content)
        if content_length < 300:
            issues.append("Contenu trop court")
            score -= 15
        elif content_length > 3000:
            issues.append("Contenu très long")
            score -= 5
            
        # Vérifier la densité des mots-clés
        if article.focus_keyword and article.content:
            keyword_density = article.content.lower().count(article.focus_keyword.lower()) / len(article.content.split()) * 100
            if keyword_density < 0.5:
                issues.append("Densité du mot-clé principal trop faible")
                score -= 10
            elif keyword_density > 3:
                issues.append("Densité du mot-clé principal trop élevée")
                score -= 10
                
        return {
            'score': max(0, score),
            'issues': issues,
            'content_length': content_length,
            'keyword_density': keyword_density if article.focus_keyword else 0
        }
    
    def check_google_indexing(self, url):
        """Vérifie si une URL est indexée par Google"""
        try:
            search_query = f'site:{url}'
            response = self.session.get(
                'https://www.google.com/search',
                params={'q': search_query, 'num': 1}
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find_all('div', class_='g')
                return len(results) > 0
                
        except Exception as e:
            print(f"Erreur vérification indexation Google : {e}")
            
        return False
    
    def check_page_speed(self, url):
        """Vérifie la vitesse de chargement d'une page"""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            load_time = time.time() - start_time
            
            return {
                'load_time': load_time,
                'status_code': response.status_code,
                'size': len(response.content)
            }
            
        except Exception as e:
            print(f"Erreur vérification vitesse : {e}")
            return None
    
    def analyze_keyword_positions(self):
        """Analyse les positions des mots-clés ciblés"""
        with self.app.app_context():
            keywords = KeywordResearch.query.all()
            
            for keyword in keywords:
                try:
                    # Recherche Google simulée (version basique)
                    search_query = keyword.keyword
                    response = self.session.get(
                        'https://www.google.com/search',
                        params={'q': search_query, 'num': 10}
                    )
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        results = soup.find_all('div', class_='g')
                        
                        # Chercher le site dans les résultats
                        position = None
                        for i, result in enumerate(results, 1):
                            link = result.find('a')
                            if link and 'medeo-partners.com' in link.get('href', ''):
                                position = i
                                break
                        
                        # Mettre à jour la position
                        keyword.current_position = position
                        keyword.last_checked = datetime.now()
                        
                except Exception as e:
                    print(f"Erreur analyse position {keyword.keyword}: {e}")
                    continue
                    
                time.sleep(2)  # Pause pour éviter le rate limiting
            
            db.session.commit()
    
    def generate_seo_report(self):
        """Génère un rapport SEO complet"""
        with self.app.app_context():
            articles = BlogArticle.query.filter_by(status='published').all()
            
            report = {
                'date': datetime.now().isoformat(),
                'total_articles': len(articles),
                'articles_analyzed': 0,
                'average_seo_score': 0,
                'issues_found': [],
                'recommendations': []
            }
            
            total_score = 0
            all_issues = []
            
            for article in articles:
                seo_analysis = self.check_article_seo(article)
                total_score += seo_analysis['score']
                all_issues.extend(seo_analysis['issues'])
                report['articles_analyzed'] += 1
                
                # Vérifier l'indexation
                article_url = f"https://medeo-partners.com/fr/blog/article/{article.slug}"
                is_indexed = self.check_google_indexing(article_url)
                
                # Vérifier la vitesse
                speed_data = self.check_page_speed(article_url)
                
                print(f"Article: {article.title}")
                print(f"  - Score SEO: {seo_analysis['score']}/100")
                print(f"  - Indexé Google: {'Oui' if is_indexed else 'Non'}")
                if speed_data:
                    print(f"  - Temps de chargement: {speed_data['load_time']:.2f}s")
                print(f"  - Problèmes: {', '.join(seo_analysis['issues']) if seo_analysis['issues'] else 'Aucun'}")
                print()
                
                time.sleep(1)  # Pause entre les vérifications
            
            if report['articles_analyzed'] > 0:
                report['average_seo_score'] = total_score / report['articles_analyzed']
            
            # Analyser les problèmes les plus fréquents
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            report['top_issues'] = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Générer des recommandations
            if report['average_seo_score'] < 70:
                report['recommendations'].append("Améliorer l'optimisation SEO globale des articles")
            
            if any('Meta description manquante' in issue for issue in all_issues):
                report['recommendations'].append("Ajouter des meta descriptions à tous les articles")
                
            if any('Mot-clé principal manquant' in issue for issue in all_issues):
                report['recommendations'].append("Définir des mots-clés principaux pour tous les articles")
            
            return report
    
    def save_report_to_csv(self, report, filename):
        """Sauvegarde le rapport en CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'total_articles', 'articles_analyzed', 'average_seo_score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow({
                'date': report['date'],
                'total_articles': report['total_articles'],
                'articles_analyzed': report['articles_analyzed'],
                'average_seo_score': report['average_seo_score']
            })
        
        print(f"✅ Rapport sauvegardé dans {filename}")
    
    def send_email_report(self, report, recipient_email):
        """Envoie le rapport par email"""
        try:
            # Configuration email (à adapter selon votre configuration)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not all([smtp_user, smtp_password]):
                print("⚠ Configuration email manquante")
                return
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = f"Rapport SEO - {datetime.now().strftime('%d/%m/%Y')}"
            
            # Corps du message
            body = f"""
            <html>
            <body>
                <h2>Rapport SEO - Blog Medeo Partners</h2>
                <p><strong>Date :</strong> {report['date']}</p>
                
                <h3>Statistiques générales</h3>
                <ul>
                    <li>Total articles : {report['total_articles']}</li>
                    <li>Articles analysés : {report['articles_analyzed']}</li>
                    <li>Score SEO moyen : {report['average_seo_score']:.1f}/100</li>
                </ul>
                
                <h3>Problèmes principaux</h3>
                <ul>
            """
            
            for issue, count in report.get('top_issues', []):
                body += f"<li>{issue} : {count} occurrences</li>"
            
            body += """
                </ul>
                
                <h3>Recommandations</h3>
                <ul>
            """
            
            for recommendation in report.get('recommendations', []):
                body += f"<li>{recommendation}</li>"
            
            body += """
                </ul>
                
                <p>Ce rapport a été généré automatiquement par le système de monitoring SEO.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Envoyer l'email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Rapport envoyé à {recipient_email}")
            
        except Exception as e:
            print(f"❌ Erreur envoi email : {e}")

def main():
    """Fonction principale"""
    print("=== MONITORING SEO - BLOG COMPTABILITÉ ===\n")
    
    monitor = SEOMonitor()
    
    # Menu interactif
    while True:
        print("\nOptions disponibles :")
        print("1. Analyser tous les articles")
        print("2. Vérifier les positions des mots-clés")
        print("3. Générer rapport complet")
        print("4. Envoyer rapport par email")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5) : ")
        
        if choice == '1':
            print("\n🔍 Analyse des articles en cours...")
            report = monitor.generate_seo_report()
            
            print(f"\n📊 Résultats :")
            print(f"- Articles analysés : {report['articles_analyzed']}")
            print(f"- Score SEO moyen : {report['average_seo_score']:.1f}/100")
            print(f"- Problèmes principaux :")
            for issue, count in report.get('top_issues', []):
                print(f"  • {issue} : {count} occurrences")
            
        elif choice == '2':
            print("\n🔍 Vérification des positions des mots-clés...")
            monitor.analyze_keyword_positions()
            print("✅ Positions mises à jour")
            
        elif choice == '3':
            print("\n📊 Génération du rapport complet...")
            report = monitor.generate_seo_report()
            
            # Sauvegarder le rapport
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"seo_report_{timestamp}.csv"
            monitor.save_report_to_csv(report, filename)
            
            # Sauvegarder aussi en JSON
            json_filename = f"seo_report_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Rapport JSON sauvegardé dans {json_filename}")
            
        elif choice == '4':
            email = input("Email du destinataire : ")
            if email:
                print("\n📊 Génération et envoi du rapport...")
                report = monitor.generate_seo_report()
                monitor.send_email_report(report, email)
            else:
                print("❌ Email invalide")
                
        elif choice == '5':
            print("Au revoir !")
            break
            
        else:
            print("Choix invalide")

if __name__ == '__main__':
    main() 