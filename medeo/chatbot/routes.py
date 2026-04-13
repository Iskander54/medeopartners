from flask import (render_template, request, Blueprint, g, current_app,
                   jsonify, redirect, url_for, abort, session)
from flask_babel import _
import json
import os
import uuid
from datetime import datetime
import requests

from medeo import db
from medeo.models import ChatbotSession, ChatbotMessage, ChatbotUsageLog
from medeo.chatbot.services import get_chatbot_service

chatbot = Blueprint('chatbot', __name__, url_prefix='/<lang_code>/chatbot')

# Limite de messages par session (configurable via env)
SESSION_MSG_LIMIT = int(os.getenv('CHATBOT_SESSION_LIMIT', '20'))
SESSION_SOFT_LIMIT = max(1, SESSION_MSG_LIMIT - 3)  # avertissement avant la limite


@chatbot.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@chatbot.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@chatbot.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en/chatbot' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except Exception:
            abort(404)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _get_or_create_session(session_id: str) -> ChatbotSession:
    """Récupère ou crée une ChatbotSession en DB."""
    chat_session = ChatbotSession.query.filter_by(session_identifier=session_id).first()
    if not chat_session:
        chat_session = ChatbotSession(
            session_identifier=session_id,
            lang_code=g.lang_code,
            ip_address=request.remote_addr,
        )
        db.session.add(chat_session)
        db.session.commit()
    return chat_session


def _get_relevant_articles(query: str) -> list:
    """Récupère les articles pertinents du blog via l'API interne."""
    try:
        lang = getattr(g, 'lang_code', 'fr')
        response = requests.get(
            f"{request.url_root}{lang}/blog/api/articles",
            timeout=3
        )
        if response.status_code == 200:
            articles = response.json()
            query_words = set(query.lower().split())
            scored = []
            for art in articles:
                title_words = set(art.get('title', '').lower().split())
                excerpt_words = set(art.get('excerpt', '').lower().split())
                relevance = len(query_words & title_words) * 3 + len(query_words & excerpt_words)
                if relevance > 0:
                    scored.append({**art, 'relevance': relevance})
            scored.sort(key=lambda x: x['relevance'], reverse=True)
            return scored[:3]
    except Exception as e:
        current_app.logger.debug(f"Chatbot: articles non disponibles: {e}")
    return []


def _build_articles_context(articles: list) -> str:
    if not articles:
        return ''
    lines = []
    for art in articles:
        lines.append(f"- **{art['title']}** : {art.get('excerpt', '')} (Lire : {art.get('url', '')})")
    return '\n'.join(lines)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@chatbot.route("/")
def index():
    """Page principale du chatbot."""
    if 'chatbot_session_id' not in session:
        session['chatbot_session_id'] = str(uuid.uuid4())

    sid = session['chatbot_session_id']
    msg_count = 0
    try:
        chat_session = ChatbotSession.query.filter_by(session_identifier=sid).first()
        if chat_session:
            msg_count = ChatbotMessage.query.filter_by(
                session_id=chat_session.id, role='user'
            ).count()
    except Exception:
        pass

    msgs_remaining = max(0, SESSION_MSG_LIMIT - msg_count)

    return render_template(
        'chatbot/index.html',
        title='Assistant Fiscal IA — Medeo Partners',
        meta_description='Posez vos questions fiscales et comptables à notre assistant expert IA. Conseils gratuits basés sur la réglementation française.',
        msgs_remaining=msgs_remaining,
        session_limit=SESSION_MSG_LIMIT,
        contact_phone='01 83 64 16 04',
        contact_email='contact@medeo-partners.com',
    )


