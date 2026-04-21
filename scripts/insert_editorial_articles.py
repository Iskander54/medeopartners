#!/usr/bin/env python3
"""
Script d'insertion du calendrier éditorial (12 articles SEO) en base de données.

Usage :
    cd /path/to/medeopartners
    python scripts/insert_editorial_articles.py

Ce script est idempotent : il ne duplique pas les articles dont le slug existe déjà.
"""

import sys
import os
from datetime import date, datetime

# Ajouter la racine du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from medeo import create_app, db
from medeo.models import BlogArticle, BlogCategory, BlogTag

app = create_app()


# ─────────────────────────────────────────────────────────────
# Données du calendrier éditorial
# ─────────────────────────────────────────────────────────────

CATEGORIES = [
    {'name': 'Fiscalité',      'slug': 'fiscalite',      'description': 'Actualités et conseils en fiscalité des entreprises et des particuliers.'},
    {'name': 'Comptabilité',   'slug': 'comptabilite',   'description': 'Guides pratiques en comptabilité générale et spécialisée.'},
    {'name': 'Création',       'slug': 'creation',       'description': 'Conseils pour créer et structurer votre entreprise.'},
    {'name': 'Social',         'slug': 'social',         'description': 'Paie, cotisations sociales, droit du travail et RH.'},
    {'name': 'Audit',          'slug': 'audit',          'description': 'Audit légal, commissariat aux comptes, contrôle interne.'},
    {'name': 'International',  'slug': 'international',  'description': 'Fiscalité internationale, expatriés, IFRS.'},
]

