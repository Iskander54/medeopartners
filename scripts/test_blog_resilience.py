"""Vérifie que le blog ne renvoie jamais de 500, DB up comme DB down.

Usage :  PYTHONPATH=. python scripts/test_blog_resilience.py
"""
import datetime
import os
import subprocess
import sys
import tempfile


def run_db_down():
    os.environ['DATABASE_URL'] = 'sqlite:////nonexistent-dir/does-not-exist.db'
    from medeo import create_app

    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    client = app.test_client()

    # 503 = DB indisponible et rien de statique à servir (signal SEO correct,
    # surtout pas une 500). 200 = servi depuis les templates statiques.
    checks = [
        ('/fr/blog/', 200),
        ('/fr/blog/article/tva-obligations-declaratives-dirigeants', 200),
        ('/fr/blog/article/creation-entreprise-erreurs-comptables-fiscales-premiere-annee', 200),
        ('/fr/blog/article/loi-finances-2026-impact-entreprise', 200),
        ('/fr/blog/article/slug-inexistant', 404),
        ('/fr/blog/categorie/fiscal', 503),
        ('/fr/blog/tag/tva', 503),
        ('/fr/blog/recherche?q=tva', 200),
        ('/fr/blog/plan-du-site', 200),
        ('/fr/blog/api/articles', 200),
        ('/fr/blog/api/categories', 200),
    ]
    failed = _assert_statuses(client, checks, 'DB DOWN')

    body = client.get('/fr/blog/').get_data(as_text=True)
    failed |= _assert(u'Nos guides de référence' in body,
                      'DB DOWN', "l'index sert les articles statiques en repli")
    return failed


def run_db_up():
    db_path = os.path.join(tempfile.mkdtemp(), 'test.db')
    os.environ['DATABASE_URL'] = 'sqlite:///' + db_path
    from medeo import create_app, db
    from medeo.models import BlogArticle, BlogCategory, BlogTag

    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    with app.app_context():
        db.create_all()
        category = BlogCategory(name='Fiscal', slug='fiscal', description='Actus fiscales')
        db.session.add(category)
        db.session.commit()
        tag = BlogTag(name='TVA', slug='tva')
        db.session.add(tag)
        db.session.commit()
        article = BlogArticle(title='Article DB test', slug='article-db-test',
                              content='Contenu', excerpt='Extrait de test',
                              status='published', category_id=category.id,
                              published_at=datetime.datetime(2026, 1, 5))
        db.session.add(article)
        db.session.commit()
        article.tags.append(tag)
        db.session.commit()

    client = app.test_client()
    checks = [
        ('/fr/blog/', 200),
        ('/fr/blog/article/article-db-test', 200),
        ('/fr/blog/article/tva-obligations-declaratives-dirigeants', 200),
        ('/fr/blog/categorie/fiscal', 200),
        ('/fr/blog/categorie/inconnue', 404),
        ('/fr/blog/tag/tva', 200),
        ('/fr/blog/tag/inconnu', 404),
        ('/fr/blog/recherche?q=test', 200),
        ('/fr/blog/plan-du-site', 200),
    ]
    failed = _assert_statuses(client, checks, 'DB UP')

    body = client.get('/fr/blog/').get_data(as_text=True)
    failed |= _assert('Article DB test' in body and u'Nos guides de référence' not in body,
                      'DB UP', "l'index sert les articles DB (pas le repli statique)")
    body = client.get('/fr/blog/article/loi-finances-2026-impact-entreprise').get_data(as_text=True)
    failed |= _assert('id="introduction"' in body and '{#introduction}' not in body,
                      'DB UP', 'les ancres markdown deviennent des id HTML')
    return failed


def _assert_statuses(client, checks, label):
    failed = False
    for url, expected in checks:
        status = client.get(url).status_code
        failed |= _assert(status == expected, label, f'{url} -> {status} (attendu {expected})')
    return failed


def _assert(condition, label, message):
    print(f"{'OK  ' if condition else 'FAIL'} [{label}] {message}")
    return not condition


if __name__ == '__main__':
    # Chaque scénario a besoin d'une app fraîche : on relance un process par cas.
    scenario = sys.argv[1] if len(sys.argv) > 1 else None
    os.environ.setdefault('SECRET_KEY', 'test-blog-resilience')
    if scenario == 'db-down':
        sys.exit(1 if run_db_down() else 0)
    if scenario == 'db-up':
        sys.exit(1 if run_db_up() else 0)

    failed = False
    for case in ('db-up', 'db-down'):
        failed |= subprocess.call([sys.executable, __file__, case]) != 0
    print('\n' + ('ÉCHEC' if failed else 'TOUT OK'))
    sys.exit(1 if failed else 0)
