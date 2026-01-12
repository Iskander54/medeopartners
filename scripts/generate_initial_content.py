#!/usr/bin/env python3
"""
Script de génération de contenu initial pour le blog Medeo Partners
Génère des articles optimisés SEO dans les domaines comptabilité/fiscalité
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from medeo import create_app, db
from medeo.models import BlogCategory, BlogArticle, BlogTag, User
from datetime import datetime
import json
import re
from slugify import slugify

app = create_app()

# Configuration des catégories principales (silos SEO)
CATEGORIES = {
    'comptabilite-generale': {
        'name': 'Comptabilité Générale',
        'description': 'Guides et conseils sur la comptabilité générale, plan comptable, écritures comptables',
        'seo_title': 'Comptabilité Générale - Guides et Conseils d\'Expert',
        'meta_description': 'Découvrez nos guides pratiques en comptabilité générale. Plan comptable, écritures, amortissements et conseils d\'experts.'
    },
    'fiscalite-entreprises': {
        'name': 'Fiscalité des Entreprises',
        'description': 'TVA, Impôt sur les Sociétés, CVAE, CFE et optimisation fiscale',
        'seo_title': 'Fiscalité des Entreprises - Optimisation et Conformité',
        'meta_description': 'Expertise en fiscalité des entreprises : TVA, IS, CVAE, CFE. Conseils d\'optimisation et conformité fiscale.'
    },
    'fiscalite-particuliers': {
        'name': 'Fiscalité des Particuliers',
        'description': 'Impôt sur le Revenu, IFI, LMNP, optimisation fiscale personnelle',
        'seo_title': 'Fiscalité des Particuliers - Optimisation IR et IFI',
        'meta_description': 'Conseils en fiscalité des particuliers : IR, IFI, LMNP. Optimisation fiscale et défiscalisation.'
    },
    'social-paie': {
        'name': 'Social et Paie',
        'description': 'DSN, cotisations sociales, bulletins de paie, droit social',
        'seo_title': 'Social et Paie - DSN et Gestion RH',
        'meta_description': 'Expertise en droit social et paie : DSN, cotisations, bulletins de paie et conformité sociale.'
    },
    'audit-controle': {
        'name': 'Audit et Contrôle',
        'description': 'Audit légal, CAC, NEP, contrôle interne et conformité',
        'seo_title': 'Audit et Contrôle - Conformité et Transparence',
        'meta_description': 'Services d\'audit et contrôle : audit légal, CAC, NEP et conformité réglementaire.'
    },
    'droit-societes': {
        'name': 'Droit des Sociétés',
        'description': 'Statuts, fusion, apport, transformation et conseil juridique',
        'seo_title': 'Droit des Sociétés - Conseil Juridique d\'Expert',
        'meta_description': 'Conseil en droit des sociétés : statuts, fusion, apport et transformation d\'entreprise.'
    },
    'comptabilite-internationale': {
        'name': 'Comptabilité Internationale',
        'description': 'IFRS, normes US GAAP, consolidation et reporting international',
        'seo_title': 'Comptabilité Internationale - IFRS et Reporting Global',
        'meta_description': 'Expertise en comptabilité internationale : IFRS, US GAAP, consolidation et reporting global.'
    },
    'tech-outils': {
        'name': 'Tech et Outils Comptables',
        'description': 'Logiciels comptables, automatisation, Power BI et transformation digitale',
        'seo_title': 'Tech et Outils Comptables - Transformation Digitale',
        'meta_description': 'Solutions technologiques pour la comptabilité : logiciels, automatisation et transformation digitale.'
    }
}

# Articles initiaux par catégorie
ARTICLES_DATA = {
    'comptabilite-generale': [
        {
            'title': 'Comment comptabiliser une facture fournisseur en 2024',
            'excerpt': 'Guide complet pour comptabiliser correctement vos factures fournisseurs selon le plan comptable français.',
            'focus_keyword': 'comptabiliser facture fournisseur',
            'secondary_keywords': ['écriture comptable', 'plan comptable', 'comptabilité générale'],
            'content': '''
<h2>Les bases de la comptabilisation d'une facture fournisseur</h2>
<p>La comptabilisation d'une facture fournisseur est une opération fondamentale en comptabilité. Elle permet d'enregistrer les dettes envers vos fournisseurs et de respecter le principe de sincérité comptable.</p>

<h3>Écriture comptable standard</h3>
<p>L'écriture comptable pour une facture fournisseur se présente généralement ainsi :</p>
<ul>
<li>Débit : Compte 606 (Achats de fournitures d'entretien et petit équipement) ou 607 (Achats de fournitures d'exploitation)</li>
<li>Débit : Compte 4456 (État - Taxes sur le chiffre d'affaires déductibles)</li>
<li>Crédit : Compte 401 (Fournisseurs)</li>
</ul>

<h3>Cas particuliers à connaître</h3>
<p>Selon la nature de l'achat, vous utiliserez différents comptes :</p>
<ul>
<li>Compte 601 : Achats stockés - Matières premières</li>
<li>Compte 602 : Achats stockés - Autres approvisionnements</li>
<li>Compte 603 : Achats stockés - Fournitures d'entretien et petit équipement</li>
<li>Compte 604 : Achats d'études, prestations de services</li>
<li>Compte 605 : Achats de matériel, équipements et travaux</li>
</ul>

<h2>FAQ sur la comptabilisation des factures</h2>
<h3>Que faire en cas de facture rectificative ?</h3>
<p>Une facture rectificative doit être comptabilisée en contre-passation de l'écriture initiale, puis enregistrée avec la nouvelle écriture correcte.</p>

<h3>Comment gérer les acomptes fournisseurs ?</h3>
<p>Les acomptes sont comptabilisés sur le compte 4091 (Fournisseurs - Acomptes versés sur commandes) et sont ensuite imputés sur la facture définitive.</p>
            ''',
            'meta_title': 'Comment comptabiliser une facture fournisseur en 2024 - Guide Complet',
            'meta_description': 'Guide pratique pour comptabiliser correctement vos factures fournisseurs. Écritures comptables, plan comptable et conseils d\'expert.'
        },
        {
            'title': 'Les amortissements comptables : guide complet 2024',
            'excerpt': 'Tout savoir sur les amortissements comptables : méthodes, durées et impact fiscal.',
            'focus_keyword': 'amortissements comptables',
            'secondary_keywords': ['amortissement linéaire', 'amortissement dégressif', 'immobilisations'],
            'content': '''
<h2>Définition et principe des amortissements</h2>
<p>L'amortissement comptable représente la constatation comptable de la dépréciation d'un bien immobilisé résultant de l'usage, du temps, du changement de technique ou de toute autre cause.</p>

<h3>Les différents types d'amortissements</h3>
<ul>
<li><strong>Amortissement linéaire</strong> : répartition constante sur la durée d'utilisation</li>
<li><strong>Amortissement dégressif</strong> : dégressivité selon un coefficient fiscal</li>
<li><strong>Amortissement exceptionnel</strong> : pour certains investissements spécifiques</li>
</ul>

<h2>Durées d'amortissement par type de bien</h2>
<table>
<tr><th>Type de bien</th><th>Durée fiscale</th><th>Durée comptable</th></tr>
<tr><td>Bâtiments industriels</td><td>20 ans</td><td>20-50 ans</td></tr>
<tr><td>Matériel informatique</td><td>3-5 ans</td><td>3-5 ans</td></tr>
<tr><td>Véhicules</td><td>4-5 ans</td><td>4-5 ans</td></tr>
<tr><td>Mobilier</td><td>10 ans</td><td>10 ans</td></tr>
</table>

<h3>Calcul de l'amortissement linéaire</h3>
<p>Formule : (Valeur d'origine - Valeur résiduelle) / Durée d'utilisation</p>

<h2>Impact fiscal des amortissements</h2>
<p>Les amortissements comptables sont déductibles fiscalement sous certaines conditions :</p>
<ul>
<li>Le bien doit être affecté à l'exploitation</li>
<li>L'amortissement doit être justifié</li>
<li>Respect des durées fiscales minimales</li>
</ul>
            ''',
            'meta_title': 'Les amortissements comptables : guide complet 2024 - Expert Comptable',
            'meta_description': 'Guide complet sur les amortissements comptables : méthodes, durées, calcul et impact fiscal. Conseils d\'expert comptable.'
        }
    ],
    'fiscalite-entreprises': [
        {
            'title': 'TVA 2024 : les nouvelles règles à connaître',
            'excerpt': 'Découvrez les principales évolutions de la TVA en 2024 et leurs impacts sur votre entreprise.',
            'focus_keyword': 'TVA 2024',
            'secondary_keywords': ['taux TVA', 'déductibilité TVA', 'régime TVA'],
            'content': '''
<h2>Les taux de TVA en vigueur en 2024</h2>
<p>En 2024, les taux de TVA applicables en France sont :</p>
<ul>
<li><strong>Taux normal</strong> : 20% (majorité des biens et services)</li>
<li><strong>Taux réduit</strong> : 10% (restauration, transport, travaux d'amélioration)</li>
<li><strong>Taux super-réduit</strong> : 5,5% (produits alimentaires, livres, énergie)</li>
<li><strong>Taux particulier</strong> : 2,1% (médicaments remboursables, presse)</li>
</ul>

<h3>Nouvelles règles pour 2024</h3>
<p>Plusieurs évolutions importantes sont à noter :</p>
<ul>
<li>Extension du taux réduit à certains services numériques</li>
<li>Modification des règles de déductibilité pour les secteurs spécifiques</li>
<li>Nouvelles obligations de reporting électronique</li>
</ul>

<h2>Régimes de TVA</h2>
<h3>Régime de la franchise en base</h3>
<p>Applicable si le CA HT est inférieur à :</p>
<ul>
<li>85 800 € pour les prestations de services</li>
<li>34 400 € pour les ventes de biens</li>
</ul>

<h3>Régime réel simplifié</h3>
<p>Entre 85 800 € et 818 000 € de CA HT pour les prestations de services.</p>

<h3>Régime réel normal</h3>
<p>Au-delà de 818 000 € de CA HT pour les prestations de services.</p>

<h2>Déductibilité de la TVA</h2>
<p>La TVA est déductible sous conditions :</p>
<ul>
<li>Le bien/service doit être utilisé pour l'exploitation</li>
<li>La TVA doit être justifiée par une facture</li>
<li>Exclusion des dépenses de logement, de restauration et de transport</li>
</ul>
            ''',
            'meta_title': 'TVA 2024 : les nouvelles règles à connaître - Expert Fiscal',
            'meta_description': 'Découvrez les évolutions de la TVA en 2024 : taux, régimes, déductibilité. Conseils d\'expert fiscal pour votre entreprise.'
        }
    ],
    'fiscalite-particuliers': [
        {
            'title': 'Optimisation fiscale 2024 : les solutions pour réduire vos impôts',
            'excerpt': 'Découvrez les solutions légales d\'optimisation fiscale pour réduire votre imposition en 2024.',
            'focus_keyword': 'optimisation fiscale 2024',
            'secondary_keywords': ['défiscalisation', 'réduction impôts', 'niches fiscales'],
            'content': '''
<h2>Les principales solutions d'optimisation fiscale</h2>
<p>L'optimisation fiscale légale permet de réduire son imposition en utilisant les dispositifs prévus par la loi.</p>

<h3>Investissement locatif</h3>
<ul>
<li><strong>LMNP</strong> : Loueur Meublé Non Professionnel</li>
<li><strong>LMP</strong> : Loueur Meublé Professionnel</li>
<li><strong>Malraux</strong> : rénovation de logements anciens</li>
<li><strong>Denormandie</strong> : rénovation locative</li>
</ul>

<h3>Investissement d'entreprise</h3>
<ul>
<li><strong>FIP</strong> : Fonds d'Investissement de Proximité</li>
<li><strong>FCPI</strong> : Fonds Commun de Placement dans l'Innovation</li>
<li><strong>Girardin</strong> : investissement outre-mer</li>
</ul>

<h2>Réduction d'impôt sur le revenu</h2>
<h3>Dons aux associations</h3>
<p>Réduction de 66% du montant des dons dans la limite de 20% du revenu imposable.</p>

<h3>Services à la personne</h3>
<p>Crédit d'impôt de 50% sur les dépenses de services à la personne.</p>

<h3>Économies d'énergie</h3>
<p>Crédit d'impôt pour la transition énergétique (CITE) : 30% des dépenses.</p>

<h2>Optimisation de l'IFI</h2>
<p>L'Impôt sur la Fortune Immobilière peut être optimisé par :</p>
<ul>
<li>La donation-partage</li>
<li>L'usufruit temporaire</li>
<li>L'investissement dans l'immobilier locatif social</li>
</ul>

<h3>Seuils IFI 2024</h3>
<p>L'IFI s'applique aux patrimoines immobiliers nets supérieurs à 1 300 000 €.</p>
            ''',
            'meta_title': 'Optimisation fiscale 2024 : solutions pour réduire vos impôts',
            'meta_description': 'Découvrez les solutions légales d\'optimisation fiscale 2024 : investissements, réductions d\'impôts et conseils d\'expert.'
        }
    ]
}

def create_categories():
    """Créer les catégories principales du blog"""
    print("Création des catégories...")
    
    with app.app_context():
        for slug, data in CATEGORIES.items():
            category = BlogCategory.query.filter_by(slug=slug).first()
            if not category:
                category = BlogCategory(
                    name=data['name'],
                    slug=slug,
                    description=data['description'],
                    seo_title=data['seo_title'],
                    meta_description=data['meta_description']
                )
                db.session.add(category)
                print(f"✓ Catégorie créée : {data['name']}")
            else:
                print(f"⚠ Catégorie existante : {data['name']}")
        
        db.session.commit()
        print("Catégories créées avec succès !\n")

def create_articles():
    """Créer les articles initiaux"""
    print("Création des articles...")
    
    with app.app_context():
        # Récupérer un utilisateur pour l'auteur (ou créer un admin par défaut)
        author = User.query.first()
        if not author:
            print("⚠ Aucun utilisateur trouvé. Création d'un utilisateur admin...")
            author = User(
                email='admin@medeo-partners.com',
                password='admin123',  # À changer en production
                firstname='Admin',
                lastname='Medeo',
                dob=datetime(1990, 1, 1)
            )
            db.session.add(author)
            db.session.commit()
        
        for category_slug, articles in ARTICLES_DATA.items():
            category = BlogCategory.query.filter_by(slug=category_slug).first()
            if not category:
                print(f"⚠ Catégorie {category_slug} non trouvée, passage...")
                continue
            
            for article_data in articles:
                # Vérifier si l'article existe déjà
                existing = BlogArticle.query.filter_by(slug=slugify(article_data['title'])).first()
                if existing:
                    print(f"⚠ Article existant : {article_data['title']}")
                    continue
                
                # Créer l'article
                article = BlogArticle(
                    title=article_data['title'],
                    slug=slugify(article_data['title']),
                    excerpt=article_data['excerpt'],
                    content=article_data['content'],
                    focus_keyword=article_data['focus_keyword'],
                    secondary_keywords=json.dumps(article_data['secondary_keywords']),
                    meta_title=article_data.get('meta_title', article_data['title']),
                    meta_description=article_data.get('meta_description', article_data['excerpt']),
                    status='published',
                    published_at=datetime.now(),
                    category_id=category.id,
                    author_id=author.id,
                    reading_time=len(article_data['content'].split()) // 200  # Estimation
                )
                
                db.session.add(article)
                print(f"✓ Article créé : {article_data['title']}")
        
        db.session.commit()
        print("Articles créés avec succès !\n")

def create_tags():
    """Créer les tags principaux"""
    print("Création des tags...")
    
    tags_data = [
        'comptabilité', 'fiscalité', 'TVA', 'impôts', 'audit', 'social', 'paie',
        'droit des sociétés', 'IFRS', 'optimisation fiscale', 'amortissements',
        'facturation', 'trésorerie', 'consolidation', 'reporting'
    ]
    
    with app.app_context():
        for tag_name in tags_data:
            tag = BlogTag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = BlogTag(
                    name=tag_name,
                    slug=slugify(tag_name),
                    description=f'Articles sur {tag_name}'
                )
                db.session.add(tag)
                print(f"✓ Tag créé : {tag_name}")
            else:
                print(f"⚠ Tag existant : {tag_name}")
        
        db.session.commit()
        print("Tags créés avec succès !\n")

def main():
    """Fonction principale"""
    print("=== GÉNÉRATION DE CONTENU INITIAL DU BLOG ===\n")
    
    try:
        create_categories()
        create_tags()
        create_articles()
        
        print("✅ Génération terminée avec succès !")
        print("\nProchaines étapes :")
        print("1. Vérifier les articles dans l'interface d'administration")
        print("2. Ajouter des images pour chaque article")
        print("3. Configurer les redirections SEO")
        print("4. Soumettre le sitemap à Google Search Console")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        db.session.rollback()

if __name__ == '__main__':
    main() 