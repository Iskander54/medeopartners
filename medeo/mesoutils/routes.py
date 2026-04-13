"""
Routes Flask pour le module Mesoutils.
Accessible uniquement depuis les IPs autorisées (variable MESOUTILS_ALLOWED_IPS).
URL de base : /mesoutils
"""
import json
import logging
import os

from flask import (
    abort, current_app, jsonify, render_template, request,
    Response, session, stream_with_context
)

from medeo.mesoutils import mesoutils
from medeo.mesoutils.agent import agent, check_ollama_health

logger = logging.getLogger(__name__)

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
def restrict_by_ip():
    """
    Restreint l'accès par IP si MESOUTILS_ALLOWED_IPS est configurée.
    Sans cette variable, toutes les IPs sont autorisées.
    """
    allowed = _get_allowed_ips()
    if not allowed:
        return None  # Pas de restriction configurée

    client_ip = _get_client_ip()
    if client_ip not in allowed:
        logger.warning(f"Accès Mesoutils refusé pour IP : {client_ip} (IPs autorisées : {allowed})")
        abort(403)

    return None


# ---------------------------------------------------------------------------
# Routes principales
# ---------------------------------------------------------------------------

@mesoutils.route("/", methods=["GET"])
def index():
    """Page principale du chat agent interne."""
    health = check_ollama_health()
    # Sur GAE Standard, les réponses HTTP ont un timeout dur de 60s.
    # On utilise le mode sync pour éviter les coupures SSE.
    # En local ou sur GAE Flexible, le streaming SSE fonctionne pleinement.
    on_gae = bool(os.getenv("GAE_ENV") or os.getenv("GAE_APPLICATION"))
    return render_template(
        "mesoutils/index.html",
        ollama_status=health,
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:14b"),
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
    """Retourne le statut des services (Ollama, Pappers, Langfuse)."""
    health = check_ollama_health()
    allowed = _get_allowed_ips()
    return jsonify({
        "ollama": health,
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:14b"),
        "pappers_configured": bool(os.getenv("PAPPERS_API_KEY")),
        "langfuse_configured": bool(os.getenv("LANGFUSE_SECRET_KEY")),
        "ip_restriction": "active" if allowed else "disabled",
        "allowed_ips": allowed,
        "client_ip": _get_client_ip(),
    })