@chatbot.route("/api/chat", methods=['POST'])
def chat():
    """API principale du chatbot."""
    try:
        data = request.get_json(silent=True) or {}
        user_message = (data.get('message') or '').strip()
        client_session_id = data.get('session_id') or session.get('chatbot_session_id')

        if not user_message:
            return jsonify({'error': 'Message vide'}), 400

        if len(user_message) > 800:
            return jsonify({'error': 'Message trop long (max 800 caractères)'}), 400

        # Session ID
        if not client_session_id:
            client_session_id = str(uuid.uuid4())
        session['chatbot_session_id'] = client_session_id

        # Persistance DB
        try:
            chat_session = _get_or_create_session(client_session_id)

            # Compter les questions de cet utilisateur
            user_msg_count = ChatbotMessage.query.filter_by(
                session_id=chat_session.id, role='user'
            ).count()

            if user_msg_count >= SESSION_MSG_LIMIT:
                return jsonify({
                    'response': '',
                    'limit_reached': True,
                    'msgs_remaining': 0,
                    'session_id': client_session_id,
                    'message': (
                        "Vous avez atteint la limite de cette session. "
                        "Pour obtenir des conseils personnalisés et approfondis, "
                        "contactez directement notre cabinet."
                    ),
                    'contact_info': {
                        'phone': '01 83 64 16 04',
                        'email': 'contact@medeo-partners.com',
                        'address': '97 Boulevard Malesherbes, 75008 Paris',
                        'contact_url': url_for('main.nouscontacter', lang_code=g.lang_code),
                    },
                })

            # Historique des messages (20 derniers max)
            past_messages = ChatbotMessage.query.filter_by(
                session_id=chat_session.id
            ).order_by(ChatbotMessage.created_at.asc()).limit(40).all()

            history = [{'role': m.role, 'content': m.content} for m in past_messages]
            history.append({'role': 'user', 'content': user_message})

        except Exception as db_err:
            current_app.logger.warning(f"Chatbot DB error: {db_err}")
            # Fallback sans persistance
            chat_session = None
            history = data.get('history', [])
            history.append({'role': 'user', 'content': user_message})
            user_msg_count = len([m for m in history if m['role'] == 'user']) - 1

        # Articles pertinents
        relevant_articles = _get_relevant_articles(user_message)
        articles_context = _build_articles_context(relevant_articles)

        # Appel au service IA
        service = get_chatbot_service()
        result = service.get_response(history, articles_context)

        ai_response = result.get('response', '')
        msgs_remaining = max(0, SESSION_MSG_LIMIT - (user_msg_count + 1))

        # Sauvegarder en DB
        if chat_session:
            try:
                db.session.add(ChatbotMessage(
                    session_id=chat_session.id, role='user', content=user_message
                ))
                db.session.add(ChatbotMessage(
                    session_id=chat_session.id, role='assistant', content=ai_response
                ))
                db.session.add(ChatbotUsageLog(
                    session_id=chat_session.id,
                    provider=result.get('provider', 'unknown'),
                    model=result.get('model', ''),
                    prompt_tokens=result.get('prompt_tokens', 0),
                    completion_tokens=result.get('completion_tokens', 0),
                ))
                chat_session.last_activity = datetime.utcnow()
                db.session.commit()
            except Exception as e:
                current_app.logger.warning(f"Chatbot: impossible de sauver en DB: {e}")
                db.session.rollback()

        # Préparer la réponse JSON
        response_payload = {
            'response': ai_response,
            'relevant_articles': relevant_articles,
            'session_id': client_session_id,
            'msgs_remaining': msgs_remaining,
            'limit_reached': msgs_remaining == 0,
            'provider': result.get('provider'),
            'history': history[-20:],  # retourner l'historique tronqué au client
        }

        if msgs_remaining <= 3 and msgs_remaining > 0:
            response_payload['warning_message'] = (
                f"Plus que {msgs_remaining} question{'s' if msgs_remaining > 1 else ''} "
                "dans cette session. Pour un accompagnement complet, contactez notre cabinet."
            )

        if msgs_remaining == 0:
            response_payload['contact_info'] = {
                'phone': '01 83 64 16 04',
                'email': 'contact@medeo-partners.com',
                'contact_url': url_for('main.nouscontacter', lang_code=g.lang_code),
            }

        return jsonify(response_payload)

    except Exception as e:
        current_app.logger.error(f"Erreur chat API: {e}", exc_info=True)
        return jsonify({'error': 'Erreur serveur'}), 500


