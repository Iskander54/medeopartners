"""
Configuration du blog - Catégories, articles liés, et métadonnées
"""

# Catégories de blog
BLOG_CATEGORIES = {
    'actualite-fiscale': {
        'name': 'Actualité fiscale',
        'description': 'Les dernières nouveautés fiscales et réglementaires',
        'color': 'bg-blue-500',
        'icon': '📊'
    },
    'guides-pratiques': {
        'name': 'Guides pratiques',
        'description': 'Guides complets et checklists pour gérer votre entreprise',
        'color': 'bg-green-500',
        'icon': '📚'
    },
    'expertise-sectorielle': {
        'name': 'Expertise sectorielle',
        'description': 'Conseils spécialisés par secteur d\'activité',
        'color': 'bg-purple-500',
        'icon': '🏢'
    },
    'optimisation-fiscale': {
        'name': 'Optimisation fiscale',
        'description': 'Stratégies légales pour optimiser votre fiscalité',
        'color': 'bg-yellow-500',
        'icon': '💰'
    },
    'creation-entreprise': {
        'name': 'Création d\'entreprise',
        'description': 'Tout savoir pour créer et développer votre entreprise',
        'color': 'bg-red-500',
        'icon': '🚀'
    },
    'fiscal': {
        'name': 'Fiscal',
        'description': 'Actualités et conseils en fiscalité',
        'color': 'bg-primary',
        'icon': '📋'
    }
}

# Mapping des articles avec leurs articles liés (pour suggestions)
RELATED_ARTICLES = {
    'tva-obligations-declaratives-dirigeants': [
        {
            'slug': 'creation-entreprise-erreurs-comptables-fiscales-premiere-annee',
            'title': 'Création d\'entreprise : erreurs comptables et fiscales à éviter',
            'excerpt': 'Découvrez les erreurs les plus fréquentes lors de la création d\'entreprise'
        },
        {
            'slug': 'loi-finances-2026-impact-entreprise',
            'title': 'Loi de Finances 2026 : Impact sur votre entreprise',
            'excerpt': 'Découvrez les changements fiscaux de la Loi de Finances 2026'
        }
    ],
    'creation-entreprise-erreurs-comptables-fiscales-premiere-annee': [
        {
            'slug': 'tva-obligations-declaratives-dirigeants',
            'title': 'TVA et obligations déclaratives : ce que les dirigeants doivent savoir',
            'excerpt': 'Maîtrisez vos obligations TVA dès le démarrage de votre activité'
        },
        {
            'slug': 'loi-finances-2026-impact-entreprise',
            'title': 'Loi de Finances 2026 : Impact sur votre entreprise',
            'excerpt': 'Anticipez les changements fiscaux dès la création de votre entreprise'
        }
    ],
    'loi-finances-2026-impact-entreprise': [
        {
            'slug': 'tva-obligations-declaratives-dirigeants',
            'title': 'TVA et obligations déclaratives : ce que les dirigeants doivent savoir',
            'excerpt': 'Maîtrisez vos obligations TVA dans le contexte de la Loi de Finances 2026'
        },
        {
            'slug': 'creation-entreprise-erreurs-comptables-fiscales-premiere-annee',
            'title': 'Création d\'entreprise : erreurs comptables et fiscales à éviter',
            'excerpt': 'Évitez les erreurs fiscales dès le démarrage de votre activité'
        }
    ]
}

# Métadonnées des articles (pour génération automatique de certaines infos)
#
# 'title', 'excerpt', 'published', 'modified' et 'image' alimentent le JSON-LD
# BlogPosting des articles servis depuis les templates statiques (quand la DB
# est HS, cf. STATIC_ARTICLE_TEMPLATES). Les articles en base utilisent leurs
# propres colonnes. Dates au format ISO (AAAA-MM-JJ) : elles correspondent à la
# mise en ligne des templates.
ARTICLE_METADATA = {
    'tva-obligations-declaratives-dirigeants': {
        'category': 'fiscal',
        'reading_time': 8,
        'keywords': ['TVA', 'obligations déclaratives', 'fiscalité', 'entreprise', 'dirigeant'],
        'related_slugs': ['creation-entreprise-erreurs-comptables-fiscales-premiere-annee', 'loi-finances-2026-impact-entreprise'],
        'title': "TVA et obligations déclaratives : ce que les dirigeants doivent absolument savoir",
        'excerpt': "La TVA représente un enjeu majeur pour les entreprises. Découvrez les obligations déclaratives essentielles que tout dirigeant doit maîtriser pour éviter les erreurs coûteuses et les sanctions fiscales.",
        'published': '2026-01-12',
        'modified': '2026-01-12',
        'image': 'images/tax.webp',
    },
    'creation-entreprise-erreurs-comptables-fiscales-premiere-annee': {
        'category': 'creation-entreprise',
        'reading_time': 10,
        'keywords': ['création entreprise', 'erreurs comptables', 'fiscalité', 'première année'],
        'related_slugs': ['tva-obligations-declaratives-dirigeants', 'loi-finances-2026-impact-entreprise'],
        'title': "Création d'entreprise : erreurs comptables et fiscales à éviter dès la première année",
        'excerpt': "La première année d'activité est déterminante. Découvrez les erreurs comptables et fiscales les plus fréquentes commises par les nouveaux entrepreneurs et comment les éviter pour sécuriser votre projet.",
        'published': '2026-01-12',
        'modified': '2026-01-12',
        'image': 'images/accounting.webp',
    },
    'loi-finances-2026-impact-entreprise': {
        'category': 'actualite-fiscale',
        'reading_time': 12,
        'keywords': ['loi finances 2026', 'fiscalité entreprise 2026', 'nouveautés fiscales', 'impôt sur les sociétés', 'CVAE', 'Paris'],
        'related_slugs': ['tva-obligations-declaratives-dirigeants', 'creation-entreprise-erreurs-comptables-fiscales-premiere-annee'],
        'title': 'Loi de Finances 2026 : Impact sur votre entreprise parisienne',
        'excerpt': "La Loi de Finances 2026 apporte des changements significatifs pour les entreprises. Découvrez les mesures qui impactent directement votre activité et comment les anticiper avec l'aide d'un expert-comptable.",
        'published': '2026-01-12',
        'modified': '2026-09-24',
        'image': 'images/budget.webp',
    }
}

def get_category_info(category_slug):
    """Retourne les informations d'une catégorie"""
    return BLOG_CATEGORIES.get(category_slug, {
        'name': 'Non catégorisé',
        'description': '',
        'color': 'bg-gray-500',
        'icon': '📄'
    })

def get_related_articles(article_slug):
    """Retourne les articles liés pour un article donné"""
    return RELATED_ARTICLES.get(article_slug, [])

def get_article_metadata(article_slug):
    """Retourne les métadonnées d'un article"""
    return ARTICLE_METADATA.get(article_slug, {
        'category': 'fiscal',
        'reading_time': 5,
        'keywords': [],
        'related_slugs': []
    })

