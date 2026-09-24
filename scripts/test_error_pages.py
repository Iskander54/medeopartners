"""Vérifie que les pages d'erreur ne produisent jamais de double faute.

Usage :  PYTHONPATH=. python scripts/test_error_pages.py
"""
import os
import sys

os.environ.setdefault('SECRET_KEY', 'test-only-not-a-real-secret')


def main():
    from medeo import create_app

    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    client = app.test_client()

    failures = []

    def check(label, got, expected):
        ok = got == expected
        print(f"  {'OK ' if ok else 'KO '} {label}: {got} (attendu {expected})")
        if not ok:
            failures.append(label)

    print('1. Préfixe de langue seul -> 301 vers accueil (était 500 en prod)')
    for path in ('/fr/', '/en/', '/fr', '/en'):
        check(path, client.get(path).status_code, 301)

    print('2. Racine -> 301 (et non 302 par défaut)')
    check('/', client.get('/').status_code, 301)

    print('3. URL inconnue -> 404 rendu proprement, pas 500')
    for path in ('/fr/page-qui-nexiste-pas', '/en/no-such-page', '/totalement-inconnu'):
        check(path, client.get(path).status_code, 404)

    print("4. La page 404 se rend bien (contenu, pas la page brute Werkzeug)")
    body = client.get('/fr/page-qui-nexiste-pas').get_data(as_text=True)
    ok = 'Page introuvable' in body and 'Internal Server Error' not in body
    print(f"  {'OK ' if ok else 'KO '} contenu 404 FR")
    if not ok:
        failures.append('contenu 404')

    print('5. Repli autonome si le template d\'erreur casse')
    # On simule un template d'erreur cassé : le handler doit renvoyer la page
    # de secours avec le bon code, jamais propager l'exception.
    import medeo.errors.handlers as handlers

    with app.test_request_context('/fr/nimporte-quoi'):
        html, code = handlers._render_error('errors/template-inexistant.html', 500)
    ok = code == 500 and 'Medeo Partners' in html and 'url_for' not in html
    print(f"  {'OK ' if ok else 'KO '} repli 500 autonome (code={code})")
    if not ok:
        failures.append('repli autonome')

    print('6. Pages réelles toujours 200')
    for path in ('/fr/accueil', '/en/home', '/fr/blog/'):
        check(path, client.get(path).status_code, 200)

    print()
    if failures:
        print(f"ECHEC : {len(failures)} vérification(s) -> {', '.join(failures)}")
        return 1
    print('SUCCES : toutes les vérifications passent.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
