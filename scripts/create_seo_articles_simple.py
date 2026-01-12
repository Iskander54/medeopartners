#!/usr/bin/env python3
"""
Script simplifié pour créer des articles SEO - utilise directement SQLite
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from datetime import datetime
import json

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'medeo', 'site.db')

# Articles SEO à créer
ARTICLES = [
    {
        "title": "TVA et obligations déclaratives : ce que les dirigeants doivent absolument savoir",
        "slug": "tva-obligations-declaratives-dirigeants",
        "excerpt": "La TVA représente un enjeu majeur pour les entreprises. Découvrez les obligations déclaratives essentielles que tout dirigeant doit maîtriser pour éviter les erreurs coûteuses et les sanctions fiscales.",
        "content": """# TVA et obligations déclaratives : ce que les dirigeants doivent absolument savoir

La Taxe sur la Valeur Ajoutée (TVA) constitue l'un des piliers du système fiscal français. Pour les dirigeants d'entreprise, maîtriser les obligations déclaratives liées à la TVA est essentiel pour éviter les erreurs, les pénalités et optimiser la gestion financière de leur structure. Cet article vous guide à travers les points clés que tout dirigeant doit connaître.

## Comprendre les mécanismes de la TVA

### Le principe de fonctionnement

La TVA est un impôt indirect qui s'applique à la plupart des biens et services vendus en France. Contrairement à une idée reçue, ce n'est pas l'entreprise qui paie la TVA, mais le consommateur final. L'entreprise joue le rôle de collecteur d'impôt pour le compte de l'État.

Le mécanisme fonctionne ainsi : votre entreprise facture la TVA à ses clients (TVA collectée) et récupère la TVA qu'elle a payée à ses fournisseurs (TVA déductible). La différence entre ces deux montants est reversée à l'administration fiscale ou récupérée si la TVA déductible est supérieure.

### Les différents taux de TVA

En France, plusieurs taux de TVA coexistent :

- **Taux normal à 20%** : applicable à la majorité des biens et services
- **Taux réduit à 10%** : restauration, transports de voyageurs, travaux de rénovation immobilière
- **Taux réduit à 5,5%** : produits alimentaires, livres, énergies renouvelables
- **Taux super-réduit à 2,1%** : médicaments remboursables, presse

L'identification du bon taux est cruciale car une erreur peut entraîner des régularisations et des pénalités.

## Les obligations déclaratives selon le régime

### Le régime de la franchise en base

Les entreprises dont le chiffre d'affaires HT est inférieur à certains seuils peuvent bénéficier de la franchise en base de TVA. Dans ce cas, elles ne facturent pas la TVA et ne peuvent pas la récupérer. Les seuils sont de 85 800 € pour les activités de vente et 34 400 € pour les prestations de services.

**Avantages** : simplification administrative, pas de déclaration de TVA à effectuer.

**Inconvénients** : impossibilité de récupérer la TVA sur les achats, ce qui peut représenter un coût réel pour l'entreprise.

### Le régime réel simplifié

Ce régime s'applique aux entreprises dont le chiffre d'affaires HT est compris entre les seuils de la franchise et 818 000 € pour les ventes (ou 247 000 € pour les services).

**Obligations** :
- Déclaration annuelle CA12 avant le 2e jour ouvré suivant le 1er mai
- Acomptes semestriels en juillet et décembre
- Tenue d'un livre des recettes ou d'une comptabilité complète selon l'activité

### Le régime réel normal

Obligatoire pour les entreprises dépassant les seuils du régime simplifié, ce régime impose :

- **Déclaration mensuelle** (CA3) avant le 25 du mois suivant
- Possibilité de déclaration trimestrielle sous certaines conditions
- Tenue d'une comptabilité complète avec livre d'achats et livre de ventes
- Conservation de tous les justificatifs (factures, bons de livraison, etc.)

## Les erreurs fréquentes à éviter

### Erreur n°1 : Oublier de déclarer la TVA

L'oubli de déclaration entraîne automatiquement une majoration de 10% du montant dû, plus des intérêts de retard. En cas de récidive, les sanctions peuvent être alourdies.

**Conseil** : Mettez en place un calendrier fiscal avec des alertes pour ne jamais manquer une échéance.

### Erreur n°2 : Appliquer le mauvais taux

L'application d'un taux incorrect peut sembler anodine mais peut générer des régularisations importantes sur plusieurs années. L'administration fiscale peut remonter jusqu'à trois ans en arrière.

