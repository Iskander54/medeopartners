"""
IndexNow — notification immédiate à Bing/Yandex lors de la publication d'un article.

IndexNow est le protocole utilisé par Bing (et donc ChatGPT via Bing)
pour indexer les nouvelles URLs en quelques minutes au lieu de jours.

Usage :
    from medeo.utils.indexnow import notify_indexnow
    notify_indexnow("https://www.medeo-partners.com/fr/blog/article/mon-article")
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "3a8fe26a40ad3a0570b5cd15f2ca5222")
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
SITE_URL = "https://www.medeo-partners.com"


def notify_indexnow(url: str) -> bool:
    """
    Notifie Bing/Yandex via IndexNow qu'une URL a été créée ou modifiée.
    Retourne True si succès (202 Accepted), False sinon.
    """
    try:
        params = {
            "url": url,
            "key": INDEXNOW_KEY,
        }
        resp = requests.get(INDEXNOW_ENDPOINT, params=params, timeout=5)
        if resp.status_code in (200, 202):
            logger.info(f"IndexNow: URL notifiée avec succès — {url}")
            return True
        else:
            logger.warning(f"IndexNow: réponse inattendue {resp.status_code} pour {url}")
            return False
    except Exception as e:
        logger.error(f"IndexNow: erreur lors de la notification de {url} — {e}")
        return False


def notify_indexnow_batch(urls: list) -> bool:
    """
    Notifie Bing/Yandex pour une liste d'URLs (jusqu'à 10 000 par appel).
    """
    if not urls:
        return False
    try:
        payload = {
            "host": "www.medeo-partners.com",
            "key": INDEXNOW_KEY,
            "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
            "urlList": urls,
        }
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code in (200, 202):
            logger.info(f"IndexNow batch: {len(urls)} URLs notifiées avec succès")
            return True
        else:
            logger.warning(f"IndexNow batch: réponse {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"IndexNow batch: erreur — {e}")
        return False