ARTICLES = [
    # ── Avril ──
    {
        'title': "Guide complet IS 2026 : tout savoir sur l'impôt sur les sociétés",
        'slug': 'guide-is-2026-impot-societes',
        'excerpt': "L'impôt sur les sociétés (IS) concerne toutes les personnes morales soumises à ce régime. Taux, base imposable, acomptes, régimes spéciaux : ce guide complet fait le point pour 2026.",
        'category_slug': 'fiscalite',
        'focus_keyword': 'impôt sur les sociétés PME',
        'secondary_keywords': '["IS 2026", "taux IS", "calcul impôt sociétés", "acomptes IS", "liasse fiscale"]',
        'reading_time': 12,
        'published_at': date(2026, 4, 15),
        'content': """# Guide complet de l'Impôt sur les Sociétés (IS) en 2026

## Qu'est-ce que l'impôt sur les sociétés ?

L'impôt sur les sociétés (IS) est un impôt direct qui frappe les bénéfices des personnes morales résidentes en France. Il est régi par les articles 205 à 235 ter ZD du Code général des impôts (CGI).

## Qui est soumis à l'IS ?

Sont obligatoirement soumises à l'IS :
- Les sociétés anonymes (SA), sociétés par actions simplifiées (SAS), sociétés à responsabilité limitée (SARL)
- Les sociétés en commandite par actions (SCA)
- Les établissements publics et organismes de droit public

Les sociétés de personnes (SNC, SCI, EURL) peuvent opter pour l'IS.

## Taux d'IS en 2026

Le taux normal de l'IS est fixé à **25 %** depuis 2022.

**Taux réduit PME :** Les PME dont le CA HT est inférieur à 10 millions d'euros et dont le capital est entièrement libéré et détenu à 75 % au moins par des personnes physiques bénéficient d'un **taux réduit de 15 %** sur les 42 500 premiers euros de bénéfice (article 219 I b du CGI).

## Calcul de la base imposable

Le résultat fiscal = Résultat comptable + réintégrations fiscales − déductions fiscales.

**Principales réintégrations :**
- Amendes et pénalités
- Charges personnelles de l'exploitant
- Rémunérations excessives
- Dépenses somptuaires

**Principales déductions :**
- Provisions déductibles (créances douteuses, dépréciation stocks)
- Amortissements fiscaux (linéaire, dégressif, exceptionnel)
- Plus-values à long terme (taux réduit)

## Acomptes d'IS

L'IS est payé par acomptes trimestriels (15 mars, 15 juin, 15 septembre, 15 décembre) pour les entreprises dont l'IS de l'exercice précédent dépasse **3 000 €**.

Chaque acompte = 25 % de l'IS de référence (exercice N-1 ou N-2).

Le solde est versé au plus tard le 15 du 4e mois suivant la clôture de l'exercice.

## Crédits et réductions d'impôt

- **Crédit d'impôt recherche (CIR)** : 30 % des dépenses R&D jusqu'à 100 M€, 5 % au-delà
- **Crédit d'impôt innovation (CII)** : 20 % des dépenses d'innovation pour les PME
- **Crédit d'impôt formation** : pour les dirigeants de TPE

## Optimisation légale de l'IS

- Timing des investissements (amortissements)
- Politique de rémunération du dirigeant (charges déductibles vs dividendes)
- Constitution de provisions
- Régime mère-fille (dividendes entre sociétés liées)
- Intégration fiscale (groupes de sociétés)

## Conclusion

La gestion de l'IS nécessite une expertise comptable pointue. Pour optimiser votre charge fiscale dans le respect de la loi, n'hésitez pas à consulter nos experts chez Medeo Partners.

**Sources :** BOFIP IS - BOI-IS, CGI articles 205-235, Légifrance
""",
        'meta_title': "IS 2026 : Guide Complet Impôt sur les Sociétés | Medeo Partners",
        'meta_description': "Taux IS 2026, calcul, acomptes, optimisation fiscale légale : guide complet de l'impôt sur les sociétés pour PME par les experts Medeo Partners.",
        'tags': ['IS', 'fiscalité entreprise', 'optimisation fiscale'],
    },
    {
        'title': "SAS vs SARL en 2026 : quel statut juridique choisir ?",
        'slug': 'sas-vs-sarl-2026-quel-statut-choisir',
        'excerpt': "SAS ou SARL : deux formes juridiques populaires aux caractéristiques très différentes. Régime social du dirigeant, flexibilité statutaire, coûts… Voici comment choisir en 2026.",
        'category_slug': 'creation',
        'focus_keyword': 'SAS ou SARL avantages',
        'secondary_keywords': '["différence SAS SARL", "choisir statut juridique", "SAS 2026", "SARL 2026", "création entreprise"]',
        'reading_time': 10,
        'published_at': date(2026, 4, 28),
        'content': """# SAS vs SARL en 2026 : le guide comparatif complet

## Introduction

Le choix entre SAS et SARL est l'une des décisions les plus importantes lors de la création d'entreprise. Ces deux formes juridiques représentent 90 % des créations de sociétés en France.

## La SARL (Société à Responsabilité Limitée)

**Avantages :**
- Cadre légal strict et rassurant pour les partenaires
- Régime TNS (Travailleur Non Salarié) du gérant : cotisations sociales réduites (~45 % du net)
- Cession de parts encadrée (agrément obligatoire)
- Adapté aux structures familiales

**Inconvénients :**
- Moins de flexibilité statutaire
- Statut TNS : protection sociale moindre
- Image moins favorable pour les investisseurs

## La SAS (Société par Actions Simplifiée)

**Avantages :**
- Grande liberté statutaire (gouvernance sur mesure)
- Président assimilé-salarié : protection sociale optimale (chômage possible sous conditions)
- Idéale pour la levée de fonds (émission d'actions, BSA, BSPCE)
- Image moderne et professionnelle

**Inconvénients :**
- Cotisations sociales plus élevées (~82 % du net pour le président)
- Pas de limitation légale des pouvoirs du président (à prévoir dans les statuts)

## Tableau comparatif

**Régime social du dirigeant :**
- SARL : gérant majoritaire = TNS (RSI/SSI) ; gérant minoritaire = assimilé-salarié
- SAS : président toujours assimilé-salarié

**Capital minimum :**
- SARL : 1 € (recommandé : 1 000 €+)
- SAS : 1 € (recommandé : 1 000 €+)

**Transmission :**
- SARL : cession de parts réglementée (agrément)
- SAS : cession d'actions libre (sauf clause d'agrément)

## Quel statut pour quel profil ?

**Choisissez la SARL si :**
- Vous souhaitez minimiser vos charges sociales
- Structure familiale ou TPE stable
- Vous n'envisagez pas de levée de fonds

**Choisissez la SAS si :**
- Vous recherchez des investisseurs ou associés
- Vous souhaitez une meilleure couverture sociale
- Vous avez besoin de flexibilité dans l'organisation

## Conclusion

Le choix entre SAS et SARL dépend de votre situation personnelle, de vos ambitions et de votre secteur. Nos experts-comptables vous accompagnent dans cette décision stratégique.

**Sources :** Code de commerce, CGI, URSSAF 2026
""",
        'meta_title': "SAS vs SARL 2026 : Comparatif Complet | Choisir son Statut | Medeo Partners",
        'meta_description': "SAS ou SARL en 2026 : régime social, charges, flexibilité, levée de fonds. Comparatif complet par les experts-comptables Medeo Partners à Paris.",
        'tags': ['SAS', 'SARL', 'création entreprise', 'statut juridique'],
    },
    # ── Mai ──
    {
        'title': "Optimiser sa rémunération de dirigeant : salaire vs dividendes en 2026",
        'slug': 'optimiser-remuneration-dirigeant-2026',
        'excerpt': "Salaire ou dividendes ? La rémunération du dirigeant est un levier fiscal majeur. Décryptage des avantages et inconvénients de chaque option selon votre structure en 2026.",
        'category_slug': 'fiscalite',
        'focus_keyword': 'rémunération dirigeant optimisation',
        'secondary_keywords': '["salaire ou dividendes", "charges dirigeant", "optimisation rémunération SAS", "dividendes SARL"]',
        'reading_time': 9,
        'published_at': date(2026, 5, 12),
        'content': """# Optimiser la rémunération du dirigeant en 2026

## Les deux grands modes de rémunération

Le dirigeant d'une société soumise à l'IS peut se rémunérer de deux façons principales :
1. **Salaire (ou rémunération de mandat)** : déductible du résultat de la société
2. **Dividendes** : distribution du bénéfice après IS

## La rémunération salariale

**Pour le dirigeant :**
- Soumise à cotisations sociales (assimilé-salarié SAS : ~82 % du net ; TNS SARL majoritaire : ~45 %)
- Déductible de l'IR (après abattement de 10 % ou frais réels)

**Pour la société :**
- Charge déductible → réduit le résultat imposable à l'IS
- Avantage si taux marginal IS (25 %) < taux marginal IR du dirigeant

## Les dividendes

**Depuis 2018 : Flat Tax (PFU) à 30 %** (12,8 % IR + 17,2 % prélèvements sociaux)
- Option pour le barème progressif de l'IR possible si plus favorable
- Pas de cotisations sociales (sauf dirigeant TNS SARL : cotisations sur dividendes > 10 % du capital)

**Inconvénients :**
- Prélevés sur le bénéfice après IS (double imposition partielle)
- Pas déductibles de la base IS

## Stratégie optimale 2026

**Règle générale :** Combiner les deux modes :
- Verser un salaire suffisant pour couvrir les besoins courants et optimiser la protection sociale
- Distribuer des dividendes pour le surplus de trésorerie disponible

**Point de basculement :** Le mix optimal dépend du taux marginal d'imposition du dirigeant. Nos experts calculent précisément ce point pour chaque situation.

## Cas pratiques

**Dirigeant SAS, TMI 41 % :**
- Salaire jusqu'au plafond de la Sécurité Sociale optimisé
- Dividendes soumis au PFU 30 % pour le surplus

**Gérant SARL majoritaire :**
- Rémunération TNS : cotisations ~45 % mais déductibles IS
- Dividendes jusqu'à 10 % du capital sans cotisations sociales

## Conclusion

L'optimisation de la rémunération est un exercice technique qui nécessite une analyse personnalisée. Contactez nos experts Medeo Partners pour un audit de votre situation.

**Sources :** CGI art. 13, 62, 158, URSSAF, BOFIP
""",
        'meta_title': "Optimiser Rémunération Dirigeant 2026 : Salaire vs Dividendes | Medeo Partners",
        'meta_description': "Salaire ou dividendes en 2026 : comparatif fiscal complet pour dirigeants de SAS et SARL. Optimisez votre rémunération avec les experts Medeo Partners.",
        'tags': ['rémunération dirigeant', 'dividendes', 'fiscalité dirigeant'],
    },
    {
        'title': "Holding patrimoniale : avantages fiscaux et modalités de création",
        'slug': 'holding-patrimoniale-avantages-fiscaux-creation',
        'excerpt': "La holding patrimoniale est un outil puissant d'optimisation fiscale et patrimoniale. Régime mère-fille, intégration fiscale, transmission : tout savoir avant de se lancer.",
        'category_slug': 'fiscalite',
        'focus_keyword': 'holding patrimoniale',
        'secondary_keywords': '["créer une holding", "régime mère-fille", "intégration fiscale", "holding familiale"]',
        'reading_time': 11,
        'published_at': date(2026, 5, 26),
        'content': """# Holding patrimoniale : guide complet 2026

## Qu'est-ce qu'une holding ?

Une holding (ou société mère) est une société dont l'objet est de détenir des participations dans d'autres sociétés (les filiales). Elle peut être :
- **Pure** : uniquement gestion de participations
- **Mixte (animatrice)** : participe activement à la gestion des filiales

## Principaux avantages fiscaux

### Régime mère-fille (article 145 CGI)
- Dividendes remontés de la filiale vers la holding **quasi-exonérés** d'IS
- Seulement 5 % du dividende réintégré (quote-part de frais et charges)
- Condition : détention ≥ 5 % du capital depuis ≥ 2 ans

### Intégration fiscale (articles 223 A et suivants CGI)
- Compensation des résultats bénéficiaires et déficitaires du groupe
- IS calculé sur le résultat consolidé
- Condition : détention ≥ 95 % du capital des filiales

### Plus-values de cession de titres
- Exonération à 88 % des plus-values long terme (si titres détenus ≥ 2 ans)
- Participation > 5 % = taux effectif ~3,09 % (5 % × 25 % × taux réduit)

## Avantages patrimoniaux

- **Transmission facilitée** : donation de titres de holding (pacte Dutreil si holding animatrice)
- **Capitalisation** : accumulation de trésorerie dans la holding à IS réduit
- **Protection** : assets détenus par la holding, pas directement par le dirigeant

## Création d'une holding

**Étapes :**
1. Choix de la forme juridique (SAS recommandée pour la flexibilité)
2. Apport des titres de la société opérationnelle à la holding (régime de faveur article 150-0 B ter CGI → report d'imposition)
3. Rédaction des statuts avec clauses adaptées
4. Enregistrement et formalités

**Attention :** L'apport-cession est encadré (réinvestissement obligatoire si cession dans les 3 ans).

## Pour qui ?

- Dirigeants avec plusieurs sociétés
- Chefs d'entreprise souhaitant préparer la transmission
- Entrepreneurs ayant une trésorerie importante à capitaliser

## Conclusion

La création d'une holding est une décision stratégique complexe. Nos experts Medeo Partners vous accompagnent dans la structuration optimale de votre patrimoine professionnel.

**Sources :** CGI art. 145, 216, 223 A, BOFIP IS-GPF
""",
        'meta_title': "Holding Patrimoniale 2026 : Avantages Fiscaux et Création | Medeo Partners",
        'meta_description': "Tout savoir sur la holding patrimoniale en 2026 : régime mère-fille, intégration fiscale, transmission. Guide complet par les experts Medeo Partners.",
        'tags': ['holding', 'optimisation fiscale', 'patrimoine'],
    },
    # ── Juin ──
    {
        'title': "Clôture comptable annuelle : la checklist complète pour votre entreprise",
        'slug': 'cloture-comptable-annuelle-checklist',
        'excerpt': "La clôture comptable est une étape incontournable pour toute entreprise. Inventaires, provisions, rapprochements bancaires, déclarations fiscales : suivez notre checklist pour ne rien oublier.",
        'category_slug': 'comptabilite',
        'focus_keyword': 'clôture comptable',
        'secondary_keywords': '["clôture exercice comptable", "checklist clôture", "comptes annuels", "bilan comptable PME"]',
        'reading_time': 8,
        'published_at': date(2026, 6, 9),
        'content': """# Checklist clôture comptable annuelle 2026

## Pourquoi bien clôturer son exercice ?

La clôture comptable annuelle conditionne la qualité de l'image financière de l'entreprise, la fiabilité des déclarations fiscales et la qualité des informations remontées aux associés et aux tiers (banques, investisseurs).

## Checklist complète — en 10 étapes

### 1. Inventaire physique des stocks
- Comptage physique des stocks au 31/12
- Valorisation : méthode FIFO, CUMP ou prix de revient
- Constatation des dépréciations si valeur < coût

### 2. Rapprochement bancaire
- Pointer toutes les écritures comptables avec les relevés bancaires
- Identifier les chèques en transit, virements en cours

### 3. Lettrage des comptes clients et fournisseurs
- Pointer les factures avec les règlements
- Identifier les soldes anormaux (doubles paiements, avoirs non comptabilisés)

### 4. Provisions à constater
- Provisions pour créances douteuses (clients en retard significatif)
- Provisions pour litiges en cours
- Provisions pour congés payés
- Provisions pour garanties

### 5. Charges et produits à rattacher (CCA / CAP / PCA / FAR)
- Charges constatées d'avance (assurances, loyers…)
- Charges à payer (factures non reçues)
- Produits constatés d'avance (encaissements anticipés)
- Produits à recevoir

### 6. Amortissements
- Vérifier les plans d'amortissement
- Intégrer les nouvelles immobilisations de l'exercice
- Constater les mises au rebut et cessions

### 7. TVA — bilan de fin d'année
- Pointer le compte TVA collectée et déductible
- Vérifier la cohérence avec les déclarations CA3 / CA12

### 8. Révision des comptes de paie
- Contrôler les provisions pour charges sociales patronales
- Vérifier la provision pour intéressement/participation si applicable

### 9. Événements post-clôture
- Identifier les événements survenus après le 31/12 ayant une incidence sur les comptes

### 10. Établissement des comptes annuels
- Bilan, compte de résultat, annexe
- Rapport de gestion (obligatoire pour SARL, SA, SAS selon seuils)
- Dépôt au greffe dans les délais légaux

## Délais légaux

- **SAS/SARL/SA** : approbation des comptes dans les 6 mois de la clôture
- **Dépôt au greffe** : 1 mois après approbation (ou 2 mois si dématérialisé)

## Conclusion

Une clôture rigoureuse est le fondement d'une gestion saine. Nos experts-comptables Medeo Partners vous accompagnent dans l'ensemble de ce processus.

**Sources :** Code de commerce art. L123-12, PCG, BOFIP BIC
""",
        'meta_title': "Clôture Comptable Annuelle 2026 : Checklist Complète | Medeo Partners",
        'meta_description': "Checklist clôture comptable annuelle : inventaire, provisions, rapprochements, comptes annuels. Tout ce qu'il faut faire pour clôturer son exercice sans erreur.",
        'tags': ['clôture comptable', 'comptes annuels', 'bilan'],
    },
    {
        'title': "CFE 2026 : qui paie la Cotisation Foncière des Entreprises et comment l'optimiser ?",
        'slug': 'cfe-2026-cotisation-fonciere-entreprises',
        'excerpt': "La CFE est due par toutes les entreprises et indépendants. Qui est concerné, comment est-elle calculée, et quelles exonérations existent en 2026 ? Tour d'horizon complet.",
        'category_slug': 'fiscalite',
        'focus_keyword': 'cotisation foncière entreprises',
        'secondary_keywords': '["CFE 2026", "exonération CFE", "calcul CFE", "micro-entrepreneur CFE"]',
        'reading_time': 7,
        'published_at': date(2026, 6, 23),
        'content': """# CFE 2026 : tout savoir sur la Cotisation Foncière des Entreprises

## Qu'est-ce que la CFE ?

La Cotisation Foncière des Entreprises (CFE) est l'une des deux composantes de la Contribution Économique Territoriale (CET), avec la CVAE. Elle est basée sur la valeur locative des biens immobiliers utilisés pour l'activité professionnelle.

**Base légale :** CGI articles 1447 à 1477

## Qui est redevable ?

Toute personne physique ou morale exerçant une activité professionnelle non salariée à titre habituel au 1er janvier de l'année d'imposition.

Cela inclut :
- Les entreprises (SA, SAS, SARL, SNC…)
- Les micro-entrepreneurs et auto-entrepreneurs
- Les professions libérales
- Les agriculteurs (sous conditions)

## Qui est exonéré ?

- **Première année d'activité** : exonération totale
- **Artisans** travaillant seuls ou avec leur famille
- **Agriculteurs** (sous certaines conditions)
- **Certaines activités** : pêche maritime, enseignement privé…
- **Chiffre d'affaires < 5 000 €** : cotisation minimum réduite de 50 %

## Comment est calculée la CFE ?

Base de calcul = valeur locative des immobilisations corporelles (locaux, terrains, équipements) au 31/12 de l'année N-2.

**Cotisation minimum :** Si valeur locative faible ou nulle (ex : domiciliation au domicile), une cotisation minimum est due, fixée par la commune :

| CA ou recettes | Cotisation minimum (fourchette 2026) |
|---|---|
| ≤ 10 000 € | 237 € à 565 € |
| 10 001 € à 32 600 € | 237 € à 1 130 € |
| 32 601 € à 100 000 € | 237 € à 2 374 € |
| 100 001 € à 250 000 € | 237 € à 3 957 € |
| 250 001 € à 500 000 € | 237 € à 5 652 € |
| > 500 000 € | 237 € à 7 349 € |

## Délais et modalités de paiement

- **Date limite de paiement** : 15 décembre de chaque année
- Paiement en ligne obligatoire au-delà de 3 000 €
- Possibilité de mensualisation

## Optimiser sa CFE

- Vérifier la base de calcul (valeur locative souvent surévaluée)
- Demander un dégrèvement si l'activité a cessé ou si les locaux ont été réduits
- Contester la valeur locative en cas d'erreur (délai : 31 décembre de l'année N+1)

## Conclusion

La CFE peut représenter une charge significative, notamment pour les TPE avec des locaux importants. Nos experts vérifient régulièrement les bases de calcul pour nos clients.

**Sources :** CGI art. 1447-1477, BOFIP IF-CFE, DGFiP
""",
        'meta_title': "CFE 2026 : Qui Paie et Comment Optimiser la Cotisation Foncière | Medeo Partners",
        'meta_description': "Tout sur la CFE 2026 : redevables, calcul, exonérations, cotisation minimum. Guide complet des experts Medeo Partners pour optimiser votre charge fiscale.",
        'tags': ['CFE', 'CET', 'fiscalité locale', 'impôts locaux'],
    },
    # ── Juillet ──
    {
        'title': "Fiscalité des expatriés en France : guide pour les non-résidents 2026",
        'slug': 'fiscalite-expatries-non-residents-france-2026',
        'excerpt': "Non-résident fiscal, impatrié ou expatrié : les règles fiscales françaises sont complexes. Domicile fiscal, conventions bilatérales, régime impatrié : ce qu'il faut savoir en 2026.",
        'category_slug': 'international',
        'focus_keyword': 'expert comptable expatrié France',
        'secondary_keywords': '["fiscalité non-résident France", "impatrié fiscal", "convention fiscale", "ISF expatrié"]',
        'reading_time': 10,
        'published_at': date(2026, 7, 8),
        'content': """# Fiscalité des expatriés et non-résidents en France en 2026

## Déterminer sa résidence fiscale

La notion de domicile fiscal (article 4 B du CGI) est déterminante. Une personne est considérée domiciliée fiscalement en France si elle remplit au moins l'un des critères suivants :
- **Foyer ou lieu de séjour principal** en France
- **Activité professionnelle** exercée en France (sauf accessoire)
- **Centre des intérêts économiques** en France

## Le régime des impatriés (article 155 B CGI)

Ce régime favorable s'applique aux personnes qui s'installent en France après avoir résidé à l'étranger pendant au moins 5 ans.

**Avantages :**
- Exonération à 30 % de la rémunération (prime d'impatriation)
- Exonération de 50 % des revenus de source étrangère (dividendes, intérêts, royalties)
- Durée : jusqu'au 31 décembre de la 8e année suivant la prise de fonctions

## Conventions fiscales bilatérales

La France a signé plus de 125 conventions fiscales. Elles permettent d'éviter la double imposition et de déterminer quel État a le droit d'imposer chaque catégorie de revenus.

**Grands principes :**
- Revenus immobiliers : imposés dans l'État où se situe le bien
- Dividendes : retenue à la source dans l'État source + impôt dans l'État de résidence (crédit d'impôt)
- Revenus d'emploi : imposés dans l'État d'exercice

## Non-résidents : impôt en France

Les non-résidents sont imposables en France uniquement sur leurs revenus de **source française** :
- Revenus fonciers sur immeubles situés en France
- Dividendes de sociétés françaises
- Plus-values sur cession d'immeubles ou de participations substantielles

**Taux minimum** : 20 % (ou 30 % au-delà de 27 519 €)

## Obligations déclaratives

- **Formulaire 2042** pour les revenus français
- **Formulaire 2047** pour les revenus étrangers
- Déclaration auprès du Service des Impôts des Particuliers Non-Résidents (SIPNR)

## Conseils pratiques

- Obtenir un certificat de résidence fiscale étrangère
- Anticiper les conséquences fiscales avant le départ ou le retour
- Vérifier les traités de sécurité sociale

## Conclusion

La fiscalité des expatriés est un domaine complexe qui nécessite une expertise spécifique. Medeo Partners accompagne les non-résidents et impatriés dans leur optimisation fiscale franco-étrangère.

**Sources :** CGI art. 4A, 4B, 155B, Légifrance, conventions fiscales bilatérales
""",
        'meta_title': "Fiscalité Expatriés France 2026 : Guide Non-Résidents | Medeo Partners",
        'meta_description': "Fiscalité des expatriés et non-résidents en France : domicile fiscal, régime impatrié, conventions bilatérales. Guide 2026 par Medeo Partners Paris.",
        'tags': ['expatrié', 'non-résident', 'fiscalité internationale'],
    },
    {
        'title': "Business plan financier : modèle et conseils pour convaincre les investisseurs",
        'slug': 'business-plan-financier-modele-conseils',
        'excerpt': "Le business plan financier est le cœur de votre dossier de financement. Compte de résultat prévisionnel, plan de trésorerie, bilan prévisionnel : comment les construire correctement.",
        'category_slug': 'creation',
        'focus_keyword': 'business plan financier',
        'secondary_keywords': '["prévisionnel financier", "compte résultat prévisionnel", "plan trésorerie", "valorisation startup"]',
        'reading_time': 12,
        'published_at': date(2026, 7, 22),
        'content': """# Business plan financier : le guide complet 2026

## Pourquoi un business plan financier ?

Le business plan financier traduit vos ambitions en chiffres. Il est indispensable pour :
- Convaincre des banques ou des investisseurs
- Vérifier la viabilité de votre projet
- Piloter votre activité une fois lancé

## Les 4 documents financiers essentiels

### 1. Le compte de résultat prévisionnel (P&L)

Projet sur 3 ans minimum (5 pour les levées de fonds significatives) :

**Structure :**
- Chiffre d'affaires (par ligne de produit/service)
- Coûts variables (COGS)
- Marge brute
- Charges fixes (loyer, salaires, marketing…)
- EBITDA
- Amortissements
- Résultat d'exploitation (EBIT)
- Résultat net

### 2. Le plan de trésorerie mensuel

Prévision mois par mois sur 12-24 mois :
- Encaissements clients (délais de paiement !)
- Décaissements fournisseurs et charges
- Solde de trésorerie cumulé
- Besoin en Fonds de Roulement (BFR)

### 3. Le bilan prévisionnel

Photographie de votre patrimoine à chaque fin d'exercice :
- Actif : immobilisations, stocks, créances, trésorerie
- Passif : capitaux propres, dettes financières, dettes fournisseurs

### 4. Le plan de financement initial

- Besoins : investissements + BFR + trésorerie de démarrage
- Ressources : apports, emprunts, subventions, aides

## Hypothèses et sensibilité

Présentez toujours 3 scénarios :
- **Optimiste** : croissance forte
- **Central** : croissance réaliste
- **Pessimiste** : scenario de stress

Identifier les principaux leviers (taux de conversion, panier moyen, délai d'acquisition client).

## Indicateurs clés à mettre en avant

- **Point mort** (break-even) : quand sera-t-il atteint ?
- **CAC** (Coût d'Acquisition Client)
- **LTV** (Lifetime Value)
- **EBITDA margin**
- **Cash runway** (autonomie financière)

## Erreurs fréquentes à éviter

- Hypothèses de CA trop optimistes non étayées
- Oublier la TVA dans le plan de trésorerie
- Sous-estimer le BFR
- Ne pas intégrer sa propre rémunération
- Projections à 1 an seulement

## Conclusion

Un business plan financier crédible repose sur des hypothèses documentées et cohérentes. Nos experts Medeo Partners vous accompagnent dans la construction de vos prévisionnels financiers.

**Sources :** PCG, CNC, pratiques bancaires BPI France
""",
        'meta_title': "Business Plan Financier 2026 : Modèle et Conseils | Medeo Partners",
        'meta_description': "Comment faire un business plan financier convaincant : compte de résultat prévisionnel, trésorerie, bilan. Modèle et conseils d'experts par Medeo Partners.",
        'tags': ['business plan', 'prévisionnel', 'financement', 'création entreprise'],
    },
    # ── Août ──
    {
        'title': "Audit légal obligatoire : seuils, procédure et commissaire aux comptes en 2026",
        'slug': 'audit-legal-obligatoire-seuils-cac-2026',
        'excerpt': "L'audit légal est obligatoire au-delà de certains seuils. Quelles entreprises sont concernées en 2026 ? Comment se déroule la mission et quel est le rôle du commissaire aux comptes ?",
        'category_slug': 'audit',
        'focus_keyword': 'commissaire aux comptes',
        'secondary_keywords': '["audit légal obligatoire", "seuils CAC 2026", "commissaire aux comptes PME", "certification comptes"]',
        'reading_time': 9,
        'published_at': date(2026, 8, 11),
        'content': """# Audit légal en 2026 : tout ce que vous devez savoir

## Qu'est-ce que l'audit légal ?

L'audit légal (ou commissariat aux comptes) est une mission de certification des comptes annuels réalisée par un commissaire aux comptes (CAC) inscrit à la CNCC. Il garantit la sincérité, la régularité et l'image fidèle des comptes.

**Base légale :** Articles L823-1 et suivants du Code de commerce

## Quelles entreprises sont concernées ?

Depuis la réforme de 2019, les seuils ont été rehaussés. Une société est tenue de désigner un CAC si elle dépasse 2 des 3 seuils suivants :

| Critère | Seuil (SAS, SARL, SA hors cotées) |
|---|---|
| Total bilan | 4 000 000 € |
| Chiffre d'affaires HT | 8 000 000 € |
| Nombre de salariés | 50 |

**Cas particuliers toujours soumis :**
- Sociétés cotées (peu importe les seuils)
- Sociétés contrôlant ou contrôlées par d'autres (groupes) : seuils réduits
- Associations de collecte de fonds public > 153 000 €

## Durée et renouvellement du mandat

Le CAC est nommé pour **6 exercices** (6 ans). Son mandat peut être renouvelé.

## Déroulement de la mission

### Phase 1 : Prise de connaissance
- Compréhension du secteur et de l'entité
- Évaluation des risques
- Définition du plan d'audit

### Phase 2 : Tests de contrôle
- Évaluation du contrôle interne
- Vérification de la séparation des tâches
- Tests des procédures comptables

### Phase 3 : Contrôles substantifs
- Confirmation des soldes avec les tiers (clients, banques, fournisseurs)
- Vérification des inventaires
- Analyse des postes significatifs

### Phase 4 : Rapport et opinion
- Opinion sur les comptes : **certification sans réserve** / **avec réserve** / **refus de certifier**
- Rapport sur les procédures de contrôle interne
- Rapport spécial sur les conventions réglementées

## Coût d'un CAC

Variable selon la taille de l'entreprise :
- TPE/PME : 3 000 € à 15 000 € par an
- ETI : 15 000 € à 100 000 € par an
- Grands groupes : au-delà

## Désignation volontaire

Même si les seuils ne sont pas atteints, une entreprise peut désigner volontairement un CAC. Cela renforce la crédibilité auprès des banques et investisseurs.

## Conclusion

L'audit légal est un gage de confiance pour vos parties prenantes. Medeo Partners vous accompagne dans la préparation de vos audits et la mise en conformité de vos processus.

**Sources :** Code de commerce art. L823-1, L820-1, Ordonnance 2019-1234
""",
        'meta_title': "Audit Légal Obligatoire 2026 : Seuils CAC et Procédure | Medeo Partners",
        'meta_description': "Qui doit avoir un commissaire aux comptes en 2026 ? Seuils, procédure d'audit légal, rôle du CAC. Guide complet par les experts Medeo Partners.",
        'tags': ['audit légal', 'commissaire aux comptes', 'CAC', 'certification comptes'],
    },
    # ── Septembre ──
    {
        'title': "TVA intracommunautaire 2026 : guide complet pour les entreprises qui exportent en UE",
        'slug': 'tva-intracommunautaire-guide-2026',
        'excerpt': "Acquisitions et livraisons intracommunautaires, autoliquidation, numéro de TVA intracommunautaire, OSS : tout ce que les entreprises doivent savoir sur la TVA en Europe en 2026.",
        'category_slug': 'fiscalite',
        'focus_keyword': 'TVA intracommunautaire',
        'secondary_keywords': '["TVA Europe", "numéro TVA intracommunautaire", "livraison intracommunautaire", "OSS TVA", "autoliquidation"]',
        'reading_time': 11,
        'published_at': date(2026, 9, 8),
        'content': """# TVA intracommunautaire 2026 : guide complet

## Principes fondamentaux

Au sein de l'Union Européenne, les échanges de biens entre assujettis sont soumis à des règles spécifiques de TVA. Le principe général : la TVA est due dans le pays d'arrivée (destination).

## Le numéro de TVA intracommunautaire

**Obligatoire** pour toute entreprise réalisant des opérations intracommunautaires.
Format français : **FR** + 2 caractères (clé) + 9 chiffres du SIREN.
À mentionner sur toutes les factures intracommunautaires.

**Validation :** Système VIES (VAT Information Exchange System) sur ec.europa.eu

## Les acquisitions intracommunautaires (AIC)

Une AIC se produit quand une entreprise française achète des biens à un fournisseur UE assujetti à la TVA.

**Mécanisme d'autoliquidation :**
- Le fournisseur facture sans TVA (exonéré dans son pays)
- L'acheteur français déclare et déduit simultanément la TVA française
- Déclaration sur la ligne CA3 : TVA due + TVA déductible = impact nul

## Les livraisons intracommunautaires (LIC)

Vente de biens à un assujetti d'un autre État membre.

**Conditions d'exonération :**
- L'acheteur doit avoir un n° de TVA intracommunautaire valide (vérifier via VIES)
- Transport hors de France documenté (CMR, lettre de transport…)
- Déclaration sur l'état récapitulatif des clients (DEB remplacé par les formulaires DES/DEB selon les cas)

## Prestations de services intracommunautaires

**Règle B2B (article 44 directive TVA) :**
- Lieu de prestation = pays du preneur
- Autoliquidation chez le client
- Facturer sans TVA avec la mention "Autoliquidation - art. 283-2 CGI"

**Règle B2C :**
- Lieu = pays du prestataire
- TVA française applicable

## Le guichet unique OSS (One Stop Shop)

Depuis 2021, les e-commerçants vendant à des particuliers UE peuvent :
- Déclarer et payer la TVA de tous les États membres via un seul portail français
- Seuil unique : 10 000 € de ventes transfrontalières B2C par an

## Déclarations et obligations

- **État récapitulatif des prestations de services (ES)** : mensuel ou trimestriel sur impots.gouv.fr
- **Déclaration d'échanges de biens (DEB)** : pour les biens au-delà de 460 000 € en introduction et 400 000 € en expédition

## Conclusion

La TVA intracommunautaire nécessite une rigueur documentaire importante. Medeo Partners accompagne les entreprises dans leur conformité et l'optimisation de leur gestion TVA en Europe.

**Sources :** Directive 2006/112/CE, CGI art. 256, 259, 283, DGFiP
""",
        'meta_title': "TVA Intracommunautaire 2026 : Guide Complet | Medeo Partners",
        'meta_description': "TVA intracommunautaire 2026 : numéro TVA UE, AIC, LIC, autoliquidation, OSS. Guide complet pour les entreprises qui exportent en Europe.",
        'tags': ['TVA intracommunautaire', 'TVA Europe', 'OSS', 'export UE'],
    },
    # ── Octobre ──
    {
        'title': "Charges sociales du dirigeant : TNS vs assimilé-salarié en 2026",
        'slug': 'charges-sociales-dirigeant-tns-vs-assimile-salarie-2026',
        'excerpt': "Gérant TNS ou président assimilé-salarié : les cotisations sociales sont radicalement différentes. Comparatif complet des charges, de la protection sociale et des stratégies d'optimisation.",
        'category_slug': 'social',
        'focus_keyword': 'charges sociales dirigeant',
        'secondary_keywords': '["TNS charges sociales", "assimilé-salarié cotisations", "gérant SARL charges", "président SAS cotisations"]',
        'reading_time': 9,
        'published_at': date(2026, 10, 6),
        'content': """# Charges sociales du dirigeant en 2026 : TNS vs Assimilé-Salarié

## Les deux régimes en bref

### Le Travailleur Non Salarié (TNS)
Concerne les gérants majoritaires de SARL (> 50 % du capital), les associés de SNC, les EURL.

**Organisme :** Sécurité Sociale des Indépendants (SSI, ex-RSI), géré par l'Assurance Maladie

**Cotisations :** ~45 % du revenu net (vs net reçu)

### L'Assimilé-Salarié
Concerne les présidents de SAS/SASU, gérants minoritaires ou égalitaires de SARL, DG.

**Organisme :** Régime général de la Sécurité Sociale

**Cotisations :** ~82 % du salaire net (cotisations salariales + patronales)

## Comparatif détaillé

Pour une rémunération nette de 50 000 €/an :

**TNS :**
- Charges sociales : ~22 500 €
- Coût total pour la société : ~72 500 €
- Protection sociale : correcte mais moindre

**Assimilé-Salarié :**
- Charges salariales : ~10 000 €
- Charges patronales : ~31 000 €
- Coût total : ~91 000 €
- Protection sociale : optimale (retraite, IJSS, chômage possible)

## Différences de protection sociale

| Prestations | TNS | Assimilé-Salarié |
|---|---|---|
| Maladie (IJ) | Oui (après 3 jours) | Oui (dès le 4e jour) |
| Retraite de base | Oui | Oui |
| Retraite complémentaire | Oui (RCI) | Oui (AGIRC-ARRCO) |
| Prévoyance | Faible | Forte |
| Chômage | Non (sauf GSC Madelin) | Non (sauf ARE sous conditions) |

## L'équation TNS vs Assimilé-Salarié

**TNS moins cher en charges MAIS :**
- Protection sociale plus faible
- Pas de chômage (sauf contrat de prévoyance Madelin)
- Pas de couverture invalidité forte par défaut

**Optimisation possible :**
- TNS : souscrire des contrats Madelin (prévoyance, retraite) → déductibles fiscalement
- Assimilé-salarié : optimiser via dividendes (PFU 30 %)

## Stratégies d'optimisation 2026

**Pour un dirigeant TNS :**
- Contrat Madelin retraite : déductible jusqu'à 10 % du PASS + 25 % revenus
- Contrat Madelin prévoyance : déductible jusqu'à 7 % du PASS
- PER collectif pour l'entreprise

**Pour un assimilé-salarié :**
- Plan d'Épargne Entreprise (PEE) + abondement
- Article 83 / PER obligatoire
- Optimisation du mix salaire/dividendes

## Conclusion

Le choix du statut social a un impact majeur sur la rémunération nette et la protection sociale. Une analyse personnalisée est indispensable. Contactez nos experts Medeo Partners.

**Sources :** Code de la Sécurité Sociale, CGI, URSSAF 2026, AGIRC-ARRCO
""",
        'meta_title': "Charges Sociales Dirigeant 2026 : TNS vs Assimilé-Salarié | Medeo Partners",
        'meta_description': "Comparatif charges sociales TNS vs assimilé-salarié 2026 : cotisations, protection sociale, optimisation. Guide complet par les experts Medeo Partners.",
        'tags': ['charges sociales', 'TNS', 'assimilé-salarié', 'protection sociale dirigeant'],
    },
    # ── Novembre ──
    {
        'title': "Défiscalisation légale pour les entreprises : 10 leviers à activer en 2026",
        'slug': 'defiscalisation-legale-entreprises-2026',
        'excerpt': "Crédits d'impôt, provisions, amortissements accélérés, dispositifs sectoriels : voici les 10 principaux leviers de défiscalisation légale pour réduire l'IS de votre entreprise en 2026.",
        'category_slug': 'fiscalite',
        'focus_keyword': 'défiscalisation entreprise',
        'secondary_keywords': '["réduire IS légalement", "crédit impôt recherche 2026", "amortissement accéléré", "optimisation fiscale légale PME"]',
        'reading_time': 13,
        'published_at': date(2026, 11, 10),
        'content': """# 10 leviers de défiscalisation légale pour les entreprises en 2026

## Introduction

La défiscalisation légale consiste à utiliser les mécanismes prévus par la loi pour réduire l'imposition de manière licite. Voici les 10 principaux leviers pour les entreprises soumises à l'IS.

## 1. Crédit d'Impôt Recherche (CIR)

**Taux :** 30 % des dépenses de R&D jusqu'à 100 M€ ; 5 % au-delà
**Dépenses éligibles :** salaires chercheurs, dotations amortissements, sous-traitance agréée, veille technologique
**Remboursable** pour les PME (Article 244 quater B CGI)

## 2. Crédit d'Impôt Innovation (CII)

**Taux :** 20 % des dépenses d'innovation pour les PME (40 % en Corse)
**Plafond :** 400 000 € de dépenses éligibles
Complémentaire au CIR pour les activités de développement de produits nouveaux.

## 3. Amortissements accélérés et suramortissement

- **Matériels verts (robotique, industrie du futur) :** suramortissement de 40 % du prix d'acquisition
- **Amortissement dégressif** pour certains biens (véhicules utilitaires, équipements industriels)

## 4. Provisions réglementées

- **Provisions pour hausse des prix** : anticipation d'une hausse des matières premières
- **Provisions pour fluctuation des cours** : sociétés minières/pétrolières
- **Provisions pour investissement** (intéressement)

## 5. Régime des plus-values long terme

- Cession de titres de participation détenus > 2 ans : exonération à 88 % (quote-part 12 %)
- Taux effectif : ~3 % au lieu de 25 %
- Concerne la holding : stratégie de cession optimisée

## 6. Zones géographiques défiscalisantes

- **Zones de Revitalisation Rurale (ZRR)** : exonération d'IS temporaire
- **Zones Franches Urbaines (ZFU)** : exonération 5 ans puis dégressive
- **Bassins d'Emploi à Redynamiser (BER)**
- **DOM-TOM** : régimes spécifiques avantageux

## 7. Crédit d'Impôt pour la Formation des Dirigeants

Disponible pour les TPE/PME : 1 heure de formation = 1 heure au taux horaire du SMIC.
Plafonné à 40 heures par an et par dirigeant.

## 8. Jeune Entreprise Innovante (JEI)

- Exonération d'IS pendant les premières années
- Exonération de cotisations sociales sur les salaires des chercheurs
- Conditions : < 8 ans, PME, > 15 % des charges en R&D

## 9. Plan d'Épargne Retraite collectif (PER)

- Abondements de l'employeur déductibles des charges
- Exonération de cotisations sociales patronales sous conditions
- Outil de fidélisation des collaborateurs

## 10. Politique de prix de transfert (groupes)

Pour les groupes ayant des entités dans différents pays :
- Optimisation des flux intra-groupe (redevances, intérêts, prestations de services)
- Dans le strict respect du principe de pleine concurrence (OCDE)
- Nécessite une documentation robuste

## Attention aux abus

L'optimisation fiscale doit rester dans le cadre légal. L'Administration fiscale dispose d'outils puissants : abus de droit (article L64 LPF), acte anormal de gestion, prix de transfert…

## Conclusion

Ces 10 leviers représentent un potentiel d'économies significatives pour votre entreprise. Medeo Partners réalise un audit fiscal annuel pour identifier les opportunités adaptées à votre situation.

**Sources :** CGI, BOFIP, Légifrance, Instruction fiscale DGFiP 2026
""",
        'meta_title': "Défiscalisation Légale Entreprise 2026 : 10 Leviers | Medeo Partners",
        'meta_description': "10 leviers de défiscalisation légale pour réduire l'IS en 2026 : CIR, CII, amortissements, JEI, ZFR. Guide complet par les experts Medeo Partners Paris.",
        'tags': ['défiscalisation', 'optimisation fiscale', 'CIR', 'IS', 'réduction impôts'],
    },
]