**Conseil** : En cas de doute sur le taux applicable, consultez un expert-comptable ou vérifiez directement auprès de l'administration fiscale.

### Erreur n°3 : Ne pas conserver les justificatifs

Toute TVA déductible doit être justifiée par une facture originale. L'absence de justificatif peut entraîner le rejet de la déduction et donc un coût supplémentaire.

**Conseil** : Organisez un archivage systématique et sécurisé de toutes vos factures, de préférence en version dématérialisée.

### Erreur n°4 : Confondre TVA collectée et TVA déductible

Cette confusion peut mener à des déclarations erronées et à des régularisations coûteuses. La TVA collectée correspond à ce que vous facturez à vos clients, tandis que la TVA déductible correspond à ce que vous payez à vos fournisseurs.

## Les points de vigilance particuliers

### Les opérations intracommunautaires

Si votre entreprise réalise des opérations avec d'autres pays de l'Union Européenne, des obligations spécifiques s'appliquent :

- Déclaration récapitulative (DEB) pour les livraisons intracommunautaires
- Numéro de TVA intracommunautaire obligatoire
- Règles particulières pour les prestations de services

### Les factures électroniques

Depuis 2024, la facturation électronique devient progressivement obligatoire. Cette évolution impacte directement la gestion de la TVA et nécessite une adaptation des processus.

### Le crédit de TVA

Lorsque la TVA déductible dépasse la TVA collectée, votre entreprise dispose d'un crédit de TVA. Vous pouvez soit le reporter sur les déclarations suivantes, soit demander son remboursement sous certaines conditions.

## Optimisation et conseils pratiques

### Anticiper les échéances

La gestion de la TVA nécessite une organisation rigoureuse. Prévoyez un calendrier fiscal et préparez vos déclarations en amont pour éviter les oublis et les erreurs de dernière minute.

### Utiliser un logiciel de comptabilité adapté

Un logiciel de comptabilité moderne vous aide à :
- Calculer automatiquement la TVA
- Générer les déclarations
- Conserver les justificatifs de manière organisée
- Suivre les échéances

### Faire appel à un expert-comptable

La complexité de la TVA justifie souvent l'intervention d'un professionnel. Un expert-comptable peut :
- Vous conseiller sur le régime le plus adapté
- Préparer et déposer vos déclarations
- Optimiser votre gestion de la TVA
- Vous représenter en cas de contrôle fiscal

## Conclusion

La maîtrise des obligations déclaratives de TVA est un enjeu majeur pour tout dirigeant d'entreprise. Les erreurs peuvent être coûteuses et les sanctions sévères. Une bonne organisation, une compréhension claire des mécanismes et, le cas échéant, l'accompagnement d'un expert-comptable, vous permettront de gérer sereinement cette obligation fiscale.

