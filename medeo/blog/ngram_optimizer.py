"""
Outil d'optimisation SEO basé sur les n-grammes
Analyse et optimise le contenu avec des expressions recherchées
"""

# N-grammes optimisés pour le secteur comptable/fiscal (basés sur les recherches Google)
OPTIMIZED_NGRAMS = {
    'loi-finances-2026': {
        'bigrammes': [
            'loi finances', 'finances 2026', 'loi 2026', 'fiscalité entreprise',
            'impôt sociétés', 'taux IS', 'CVAE 2026', 'crédit impôt',
            'optimisation fiscale', 'entreprise parisienne', 'expert comptable'
        ],
        'trigrammes': [
            'loi de finances', 'loi finances 2026', 'impôt sur sociétés',
            'expert comptable Paris', 'cabinet comptable Paris',
            'optimisation fiscale entreprise', 'crédit impôt recherche',
            'contribution complémentaire', 'barème kilométrique'
        ],
        'quadrigrammes': [
            'loi de finances 2026', 'expert comptable Paris 8',
            'cabinet comptable Paris 8ème', 'optimisation fiscale entreprise',
            'crédit impôt recherche CIR', 'impôt sur les sociétés'
        ]
    },
    'tva-obligations': {
        'bigrammes': [
            'TVA obligations', 'obligations déclaratives', 'déclaration TVA',
            'régime TVA', 'taux TVA', 'TVA déductible', 'TVA collectée',
            'expert comptable', 'gestion TVA', 'facturation TVA'
        ],
        'trigrammes': [
            'obligations déclaratives TVA', 'déclaration de TVA',
            'régime réel normal', 'régime réel simplifié', 'franchise base TVA',
            'expert comptable Paris', 'gestion de la TVA', 'taux de TVA'
        ],
        'quadrigrammes': [
            'obligations déclaratives de TVA', 'régime réel normal TVA',
            'régime réel simplifié TVA', 'expert comptable à Paris',
            'cabinet expert comptable', 'gestion de la TVA entreprise'
        ]
    },
    'creation-entreprise': {
        'bigrammes': [
            'création entreprise', 'erreurs comptables', 'erreurs fiscales',
            'première année', 'expert comptable', 'comptabilité entreprise',
            'fiscalité entreprise', 'statut juridique', 'immatriculation RCS'
        ],
        'trigrammes': [
            'création d\'entreprise', 'erreurs comptables fiscales',
            'première année activité', 'expert comptable Paris',
            'comptabilité de l\'entreprise', 'choix statut juridique',
            'immatriculation au RCS'
        ],
        'quadrigrammes': [
            'création d\'entreprise Paris', 'erreurs comptables première année',
            'expert comptable création entreprise', 'comptabilité création entreprise',
            'fiscalité création entreprise'
        ]
    }
}

# Expressions longue traîne optimisées (basées sur les recherches réelles)
LONG_TAIL_KEYWORDS = {
    'loi-finances-2026': [
        'loi de finances 2026 impact entreprise',
        'loi finances 2026 nouveautés fiscales',
        'loi finances 2026 impôt sociétés',
        'loi finances 2026 CVAE',
        'loi finances 2026 crédit impôt',
        'expert comptable Paris loi finances 2026',
        'optimisation fiscale loi finances 2026',
        'loi finances 2026 PME Paris'
    ],
    'tva-obligations': [
        'obligations déclaratives TVA dirigeant',
        'TVA obligations ce que dirigeant doit savoir',
        'régime TVA entreprise choisir',
        'déclaration TVA échéances 2026',
        'expert comptable gestion TVA',
        'TVA intracommunautaire obligations',
        'facturation TVA mentions obligatoires'
    ],
    'creation-entreprise': [
        'erreurs comptables création entreprise éviter',
        'erreurs fiscales première année entreprise',
        'création entreprise erreurs comptables fiscales',
        'expert comptable création entreprise Paris',
        'comptabilité création entreprise guide',
        'statut juridique création entreprise choisir'
    ]
}

def get_optimized_ngrams(article_slug):
    """Retourne les n-grammes optimisés pour un article"""
    return OPTIMIZED_NGRAMS.get(article_slug, {})

def get_long_tail_keywords(article_slug):
    """Retourne les mots-clés longue traîne pour un article"""
    return LONG_TAIL_KEYWORDS.get(article_slug, [])

def analyze_content_ngrams(content):
    """Analyse les n-grammes présents dans un contenu"""
    import re
    from collections import Counter
    
    # Nettoyer le contenu (supprimer HTML, markdown)
    text = re.sub(r'<[^>]+>', '', content)
    text = re.sub(r'[#*\[\]()]', '', text)
    words = text.lower().split()
    
    # Extraire bigrammes et trigrammes
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
    
    # Compter les fréquences
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)
    
    return {
        'bigrams': dict(bigram_counts.most_common(20)),
        'trigrams': dict(trigram_counts.most_common(20))
    }

def suggest_improvements(content, article_slug):
    """Suggère des améliorations basées sur les n-grammes optimisés"""
    optimized = get_optimized_ngrams(article_slug)
    current_ngrams = analyze_content_ngrams(content)
    
    suggestions = {
        'missing_bigrams': [],
        'missing_trigrams': [],
        'underused_expressions': []
    }
    
    # Identifier les bigrammes manquants
    if 'bigrammes' in optimized:
        for bigram in optimized['bigrammes']:
            if bigram.lower() not in [b.lower() for b in current_ngrams['bigrams'].keys()]:
                suggestions['missing_bigrams'].append(bigram)
    
    # Identifier les trigrammes manquants
    if 'trigrammes' in optimized:
        for trigram in optimized['trigrammes']:
            if trigram.lower() not in [t.lower() for t in current_ngrams['trigrams'].keys()]:
                suggestions['missing_trigrams'].append(trigram)
    
    return suggestions

