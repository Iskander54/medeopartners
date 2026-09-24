"""Helpers de sécurité transverses : IP client, redirections, en-têtes HTTP."""
import os
from urllib.parse import urljoin, urlparse

from flask import request

# Nombre de proxys de confiance devant l'application.
# App Engine place son frontend devant l'app : la dernière entrée de
# X-Forwarded-For est ajoutée par Google et est la seule non falsifiable.
TRUSTED_PROXY_COUNT = int(os.getenv('TRUSTED_PROXY_COUNT', '1'))


def get_client_ip(trusted_proxy_count=None):
    """IP réelle du client, en ne faisant confiance qu'aux proxys connus.

    X-Forwarded-For est une liste « client, proxy1, proxy2 » où seules les
    entrées ajoutées par NOS proxys sont fiables : le client contrôle
    entièrement le début de la chaîne. Prendre la première entrée, comme le
    faisait _get_client_ip(), laisse donc n'importe qui choisir l'IP que
    l'application verra — il suffit d'envoyer « X-Forwarded-For: 1.2.3.4 ».

    On compte donc depuis la DROITE : avec N proxys de confiance, l'IP du
    client est la (N+1)ème en partant de la fin. Les entrées situées avant
    sont ignorées, elles sont sous contrôle de l'appelant.

    X-Real-IP n'est PAS pris en compte : App Engine ne le pose pas, donc il ne
    peut venir que du client.
    """
    if trusted_proxy_count is None:
        trusted_proxy_count = TRUSTED_PROXY_COUNT

    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for and trusted_proxy_count > 0:
        chain = [part.strip() for part in forwarded_for.split(',') if part.strip()]
        if chain:
            index = len(chain) - trusted_proxy_count - 1
            # Chaîne plus courte qu'attendu (appel direct, proxy absent) :
            # on retombe sur l'entrée la plus à gauche disponible plutôt que
            # de sortir de la liste.
            return chain[max(index, 0)]
    return request.remote_addr or ''


def safe_redirect_target(target):
    """Valide une cible de redirection fournie par l'utilisateur.

    Sans ce filtre, ?next=https://site-malveillant.example redirige la victime
    hors du site juste après une connexion réussie : elle fait confiance au
    domaine de départ et se retrouve sur une page de phishing (open redirect).

    On n'accepte qu'un chemin interne au site : même hôte, schéma http(s), et
    pas de forme « //evil.example » que le navigateur traite comme absolue.
    """
    if not target:
        return None
    if target.startswith('//') or target.startswith('\\\\'):
        return None
    reference = urlparse(request.host_url)
    candidate = urlparse(urljoin(request.host_url, target))
    if candidate.scheme not in ('http', 'https'):
        return None
    if candidate.netloc != reference.netloc:
        return None
    return target


# Origines externes réellement utilisées par les templates. Toute CSP plus
# stricte que ça casserait le site en l'état (scripts et styles inline
# omniprésents, cf. 'unsafe-inline').
CSP_DIRECTIVES = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
    "https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com "
    "https://www.googletagmanager.com https://www.google-analytics.com "
    "https://assets.calendly.com https://www.google.com https://www.gstatic.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
    "https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com "
    "https://assets.calendly.com; "
    "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https://www.google-analytics.com "
    "https://translation.googleapis.com; "
    "frame-src https://calendly.com https://assets.calendly.com "
    "https://www.google.com https://www.youtube.com; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "object-src 'none'"
)


def apply_security_headers(response, https=True, csp_report_only=True):
    """Pose les en-têtes de sécurité sur une réponse.

    La CSP est envoyée en Report-Only par défaut : le site utilise massivement
    des scripts et styles inline et une dizaine de CDN. Passer directement en
    CSP bloquante casserait des pages sans qu'on s'en aperçoive. Report-Only
    laisse observer les violations avant de basculer (CSP_ENFORCE=1).
    """
    headers = response.headers
    headers.setdefault('X-Content-Type-Options', 'nosniff')
    headers.setdefault('X-Frame-Options', 'DENY')
    headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    headers.setdefault(
        'Permissions-Policy',
        'geolocation=(), microphone=(), camera=(), interest-cohort=()')
    if https:
        # 1 an, sous-domaines inclus. Pas de preload : c'est quasi
        # irréversible, à décider explicitement.
        headers.setdefault('Strict-Transport-Security',
                           'max-age=31536000; includeSubDomains')
    header_name = ('Content-Security-Policy-Report-Only' if csp_report_only
                   else 'Content-Security-Policy')
    headers.setdefault(header_name, CSP_DIRECTIVES)
    return response
