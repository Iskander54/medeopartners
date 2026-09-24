"""Vérifie les correctifs d'accessibilité.

Usage :  PYTHONPATH=. python scripts/test_a11y.py
"""
import os
import re
import sys

os.environ.setdefault('SECRET_KEY', 'test-only-not-a-real-secret')

PAGES = ['/fr/accueil', '/en/home', '/fr/votre_cabinet', '/fr/notre_expertise',
         '/fr/nos_services', '/fr/nouscontacter', '/fr/actualites', '/fr/blog/']


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

    bodies = {}
    for url in PAGES:
        resp = client.get(url)
        if resp.status_code != 200:
            check(f'{url} accessible', False, str(resp.status_code))
            continue
        # On retire les commentaires HTML : ces templates contiennent
        # beaucoup d'ancien balisage commenté, invisible pour le navigateur
        # comme pour les lecteurs d'écran. Le compter fausserait les mesures.
        bodies[url] = re.sub(r'<!--.*?-->', '', resp.get_data(as_text=True),
                             flags=re.S)

    print('1. Exactement un <h1> par page')
    for url, body in bodies.items():
        n = len(re.findall(r'<h1[\s>]', body))
        check(f'{url}', n == 1, f'{n} h1')

    print('2. Balises de titre équilibrées (pas de </h1> orphelin)')
    for url, body in bodies.items():
        check(f'{url}', body.count('</h1>') == body.count('<h1'),
              f"{body.count('<h1')} ouvrants / {body.count('</h1>')} fermants")

    print('3. Le contenu de page est DANS <main>')
    for url, body in bodies.items():
        start = body.find('<main')
        end = body.find('</main>')
        check(f'{url} : <main> présent et fermé', start != -1 and end > start)
        if start == -1 or end < start:
            continue
        main_html = body[start:end]
        # Le h1 de la page doit se trouver à l'intérieur du repère principal.
        check(f'{url} : le <h1> est dans <main>', '<h1' in main_html)
        # Et <main> ne doit pas être quasi vide comme avant le correctif.
        text = re.sub(r'<[^>]+>', ' ', main_html)
        check(f'{url} : <main> contient du vrai contenu',
              len(text.split()) > 50, f'{len(text.split())} mots')

    print('4. Lien d\'évitement présent et pointant sur <main>')
    for url, body in bodies.items():
        check(f'{url} : skip-link présent',
              'class="skip-link"' in body and 'href="#contenu-principal"' in body)
        check(f'{url} : la cible existe',
              'id="contenu-principal"' in body)

    print('5. Le skip-link est le premier élément focusable du <body>')
    body = bodies['/fr/accueil']
    after_body = body[body.find('<body'):]
    first_link = after_body.find('<a ')
    skip_pos = after_body.find('class="skip-link"')
    check('skip-link en tête du body', 0 <= skip_pos <= first_link + 60,
          f'position={skip_pos}, premier <a>={first_link}')

    print('6. Tous les champs de formulaire ont un label ou un aria-label')
    for url, body in bodies.items():
        labels = set(re.findall(r'<label[^>]*\bfor="([^"]+)"', body))
        problems = []
        for tag, attrs in re.findall(r'<(input|select|textarea)\b([^>]*)>', body):
            field_type = (re.search(r'type="([^"]+)"', attrs) or [None, 'text'])[1]
            if field_type in ('hidden', 'submit', 'button', 'image', 'reset'):
                continue
            field_id = (re.search(r'\bid="([^"]+)"', attrs) or [None, None])[1]
            labelled = (field_id in labels or 'aria-label' in attrs
                        or 'aria-labelledby' in attrs)
            if not labelled:
                problems.append(f'{tag}#{field_id}')
        check(f'{url}', not problems, str(problems))

    print('7. Aucun id dupliqué (casse l\'association label/champ)')
    for url, body in bodies.items():
        ids = re.findall(r'\bid="([^"]+)"', body)
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        check(f'{url}', not dupes, str(dupes))

    print()
    if failures:
        print(f"ECHEC : {len(failures)} vérification(s)")
        return 1
    print('SUCCES : toutes les vérifications passent.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
