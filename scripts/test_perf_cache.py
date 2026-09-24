"""Vérifie le versionnage des assets statiques et les en-têtes de cache.

Usage :  PYTHONPATH=. python scripts/test_perf_cache.py
"""
import os
import re
import sys

os.environ.setdefault('SECRET_KEY', 'test-only-not-a-real-secret')


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

    print('1. Les URLs statiques du HTML sont versionnées')
    body = client.get('/fr/accueil').get_data(as_text=True)
    static_urls = set(re.findall(r'/static/[^"\'\s>]+', body))
    unversioned = [u for u in static_urls if 'v=' not in u]
    check(f'{len(static_urls)} URLs statiques, toutes versionnées',
          not unversioned, f"sans version : {unversioned[:5]}")

    print('2. Une URL versionnée est mise en cache longuement et immutable')
    sample = next(u for u in static_urls if 'v=' in u)
    resp = client.get(sample)
    check('asset versionné -> 200', resp.status_code == 200, str(resp.status_code))
    cc = resp.headers.get('Cache-Control', '')
    check('Cache-Control: max-age=31536000, immutable',
          'max-age=31536000' in cc and 'immutable' in cc, cc)

    print('3. Une URL NON versionnée reste en cache court')
    resp = client.get('/static/images/logo.webp')
    cc = resp.headers.get('Cache-Control', '')
    check('Cache-Control: max-age=3600', 'max-age=3600' in cc, cc)

    print("4. Le HTML n'est jamais mis en cache longuement")
    resp = client.get('/fr/accueil')
    cc = resp.headers.get('Cache-Control', '')
    check('HTML en no-cache', 'no-cache' in cc, cc)

    print('5. La version change quand le fichier change (invalidation)')
    sample_rel = sample.split('?')[0][len('/static/'):]
    path = os.path.join(app.static_folder, sample_rel)
    os.utime(path, (1700000000, 1700000000))
    body2 = client.get('/fr/accueil').get_data(as_text=True)
    after = re.search(re.escape(sample.split('?')[0]) + r'\?v=(\d+)', body2)
    check('la version suit la date de modification du fichier',
          after is not None and after.group(1) == '1700000000',
          after.group(1) if after else 'absente')

    print('6. Toutes les images référencées dans le HTML existent vraiment')
    missing = []
    for u in static_urls:
        rel = u.split('?')[0][len('/static/'):]
        if not os.path.exists(os.path.join(app.static_folder, rel)):
            missing.append(rel)
    check('aucune référence morte', not missing, str(missing))

    print('7. Les deux images géantes non utilisées ont bien disparu')
    for name in ('successful-business-team-expressing-unity.jpg',
                 'startup-business.jpg'):
        check(f'{name} supprimée',
              not os.path.exists(os.path.join(app.static_folder, 'images', name)))

    print()
    if failures:
        print(f"ECHEC : {len(failures)} vérification(s)")
        return 1
    print('SUCCES : toutes les vérifications passent.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
