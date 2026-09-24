from flask import Blueprint, render_template, request, g, current_app
from flask_babel import _, refresh

errors = Blueprint('errors', __name__, url_prefix='/<lang_code>')

# Page de secours totalement autonome : aucun url_for, aucun héritage de layout.
# Sert uniquement si le rendu du template normal échoue (ex. BuildError dans
# layout.html). Sans elle, une erreur dans la page d'erreur produit une double
# faute et Werkzeug renvoie sa page « Internal Server Error » brute.
_FALLBACK_PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Medeo Partners &ndash; {code}</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;
display:flex;min-height:100vh;align-items:center;justify-content:center;
background:#f8fafc;color:#1f2937;text-align:center;padding:1.5rem}}
h1{{font-size:1.5rem;margin:0 0 .75rem}}
p{{margin:0 0 1.5rem;color:#4b5563}}
a{{display:inline-block;padding:.65rem 1.25rem;border-radius:.5rem;
background:#1d4ed8;color:#fff;text-decoration:none}}
</style>
</head>
<body>
<main>
<h1>{title}</h1>
<p>{message}</p>
<a href="/{lang}/accueil">{cta}</a>
</main>
</body>
</html>"""

_FALLBACK_TEXT = {
    404: {
        'fr': ('Page introuvable (404)',
               "Cette page n'existe pas ou a été déplacée."),
        'en': ('Page not found (404)',
               'This page does not exist or has been moved.'),
    },
    403: {
        'fr': ('Accès refusé (403)',
               "Vous n'avez pas les droits nécessaires pour accéder à cette page."),
        'en': ('Access denied (403)',
               'You do not have permission to access this page.'),
    },
    500: {
        'fr': ('Une erreur est survenue (500)',
               'Un incident technique est en cours. Merci de réessayer dans quelques instants.'),
        'en': ('Something went wrong (500)',
               "We're experiencing some trouble on our end. Please try again shortly."),
    },
}

_FALLBACK_CTA = {'fr': "Retour à l'accueil", 'en': 'Back to home'}


def _lang_code():
    """Langue courante, avec repli sur le préfixe d'URL puis sur le français."""
    lang = g.get('lang_code', None)
    if lang in ('fr', 'en'):
        return lang
    segment = request.path.lstrip('/').split('/', 1)[0]
    return segment if segment in ('fr', 'en') else 'fr'


def _render_error(template, code):
    """Rend la page d'erreur, avec repli autonome si le template échoue."""
    lang = _lang_code()
    # Le template et layout.html lisent g.lang_code directement.
    g.lang_code = lang
    try:
        return render_template(template), code
    except Exception:
        current_app.logger.exception(
            "Echec du rendu de la page d'erreur %s, repli sur la page autonome", code
        )
        title, message = _FALLBACK_TEXT[code][lang]
        html = _FALLBACK_PAGE.format(
            lang=lang, code=code, title=title, message=message,
            cta=_FALLBACK_CTA[lang],
        )
        return html, code


@errors.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@errors.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@errors.app_errorhandler(404)
def error_404(error):
    return _render_error('errors/404.html', 404)


@errors.app_errorhandler(403)
def error_403(error):
    return _render_error('errors/403.html', 403)


@errors.app_errorhandler(500)
def error_500(error):
    return _render_error('errors/500.html', 500)