@chatbot.route("/api/health")
def health():
    """Vérification disponibilité du service."""
    try:
        service = get_chatbot_service()
        ok = service.health_check()
        provider = os.getenv('CHATBOT_PROVIDER', 'groq' if os.getenv('GROQ_API_KEY') else 'openai')
        return jsonify({'status': 'ok' if ok else 'degraded', 'provider': provider})
    except Exception:
        return jsonify({'status': 'error'}), 503


@chatbot.route("/api/reset", methods=['POST'])
def reset_chat():
    """Réinitialise la session (crée un nouvel ID)."""
    new_session_id = str(uuid.uuid4())
    session['chatbot_session_id'] = new_session_id
    return jsonify({'success': True, 'session_id': new_session_id})


@chatbot.route("/api/faq")
def faq():
    """Questions fréquentes fiscales."""
    faqs = [
        {
            'question': 'Quels sont les seuils de TVA en 2026 ?',
            'answer': 'Franchise en base : 37 500 € pour les services, 85 000 € pour les ventes. Régime réel simplifié jusqu\'à 254 000 € (services) ou 840 000 € (ventes).'
        },
        {
            'question': 'Comment optimiser fiscalement mon entreprise ?',
            'answer': 'Les leviers principaux : choix du régime fiscal (IS vs IR), rémunération du dirigeant, holding patrimoniale, crédits d\'impôt (CIR, CII), provisions réglementées. Chaque situation est unique — consultez un expert-comptable.'
        },
        {
            'question': 'SAS ou SARL : quelle forme juridique choisir ?',
            'answer': 'La SAS offre plus de liberté statutaire et une meilleure image (levée de fonds), la SARL est plus encadrée et adaptée aux structures familiales. Le régime social du dirigeant diffère : assimilé-salarié en SAS, TNS en SARL.'
        },
        {
            'question': 'Quelles sont les obligations comptables d\'une SAS ?',
            'answer': 'Tenue d\'une comptabilité régulière, établissement des comptes annuels (bilan, CR, annexe), dépôt au greffe. Audit légal obligatoire si 2 des 3 seuils dépassés : 4M€ bilan, 8M€ CA, 50 salariés.'
        },
        {
            'question': 'Qu\'est-ce que le régime micro-entrepreneur ?',
            'answer': 'Régime simplifié : abattement forfaitaire sur le CA (71% achat-revente, 50% services BIC, 34% BNC). Plafonds 2026 : 188 700 € (ventes) et 77 700 € (services). Franchise de TVA en dessous de 37 500 €.'
        },
        {
            'question': 'Comment déclarer sa TVA ?',
            'answer': 'Via le portail impots.gouv.fr, formulaire CA3 (mensuel/trimestriel) ou CA12 (annuel simplifié). Délai : le 15 ou 24 du mois suivant la période. La TVA déductible s\'impute sur la TVA collectée.'
        },
    ]
    return jsonify({'faqs': faqs})


@chatbot.route("/api/categories")
def categories():
    """Catégories de questions."""
    cats = [
        {'id': 'comptabilite', 'name': 'Comptabilité Générale', 'icon': '📊',
         'description': 'Plan comptable, écritures, bilan, compte de résultat'},
        {'id': 'fiscalite-entreprise', 'name': 'Fiscalité des Entreprises', 'icon': '🏢',
         'description': 'TVA, IS, CVAE, CFE, optimisation fiscale'},
        {'id': 'fiscalite-particulier', 'name': 'Fiscalité des Particuliers', 'icon': '👤',
         'description': 'IR, IFI, LMNP, défiscalisation'},
        {'id': 'creation', 'name': 'Création d\'Entreprise', 'icon': '🚀',
         'description': 'Statuts, SAS, SARL, micro-entrepreneur'},
        {'id': 'social', 'name': 'Social et Paie', 'icon': '👥',
         'description': 'DSN, cotisations, bulletins de paie, charges'},
        {'id': 'audit', 'name': 'Audit et Contrôle', 'icon': '🔍',
         'description': 'Audit légal, CAC, conformité réglementaire'},
    ]
    return jsonify({'categories': cats})