N'hésitez pas à consulter un cabinet d'expertise comptable pour bénéficier d'un accompagnement personnalisé et sécuriser votre gestion de la TVA. Un professionnel pourra analyser votre situation spécifique et vous proposer les solutions les plus adaptées à votre activité.""",
        "focus_keyword": "TVA obligations déclaratives",
        "secondary_keywords": json.dumps([
            "déclaration TVA",
            "régime TVA",
            "TVA déductible",
            "TVA collectée",
            "franchise en base TVA",
            "régime réel simplifié",
            "déclaration CA3",
            "expert comptable TVA"
        ]),
        "meta_title": "TVA et obligations déclaratives : guide complet pour dirigeants",
        "meta_description": "Découvrez tout ce que les dirigeants doivent savoir sur la TVA et les obligations déclaratives. Régimes, échéances, erreurs à éviter et conseils d'experts.",
        "category_name": "Fiscalité",
        "category_slug": "fiscalite",
        "tags": ["TVA", "Fiscalité", "Obligations fiscales", "Déclarations"]
    },
    {
        "title": "Création d'entreprise : erreurs comptables et fiscales à éviter dès la première année",
        "slug": "creation-entreprise-erreurs-comptables-fiscales-premiere-annee",
        "excerpt": "La première année d'activité est déterminante. Découvrez les erreurs comptables et fiscales les plus fréquentes commises par les nouveaux entrepreneurs et comment les éviter pour sécuriser votre projet.",
        "content": """# Création d'entreprise : erreurs comptables et fiscales à éviter dès la première année

La création d'une entreprise représente une aventure passionnante mais également un défi administratif et fiscal de taille. La première année d'activité est souvent déterminante pour l'avenir de l'entreprise. Malheureusement, de nombreux entrepreneurs commettent des erreurs comptables et fiscales qui peuvent compromettre leur projet dès le départ. Cet article vous aide à identifier et éviter ces pièges courants.

## L'importance d'un démarrage bien préparé

### Les enjeux de la première année

La première année d'activité pose les fondations de votre entreprise. Les décisions prises durant cette période impactent directement :
- La santé financière de l'entreprise
- Les relations avec l'administration fiscale
- La capacité de l'entreprise à se développer
- La tranquillité d'esprit du dirigeant

Une mauvaise gestion dès le départ peut créer des difficultés difficiles à rattraper par la suite.

## Erreur n°1 : Ne pas tenir de comptabilité dès le premier jour

### Le problème

Beaucoup d'entrepreneurs pensent qu'ils peuvent "rattraper" la comptabilité plus tard, une fois que l'activité sera lancée. Cette approche est une grave erreur.

### Les conséquences

- Perte de justificatifs essentiels
- Impossibilité de suivre la trésorerie réelle
- Difficultés pour établir les déclarations fiscales
- Risque de redressement fiscal
- Perte de temps considérable pour reconstituer les écritures

### La solution

Mettez en place votre comptabilité dès le premier jour d'activité :
- Ouvrez un compte bancaire professionnel dédié
- Tenez un livre des recettes ou une comptabilité complète selon votre régime
- Conservez tous les justificatifs (factures, notes de frais, relevés bancaires)
- Utilisez un logiciel de comptabilité adapté ou faites appel à un expert-comptable

## Erreur n°2 : Confondre compte personnel et compte professionnel

### Le problème

Mélanger les finances personnelles et professionnelles est l'une des erreurs les plus fréquentes chez les nouveaux entrepreneurs, notamment pour les micro-entreprises et les auto-entrepreneurs.

### Les conséquences

- Difficultés pour justifier les dépenses professionnelles
- Risque de rejet de certaines déductions fiscales
- Confusion dans la gestion de la trésorerie
- Complications en cas de contrôle fiscal
- Perte de la protection du patrimoine personnel (pour certaines structures)

### La solution

Séparez strictement vos comptes :
- Ouvrez un compte bancaire professionnel exclusivement dédié à l'activité
- N'utilisez jamais votre compte personnel pour des dépenses professionnelles
- Tenez un carnet de notes de frais pour les dépenses mixtes
- Documentez chaque mouvement financier

## Erreur n°3 : Sous-estimer les obligations fiscales

### Le problème

Les nouveaux entrepreneurs sous-estiment souvent la complexité et la fréquence des déclarations fiscales. Ils pensent pouvoir gérer seuls ces obligations.

### Les conséquences

- Oubli de déclarations entraînant des pénalités
- Erreurs dans les calculs fiscaux
- Paiements tardifs avec intérêts de retard
- Stress et perte de temps considérable
- Risque de redressement fiscal

### Les principales obligations à connaître

**Pour toutes les entreprises** :
- Déclaration de résultat (BIC, BNC ou IS selon le statut)
- Déclaration de TVA (selon le régime)
- Déclaration des charges sociales (URSSAF)
- Déclaration CFE (Cotisation Foncière des Entreprises)

**Selon l'activité** :
- Déclarations spécifiques (CVAE, taxe d'apprentissage, etc.)
- Obligations sociales (déclarations DSN si salariés)

### La solution

- Informez-vous sur toutes vos obligations avant le démarrage
- Consultez un expert-comptable pour comprendre votre calendrier fiscal
- Utilisez un agenda fiscal avec alertes
- Faites appel à un professionnel pour la préparation des déclarations

## Erreur n°4 : Mal choisir son régime fiscal

### Le problème

Le choix du régime fiscal (micro-entreprise, réel simplifié, réel normal) impacte directement :
- Le montant des impôts à payer
- Les obligations déclaratives
- La possibilité de déduire certaines charges
- La gestion administrative

Un mauvais choix peut coûter cher à l'entreprise.

### Les points à considérer

**Micro-entreprise (auto-entrepreneur)** :
- Avantages : simplicité, pas de comptabilité
- Inconvénients : abattements forfaitaires, pas de déduction des charges réelles
- Adapté pour : activités avec peu de charges

**Régime réel simplifié** :
- Avantages : déduction des charges réelles, déclarations simplifiées
- Inconvénients : comptabilité obligatoire
- Adapté pour : entreprises avec charges importantes

**Régime réel normal** :
- Avantages : déduction complète, optimisation fiscale possible
- Inconvénients : comptabilité complète, déclarations fréquentes
- Adapté pour : entreprises importantes ou avec besoins spécifiques

### La solution

Analysez votre situation avec un expert-comptable avant le démarrage. Il pourra :
- Évaluer vos charges prévisionnelles
- Comparer les différents régimes
- Vous conseiller sur le choix le plus avantageux
- Vous accompagner dans les démarches

## Erreur n°5 : Ne pas prévoir les charges sociales et fiscales

### Le problème

Beaucoup d'entrepreneurs se concentrent sur le chiffre d'affaires sans anticiper les charges à venir. Ils se retrouvent ensuite en difficulté de trésorerie.

### Les charges à anticiper

**Charges sociales** (pour les dirigeants) :
- Cotisations sociales sur les revenus
- CSG/CRDS
- Cotisations retraite complémentaire

**Impôts** :
- Impôt sur le revenu (BIC/BNC) ou impôt sur les sociétés (IS)
- TVA à reverser
- CFE et autres taxes

**Autres charges** :
- Frais de comptabilité
- Assurances professionnelles
- Frais bancaires

### La solution

- Établissez un budget prévisionnel incluant toutes les charges
- Mettez de côté chaque mois une provision pour les impôts et charges sociales
- Consultez un expert-comptable pour estimer vos charges réelles
- Utilisez un tableau de bord de trésorerie

## Erreur n°6 : Négliger la facturation et la gestion des créances

### Le problème

Une facturation tardive ou incomplète peut créer des difficultés de trésorerie majeures.

### Les conséquences

- Retards de paiement des clients
- Difficultés de trésorerie
- Perte de revenus en cas de non-paiement
- Problèmes de justification comptable

### La solution

- Facturez immédiatement après chaque prestation ou livraison
- Respectez les mentions obligatoires sur les factures
- Mettez en place un suivi rigoureux des créances
- Relancez systématiquement les clients en retard
- Utilisez des outils de gestion de facturation

## Erreur n°7 : Ne pas faire appel à un expert-comptable dès le départ

### Le problème

Beaucoup d'entrepreneurs pensent économiser en gérant seuls leur comptabilité au début. Cette approche est souvent contre-productive.

### Les avantages d'un expert-comptable dès le départ

**Conseil stratégique** :
- Choix du statut juridique optimal
- Optimisation fiscale
- Conseil sur la structure financière

**Gain de temps** :
- Vous vous concentrez sur votre cœur de métier
- Gestion administrative déléguée
- Déclarations préparées et déposées

**Sécurité** :
- Respect des obligations légales
- Réduction des risques d'erreurs
- Accompagnement en cas de contrôle

**Économies** :
- Optimisation fiscale souvent supérieure aux honoraires
- Évite les pénalités et erreurs coûteuses
- Meilleure gestion financière

### La solution

Consultez un cabinet d'expertise comptable dès la phase de création. Un professionnel pourra :
- Vous accompagner dans le choix de votre structure
- Vous conseiller sur les régimes fiscaux
- Mettre en place votre comptabilité
- Vous assister dans toutes vos démarches

## Checklist de la première année

Pour éviter les erreurs, suivez cette checklist :

- [ ] Comptabilité mise en place dès le premier jour
- [ ] Compte bancaire professionnel ouvert
- [ ] Séparation stricte des comptes personnels et professionnels
- [ ] Calendrier fiscal établi avec toutes les échéances
- [ ] Régime fiscal choisi avec conseil professionnel
- [ ] Budget prévisionnel établi incluant toutes les charges
- [ ] Système de facturation mis en place
- [ ] Archivage organisé de tous les justificatifs
- [ ] Expert-comptable consulté ou mandaté
- [ ] Assurances professionnelles souscrites

## Conclusion

La première année d'activité est cruciale pour l'avenir de votre entreprise. Les erreurs comptables et fiscales peuvent compromettre votre projet dès le départ. En étant bien préparé, en respectant les obligations légales et en vous faisant accompagner par des professionnels, vous mettez toutes les chances de votre côté pour réussir.

N'hésitez pas à consulter un cabinet d'expertise comptable dès la création de votre entreprise. Un accompagnement professionnel dès le départ vous permettra d'éviter les erreurs coûteuses et de vous concentrer sur le développement de votre activité.""",
        "focus_keyword": "création entreprise erreurs comptables",
        "secondary_keywords": json.dumps([
            "erreurs fiscales création entreprise",
            "première année entreprise",
            "comptabilité création entreprise",
            "expert comptable création entreprise",
            "obligations fiscales entreprise",
            "régime fiscal entreprise",
            "démarrage entreprise",
            "conseil création entreprise"
        ]),
        "meta_title": "Création d'entreprise : erreurs comptables et fiscales à éviter",
        "meta_description": "Découvrez les 7 erreurs comptables et fiscales les plus fréquentes lors de la création d'entreprise et comment les éviter pour sécuriser votre projet dès la première année.",
        "category_name": "Création d'entreprise",
        "category_slug": "creation-entreprise",
        "tags": ["Création d'entreprise", "Comptabilité", "Fiscalité", "Conseil"]
    }
]

