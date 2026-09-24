"""Vérifie le JSON-LD BlogPosting inline et l'hygiène des données structurées.

Usage :  PYTHONPATH=. python scripts/test_seo_jsonld.py
"""
import json
import os
import re
import sys

os.environ.setdefault('SECRET_KEY', 'test-only-not-a-real-secret')

SLUGS = [
    'tva-obligations-declaratives-dirigeants',
    'creation-entreprise-erreurs-comptables-fiscales-premiere-annee',
    'loi-finances-2026-impact-entreprise',
]

# Champs exigés par Google pour Article/BlogPosting.
REQUIRED = ['@context', '@type', 'headline', 'datePublished', 'dateModified',
            'author', 'publisher', 'image', 'mainEntityOfPage']

INLINE_RE = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S)


def main():
    from medeo import create_app

    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    client = app.test_client()
    failures = []

    def check(label, ok, detail=''):
        print(f"  {'OK ' if ok else 'KO '} {label}{(' — ' + detail) if detail else ''}")
        if not ok:
            failures.append(label)

    print('1. JSON-LD BlogPosting inline sur chaque article (DB HS -> statique)')
    for slug in SLUGS:
        resp = client.get(f'/fr/blog/article/{slug}')
        check(f'{slug} -> 200', resp.status_code == 200, str(resp.status_code))
        body = resp.get_data(as_text=True)
        blocks = [json.loads(b) for b in INLINE_RE.findall(body)]
        posting = next((b for b in blocks if b.get('@type') == 'BlogPosting'), None)
        check(f'{slug} : bloc BlogPosting inline présent', posting is not None)
        if not posting:
            continue
        missing = [f for f in REQUIRED if not posting.get(f)]
        check(f'{slug} : champs requis Google', not missing, f"manquants={missing}")
        check(f'{slug} : headline <= 110 car.', len(posting['headline']) <= 110)
        check(f'{slug} : image en URL absolue',
              posting['image'][0].startswith('https://www.medeo-partners.com/'))
        check(f'{slug} : datePublished ISO',
              bool(re.match(r'^\d{4}-\d{2}-\d{2}', posting['datePublished'])),
              posting['datePublished'])
        check(f'{slug} : @id canonique = URL de la page',
              posting['mainEntityOfPage']['@id'].endswith(f'/fr/blog/article/{slug}'))

    print('2. Aucune AggregateRating inventée nulle part')
    aggr_in_repo = []
    for root, _dirs, files in os.walk('medeo'):
        if '__pycache__' in root:
            continue
        for name in files:
            path = os.path.join(root, name)
            try:
                with open(path, encoding='utf-8', errors='ignore') as fh:
                    if 'AggregateRating' in fh.read():
                        aggr_in_repo.append(path)
            except OSError:
                pass
    check('aucun AggregateRating dans medeo/', not aggr_in_repo, str(aggr_in_repo))

    print('3. Pas de balise Bing bidon tant que le code n\'est pas configuré')
    body = client.get('/fr/accueil').get_data(as_text=True)
    check('REMPLACER_PAR_CODE_BING absent du HTML', 'REMPLACER_PAR_CODE_BING' not in body)
    check('msvalidate.01 non émis sans configuration', 'msvalidate.01' not in body)

    app.config['BING_SITE_VERIFICATION'] = 'ABC123CODEBING'
    body = client.get('/fr/accueil').get_data(as_text=True)
    check('msvalidate.01 émis une fois configuré',
          '<meta name="msvalidate.01" content="ABC123CODEBING">' in body)

    print('4. Les pages non-article n\'émettent pas de BlogPosting')
    body = client.get('/fr/accueil').get_data(as_text=True)
    blocks = [json.loads(b) for b in INLINE_RE.findall(body)]
    check('accueil sans BlogPosting',
          not any(b.get('@type') == 'BlogPosting' for b in blocks))

    print()
    if failures:
        print(f"ECHEC : {len(failures)} vérification(s)")
        return 1
    print('SUCCES : toutes les vérifications passent.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