# ─────────────────────────────────────────────────────────────
# Insertion
# ─────────────────────────────────────────────────────────────

def get_or_create_category(name, slug, description=''):
    cat = BlogCategory.query.filter_by(slug=slug).first()
    if not cat:
        cat = BlogCategory(name=name, slug=slug, description=description,
                           seo_title=f"{name} — Blog Medeo Partners",
                           meta_description=f"Articles et guides sur {name.lower()} par les experts Medeo Partners.")
        db.session.add(cat)
        db.session.flush()
        print(f"  [+] Catégorie créée : {name}")
    return cat


def get_or_create_tag(name):
    from python_slugify import slugify
    slug = slugify(name)
    tag = BlogTag.query.filter_by(slug=slug).first()
    if not tag:
        tag = BlogTag(name=name, slug=slug)
        db.session.add(tag)
        db.session.flush()
    return tag


def insert_articles():
    with app.app_context():
        # Créer les catégories
        cat_map = {}
        for cat_data in CATEGORIES:
            cat = get_or_create_category(cat_data['name'], cat_data['slug'], cat_data['description'])
            cat_map[cat_data['slug']] = cat
        db.session.commit()

        inserted = 0
        skipped = 0

        for art_data in ARTICLES:
            # Vérifier si l'article existe déjà
            existing = BlogArticle.query.filter_by(slug=art_data['slug']).first()
            if existing:
                print(f"  [=] Ignoré (existe) : {art_data['slug']}")
                skipped += 1
                continue

            cat = cat_map.get(art_data['category_slug'])
            if not cat:
                print(f"  [!] Catégorie introuvable : {art_data['category_slug']}")
                continue

            # Créer les tags
            tags = []
            for tag_name in art_data.get('tags', []):
                tags.append(get_or_create_tag(tag_name))

            published_at = datetime.combine(art_data['published_at'], datetime.min.time())

            article = BlogArticle(
                title=art_data['title'],
                slug=art_data['slug'],
                excerpt=art_data['excerpt'],
                content=art_data['content'],
                category_id=cat.id,
                focus_keyword=art_data.get('focus_keyword', ''),
                secondary_keywords=art_data.get('secondary_keywords', '[]'),
                meta_title=art_data.get('meta_title', art_data['title']),
                meta_description=art_data.get('meta_description', art_data['excerpt'][:300]),
                reading_time=art_data.get('reading_time', 8),
                status='published',
                published_at=published_at,
                view_count=0,
            )
            article.tags = tags
            db.session.add(article)
            db.session.flush()
            print(f"  [+] Article créé : {art_data['slug']}")
            inserted += 1

        db.session.commit()
        print(f"\n✅ {inserted} article(s) insérés, {skipped} ignorés.")


if __name__ == '__main__':
    try:
        from python_slugify import slugify
    except ImportError:
        print("❌ python-slugify requis : pip install python-slugify")
        sys.exit(1)

    print("🚀 Insertion du calendrier éditorial (12 articles)...")
    insert_articles()
    print("✅ Terminé.")