def create_articles():
    """Crée les articles dans la base de données SQLite"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée : {DB_PATH}")
        print("💡 Veuillez d'abord lancer l'application pour créer la base de données.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si les tables existent
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blog_category'")
    if not cursor.fetchone():
        print("❌ Les tables du blog n'existent pas. Veuillez d'abord créer les tables.")
        conn.close()
        return
    
    # Créer les catégories si elles n'existent pas
    for article_data in ARTICLES:
        category_slug = article_data["category_slug"]
        category_name = article_data["category_name"]
        
        cursor.execute("SELECT id FROM blog_category WHERE slug = ?", (category_slug,))
        category = cursor.fetchone()
        
        if not category:
            cursor.execute("""
                INSERT INTO blog_category (name, slug, description, meta_description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (category_name, category_slug, f"Articles sur {category_name}", 
                  f"Découvrez nos articles sur {category_name}", datetime.now()))
            category_id = cursor.lastrowid
            print(f"✅ Catégorie créée : {category_name}")
        else:
            category_id = category[0]
        
        # Vérifier si l'article existe déjà
        cursor.execute("SELECT id FROM blog_article WHERE slug = ?", (article_data["slug"],))
        if cursor.fetchone():
            print(f"⚠️  Article déjà existant : {article_data['title']}")
            continue
        
        # Calculer le temps de lecture
        word_count = len(article_data["content"].split())
        reading_time = max(1, word_count // 200)
        
        # Créer l'article
        cursor.execute("""
            INSERT INTO blog_article 
            (title, slug, excerpt, content, focus_keyword, secondary_keywords, 
             meta_title, meta_description, status, published_at, category_id, 
             reading_time, view_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_data["title"],
            article_data["slug"],
            article_data["excerpt"],
            article_data["content"],
            article_data["focus_keyword"],
            article_data["secondary_keywords"],
            article_data["meta_title"],
            article_data["meta_description"],
            "published",
            datetime.now(),
            category_id,
            reading_time,
            0,
            datetime.now(),
            datetime.now()
        ))
        
        article_id = cursor.lastrowid
        
        # Créer les tags et les associer
        for tag_name in article_data["tags"]:
            tag_slug = tag_name.lower().replace(' ', '-').replace("'", '-')
            
            # Vérifier si le tag existe
            cursor.execute("SELECT id FROM blog_tag WHERE slug = ?", (tag_slug,))
            tag = cursor.fetchone()
            
            if not tag:
                cursor.execute("""
                    INSERT INTO blog_tag (name, slug, description)
                    VALUES (?, ?, ?)
                """, (tag_name, tag_slug, f"Articles taggés {tag_name}"))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag[0]
            
            # Associer le tag à l'article
            cursor.execute("""
                INSERT INTO article_tags (article_id, tag_id)
                VALUES (?, ?)
            """, (article_id, tag_id))
        
        conn.commit()
        print(f"✅ Article créé : {article_data['title']}")
        print(f"   - Slug : {article_data['slug']}")
        print(f"   - Catégorie : {category_name}")
        print(f"   - Temps de lecture : {reading_time} min")
        print(f"   - Mots : {word_count}")
        print()
    
    conn.close()
    print("🎉 Création des articles terminée !")

if __name__ == "__main__":
    create_articles()

