"""
Routes Flask pour le module Mesoutils.
Accès protégé par mot de passe (MESOUTILS_PASSWORD) + optionnellement par IP.
URL de base : /fr/mesoutils
"""
import hashlib
import json
import logging
import os

from flask import (
    abort, current_app, jsonify, render_template, request,
    Response, session, stream_with_context, redirect, url_for, flash
)

from medeo.mesoutils import mesoutils
from medeo.mesoutils.agent import agent, check_groq_health

logger = logging.getLogger(__name__)

_MESOUTILS_PASSWORD = os.getenv("MESOUTILS_PASSWORD", "Medeo2026$")
_SESSION_KEY = "mesoutils_auth"


def _check_password(candidate: str) -> bool:
    """Comparaison en temps constant pour éviter les timing attacks."""
    expected = hashlib.sha256(_MESOUTILS_PASSWORD.encode()).hexdigest()
    received = hashlib.sha256(candidate.encode()).hexdigest()
    return expected == received


def _is_authenticated() -> bool:
    return session.get(_SESSION_KEY) is True

# ---------------------------------------------------------------------------
# Restriction d'accès par IP
# ---------------------------------------------------------------------------

def _get_client_ip() -> str:
    """
    Retourne l'IP réelle du client en tenant compte des reverse proxies.
    Priorise X-Forwarded-For, puis X-Real-IP, puis remote_addr.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.remote_addr or ""


def _get_allowed_ips() -> list:
    """
    Retourne la liste des IPs autorisées depuis MESOUTILS_ALLOWED_IPS.
    Format : IPs séparées par des virgules (ex: "192.168.1.10,10.0.0.5").
    Si la variable est vide ou absente, AUCUNE restriction n'est appliquée.
    Pour activer la restriction, définissez la variable dans .env ou app.yaml.
    """
    raw = os.getenv("MESOUTILS_ALLOWED_IPS", "").strip()
    if raw:
        return [ip.strip() for ip in raw.split(",") if ip.strip()]
    return []  # liste vide = pas de restriction


@mesoutils.before_request
def restrict_access():
    """
    Double protection :
    1. Restriction IP optionnelle (MESOUTILS_ALLOWED_IPS)
    2. Authentification par mot de passe (MESOUTILS_PASSWORD)
    Les routes /login et /logout sont exemptées.
    """
    # Exemption des routes d'auth
    if request.endpoint in ("mesoutils.login", "mesoutils.logout"):
        return None

    # Restriction IP (optionnelle)
    allowed = _get_allowed_ips()
    if allowed:
        client_ip = _get_client_ip()
        if client_ip not in allowed:
            logger.warning(f"Accès Mesoutils refusé pour IP : {client_ip}")
            abort(403)

    # Vérification mot de passe
    if not _is_authenticated():
        return redirect(url_for("mesoutils.login", next=request.path))

    return None


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------

@mesoutils.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion protégée par mot de passe."""
    if _is_authenticated():
        return redirect(url_for("mesoutils.index"))

    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if _check_password(password):
            session[_SESSION_KEY] = True
            session.permanent = True
            next_url = request.args.get("next") or url_for("mesoutils.index")
            logger.info(f"Connexion Mesoutils réussie depuis {_get_client_ip()}")
            return redirect(next_url)
        else:
            error = "Mot de passe incorrect."
            logger.warning(f"Tentative de connexion Mesoutils échouée depuis {_get_client_ip()}")

    return render_template("mesoutils/login.html", error=error)


@mesoutils.route("/logout", methods=["POST"])
def logout():
    """Déconnexion."""
    session.pop(_SESSION_KEY, None)
    return redirect(url_for("mesoutils.login"))


# ---------------------------------------------------------------------------
# Routes principales
# ---------------------------------------------------------------------------

@mesoutils.route("/", methods=["GET"])
def index():
    """Page principale du chat agent interne."""
    health = check_groq_health()
    on_gae = bool(os.getenv("GAE_ENV") or os.getenv("GAE_APPLICATION"))
    return render_template(
        "mesoutils/index.html",
        groq_status=health,
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        pappers_configured=bool(os.getenv("PAPPERS_API_KEY")),
        langfuse_configured=bool(os.getenv("LANGFUSE_SECRET_KEY")),
        langfuse_host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
        use_sync_mode=on_gae,
    )


@mesoutils.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint synchrone : exécute l'agent et retourne la réponse complète.
    Body JSON : {"message": str, "reset": bool (optionnel)}
    """
    try:
        data = request.get_json(force=True)
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({"error": "Message vide"}), 400

        if data.get("reset"):
            session.pop("mesoutils_history", None)

        history = session.get("mesoutils_history", [])

        result = agent.run(user_message, history)

        # Mettre à jour l'historique (on ne garde que les messages user/assistant)
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": result["response"]})
        # Limite : 20 messages (10 échanges)
        if len(history) > 20:
            history = history[-20:]
        session["mesoutils_history"] = history
        session.modified = True

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Erreur /api/chat : {e}")
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500


@mesoutils.route("/api/stream", methods=["POST"])
def stream():
    """
    Endpoint streaming SSE : exécute l'agent avec retour temps réel.
    Body JSON : {"message": str, "reset": bool (optionnel)}
    Retourne un flux text/event-stream.
    """
    try:
        data = request.get_json(force=True)
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({"error": "Message vide"}), 400

        if data.get("reset"):
            session.pop("mesoutils_history", None)

        history = session.get("mesoutils_history", [])
        # On copie l'historique avant le streaming pour éviter les problèmes de session
        history_snapshot = list(history)

        def generate():
            collected_response = []
            tool_log = []

            for chunk in agent.stream(user_message, history_snapshot):
                yield chunk
                # Collecter la réponse finale pour mettre à jour l'historique
                try:
                    event_data = json.loads(chunk.replace("data: ", "").strip())
                    if event_data.get("type") == "token":
                        collected_response.append(event_data.get("content", ""))
                    elif event_data.get("type") == "done":
                        tool_log = event_data.get("tool_calls_log", [])
                except Exception:
                    pass

            # Mettre à jour l'historique après streaming (hors contexte stream)
            full_response = "".join(collected_response)
            history_snapshot.append({"role": "user", "content": user_message})
            history_snapshot.append({"role": "assistant", "content": full_response})
            updated = history_snapshot[-20:]
            session["mesoutils_history"] = updated
            session.modified = True

        return Response(
            stream_with_context(generate()),
            content_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.exception(f"Erreur /api/stream : {e}")
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500


@mesoutils.route("/api/reset", methods=["POST"])
def reset():
    """Réinitialise l'historique de conversation."""
    session.pop("mesoutils_history", None)
    return jsonify({"success": True, "message": "Conversation réinitialisée."})


@mesoutils.route("/api/status", methods=["GET"])
def status():
    """Retourne le statut des services (Groq, Pappers, Langfuse)."""
    health = check_groq_health()
    allowed = _get_allowed_ips()
    return jsonify({
        "groq": health,
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "pappers_configured": bool(os.getenv("PAPPERS_API_KEY")),
        "langfuse_configured": bool(os.getenv("LANGFUSE_SECRET_KEY")),
        "ip_restriction": "active" if allowed else "disabled",
        "allowed_ips": allowed,
        "client_ip": _get_client_ip(),
    })
