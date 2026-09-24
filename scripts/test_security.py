"""Vérifie le durcissement sécurité (code uniquement).

Usage :  PYTHONPATH=. python scripts/test_security.py
"""
import os
import sys

os.environ.setdefault('SECRET_KEY', 'test-only-not-a-real-secret')


def main():
    import medeo
    from medeo import create_app
    from medeo.config import Config

    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    failures = []

    def check(label, ok, detail=''):
        print(f"  {'OK ' if ok else 'KO '} {label}{(' — ' + detail) if detail else ''}")
        if not ok:
            failures.append(label)

    # ---------------------------------------------------------------- 1
    print('1. Open redirect : ?next= ne peut pas sortir du site')
    from medeo.security import safe_redirect_target
    hostile = [
        'https://evil.example/phishing',
        '//evil.example/phishing',
        'http://evil.example',
        '\\\\evil.example',
        'javascript:alert(1)',
    ]
    with app.test_request_context('/', base_url='https://localhost'):
        for target in hostile:
            check(f'rejeté : {target!r}', safe_redirect_target(target) is None,
                  repr(safe_redirect_target(target)))
        for target in ['/fr/accueil', '/fr/blog/?page=2', 'https://localhost/fr/accueil']:
            check(f'accepté : {target!r}', safe_redirect_target(target) == target)

    # ---------------------------------------------------------------- 2
    print('2. X-Forwarded-For : la première entrée (falsifiable) est ignorée')
    from medeo.security import get_client_ip
    # Un proxy de confiance (App Engine) : l'IP réelle est l'avant-dernière.
    with app.test_request_context(
            '/', headers={'X-Forwarded-For': '1.2.3.4, 9.9.9.9, 10.0.0.1'},
            environ_base={'REMOTE_ADDR': '10.0.0.1'}):
        got = get_client_ip(trusted_proxy_count=1)
        check("l'IP annoncée par le client (1.2.3.4) n'est pas retenue",
              got != '1.2.3.4', got)
        check('IP retenue = avant-dernier saut', got == '9.9.9.9', got)
    # X-Real-IP ne doit plus être pris en compte du tout.
    with app.test_request_context('/', headers={'X-Real-IP': '6.6.6.6'},
                                  environ_base={'REMOTE_ADDR': '10.0.0.1'}):
        check('X-Real-IP ignoré', get_client_ip() == '10.0.0.1', get_client_ip())

    # ---------------------------------------------------------------- 3
    print('3. En-têtes de sécurité présents')
    client = app.test_client()
    # Hôte de production : en localhost on ne pose volontairement pas HSTS.
    PROD = 'https://www.medeo-partners.com'
    resp = client.get('/fr/accueil', base_url=PROD)
    expected = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }
    for header, value in expected.items():
        check(f'{header}: {value}', resp.headers.get(header) == value,
              str(resp.headers.get(header)))
    check('Strict-Transport-Security posé en https',
          'max-age=31536000' in resp.headers.get('Strict-Transport-Security', ''),
          str(resp.headers.get('Strict-Transport-Security')))
    check('CSP en Report-Only par défaut',
          'Content-Security-Policy-Report-Only' in resp.headers)
    check('Permissions-Policy posé', 'Permissions-Policy' in resp.headers)

    print("   HSTS n'est pas posé en local (http), sinon https://localhost est épinglé")
    resp_local = client.get('/fr/accueil', base_url='http://localhost')
    check('pas de HSTS en local',
          'Strict-Transport-Security' not in resp_local.headers)

    # ---------------------------------------------------------------- 4
    print('4. Cookies durcis')
    check('SESSION_COOKIE_HTTPONLY', app.config['SESSION_COOKIE_HTTPONLY'] is True)
    check('SESSION_COOKIE_SAMESITE=Lax', app.config['SESSION_COOKIE_SAMESITE'] == 'Lax')
    check('SESSION_COOKIE_SECURE', app.config['SESSION_COOKIE_SECURE'] is True)
    check('REMEMBER_COOKIE_HTTPONLY', app.config['REMEMBER_COOKIE_HTTPONLY'] is True)

    # ---------------------------------------------------------------- 5
    print('5. SECRET_KEY : plus aucun repli sur la clé de tutoriel')
    import inspect
    from medeo import config as config_module
    src = inspect.getsource(config_module)
    check("la clé de tutoriel n'est plus dans medeo/config.py",
          '5791628bb0b13ce0c676dfde280ba245' not in src)
    with open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'config_local.py'), encoding='utf-8') as fh:
        check("la clé de tutoriel n'est plus dans config_local.py",
              '5791628bb0b13ce0c676dfde280ba245' not in fh.read())

    print("   create_app() refuse de démarrer sans SECRET_KEY")

    class NoSecret(Config):
        SECRET_KEY = None
    try:
        create_app(NoSecret)
        check('RuntimeError levée sans SECRET_KEY', False, 'aucune exception')
    except RuntimeError as e:
        check('RuntimeError levée sans SECRET_KEY', 'SECRET_KEY' in str(e))

    print('   create_app() honore enfin son paramètre config_class')

    class Marker(Config):
        MARQUEUR_TEST = 'applique'
    check('config_class pris en compte',
          create_app(Marker).config.get('MARQUEUR_TEST') == 'applique')

    # ---------------------------------------------------------------- 6
    print('6. Limitation de débit sur les routes d\'authentification')
    check('Flask-Limiter initialisé', medeo.limiter is not None)
    # Vérification fonctionnelle : le 11e POST /login dans la minute est refusé.
    # NB : la vue /login renvoie 500 (login.html n'existe pas dans le dépôt,
    # cf. note de la PR) ; ce qui compte ici est que le limiteur intercepte
    # AVANT d'atteindre la vue.
    # App neuve : on doit enregistrer le handler avant la première requête.
    rl_app = create_app()
    rl_app.config['SERVER_NAME'] = 'localhost'
    rl_app.config['RATELIMIT_ENABLED'] = True
    rl_app.config['PROPAGATE_EXCEPTIONS'] = False
    # La page d'erreur par défaut plante elle-même sur cette branche (double
    # faute corrigée dans la PR #37) : on neutralise le handler 500 pour que
    # le test observe bien les codes renvoyés par le limiteur.
    rl_app.register_error_handler(500, lambda e: ('erreur', 500))
    codes = []
    with rl_app.test_client() as c:
        for _ in range(12):
            r = c.post('/login', data={'email': 'a@b.c', 'password': 'x'},
                       base_url=PROD)
            codes.append(r.status_code)
    check('POST /login finit par renvoyer 429', 429 in codes, f'codes={codes}')
    check('les 10 premières tentatives ne sont pas bloquées',
          codes[0] != 429 and codes.count(429) == 2, f'codes={codes}')

    # ---------------------------------------------------------------- 7
    print('7. Google Translate côté client supprimé')
    body = client.get('/fr/accueil', base_url=PROD).get_data(as_text=True)
    check('plus de const apiKey dans le HTML', 'const apiKey' not in body)
    check('plus d\'appel à translation.googleapis.com',
          'translation.googleapis.com/language/translate' not in body)
    check('fonction autoTranslateContent supprimée',
          'autoTranslateContent' not in body)

    # ---------------------------------------------------------------- 8
    print('8. Artefacts dé-suivis de git')
    import subprocess
    tracked = subprocess.run(['git', 'ls-files'], capture_output=True,
                             text=True).stdout.splitlines()
    for pattern in ('medeo/site.db', 'get-pip.py', 'medeo/pyvenv.cfg'):
        check(f'{pattern} n\'est plus suivi', pattern not in tracked)
    check('le venv medeo/bin/ n\'est plus suivi',
          not any(t.startswith('medeo/bin/') for t in tracked))

    print()
    if failures:
        print(f"ECHEC : {len(failures)} vérification(s)")
        return 1
    print('SUCCES : toutes les vérifications passent.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
