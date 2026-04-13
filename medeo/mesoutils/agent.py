"""
Agent IA pour Mesoutils.
Utilise Ollama via l'API compatible OpenAI avec tool/function calling.
Monitoring optionnel via Langfuse si les variables d'environnement sont configurées.
"""
import os
import json
import logging
import time
from typing import Generator

import requests

from medeo.mesoutils.tools import TOOLS_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

SYSTEM_PROMPT = """Tu es un assistant IA interne pour les collaborateurs experts-comptables du cabinet Medeo Partners.
Tu as accès à des outils spécialisés pour :
- Rechercher des informations sur des entreprises françaises via l'API Pappers (SIREN, dirigeants, bilans, statuts)
- Effectuer des calculs fiscaux (TVA, IS)
- Consulter les prochaines échéances fiscales et sociales

Règles de comportement :
1. Réponds en français de manière professionnelle et concise.
2. Utilise systématiquement les outils disponibles quand c'est pertinent (recherche d'entreprise, calculs).
3. Cite les résultats des outils dans ta réponse de manière structurée.
4. Pour les calculs fiscaux, précise toujours qu'il s'agit d'estimations indicatives.
5. En cas de doute sur une situation complexe, recommande de consulter la documentation officielle (BOFIP, CGI).
6. Ne fournis jamais de conseils fiscaux personnalisés définitifs sans préciser leurs limites.
7. Si une recherche Pappers ne donne pas de résultat, propose d'affiner avec le SIREN exact.

Tu es un outil interne professionnel, pas un chatbot public. Sois direct et efficace."""

# ---------------------------------------------------------------------------
# Langfuse monitoring (optionnel)
# ---------------------------------------------------------------------------

_langfuse = None

def _get_langfuse():
    global _langfuse
    if _langfuse is not None:
        return _langfuse
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    if secret_key and public_key:
        try:
            from langfuse import Langfuse
            _langfuse = Langfuse(secret_key=secret_key, public_key=public_key, host=host)
            logger.info("Langfuse monitoring activé.")
        except ImportError:
            logger.warning("Package langfuse non installé. Monitoring désactivé.")
        except Exception as e:
            logger.warning(f"Impossible d'initialiser Langfuse : {e}")
    return _langfuse


# ---------------------------------------------------------------------------
# Vérification de disponibilité Ollama
# ---------------------------------------------------------------------------

def check_ollama_health() -> dict:
    """Vérifie si Ollama est disponible et retourne les modèles installés."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"status": "ok", "models": models}
        return {"status": "error", "message": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Ollama non accessible (vérifiez que le service tourne sur " + OLLAMA_BASE_URL + ")"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Agent principal
# ---------------------------------------------------------------------------

class MesoutilsAgent:
    """
    Agent IA qui orchestre les appels LLM (Ollama) et l'exécution des outils.
    Utilise la boucle : LLM → tool_calls → execute → LLM → réponse finale.
    """

    def __init__(self):
        self.model = OLLAMA_MODEL
        self.base_url = OLLAMA_BASE_URL
        self.timeout = OLLAMA_TIMEOUT

    def _call_ollama(self, messages: list, tools: list = None, stream: bool = False) -> dict:
        """
        Appelle l'API Ollama /api/chat avec format OpenAI.
        Retourne la réponse complète ou lève une exception.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.3,
                "num_ctx": 8192,
            }
        }
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            if stream:
                return response
            return response.json()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Impossible de contacter Ollama sur {self.base_url}. "
                "Vérifiez que le service est démarré (docker compose up ollama)."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Timeout après {self.timeout}s. Le modèle {self.model} est peut-être trop lent "
                "ou n'est pas chargé. Essayez un modèle plus petit."
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Erreur HTTP Ollama : {e}")

    def run(self, user_message: str, history: list = None) -> dict:
        """
        Exécute l'agent pour un message utilisateur.
        Retourne : {"response": str, "tool_calls_log": list, "error": str|None}
        """
        start_time = time.time()
        history = history or []
        tool_calls_log = []

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        lf = _get_langfuse()
        trace = None
        if lf:
            try:
                trace = lf.trace(
                    name="mesoutils-agent",
                    input={"message": user_message, "history_length": len(history)},
                    metadata={"model": self.model}
                )
            except Exception:
                pass

        max_iterations = 10
        iteration = 0

        try:
            while iteration < max_iterations:
                iteration += 1

                if lf and trace:
                    try:
                        generation = trace.generation(
                            name=f"llm-call-{iteration}",
                            model=self.model,
                            input=messages
                        )
                    except Exception:
                        generation = None
                else:
                    generation = None

                raw = self._call_ollama(messages, tools=TOOLS_DEFINITIONS)

                message = raw.get("message", {})
                finish_reason = "tool_calls" if message.get("tool_calls") else "stop"

                if generation:
                    try:
                        generation.end(output=message, usage=raw.get("eval_count"))
                    except Exception:
                        pass

                if finish_reason == "tool_calls" and message.get("tool_calls"):
                    messages.append({
                        "role": "assistant",
                        "content": message.get("content", ""),
                        "tool_calls": message["tool_calls"]
                    })

                    for tool_call in message["tool_calls"]:
                        fn = tool_call.get("function", {})
                        tool_name = fn.get("name", "")
                        tool_args = fn.get("arguments", {})

                        if isinstance(tool_args, str):
                            try:
                                tool_args = json.loads(tool_args)
                            except Exception:
                                tool_args = {}

                        logger.info(f"Outil appelé : {tool_name} avec args : {tool_args}")

                        if lf and trace:
                            try:
                                span = trace.span(
                                    name=f"tool-{tool_name}",
                                    input=tool_args
                                )
                            except Exception:
                                span = None
                        else:
                            span = None

                        result = execute_tool(tool_name, tool_args)

                        if span:
                            try:
                                span.end(output=result)
                            except Exception:
                                pass

                        tool_calls_log.append({
                            "tool": tool_name,
                            "arguments": tool_args,
                            "result": result
                        })

                        messages.append({
                            "role": "tool",
                            "content": json.dumps(result, ensure_ascii=False)
                        })

                else:
                    final_response = message.get("content", "").strip()
                    elapsed = round(time.time() - start_time, 2)

                    if lf and trace:
                        try:
                            trace.update(
                                output=final_response,
                                metadata={
                                    "elapsed_seconds": elapsed,
                                    "iterations": iteration,
                                    "tool_calls_count": len(tool_calls_log)
                                }
                            )
                        except Exception:
                            pass

                    return {
                        "response": final_response,
                        "tool_calls_log": tool_calls_log,
                        "elapsed_seconds": elapsed,
                        "model": self.model,
                        "error": None
                    }

            return {
                "response": "L'agent a dépassé le nombre maximum d'itérations. Veuillez reformuler votre demande.",
                "tool_calls_log": tool_calls_log,
                "elapsed_seconds": round(time.time() - start_time, 2),
                "model": self.model,
                "error": "max_iterations_exceeded"
            }

        except RuntimeError as e:
            logger.error(f"Erreur agent : {e}")
            return {
                "response": str(e),
                "tool_calls_log": tool_calls_log,
                "elapsed_seconds": round(time.time() - start_time, 2),
                "model": self.model,
                "error": "ollama_error"
            }
        except Exception as e:
            logger.exception(f"Erreur inattendue agent : {e}")
            return {
                "response": f"Erreur inattendue : {str(e)}",
                "tool_calls_log": tool_calls_log,
                "elapsed_seconds": round(time.time() - start_time, 2),
                "model": self.model,
                "error": "unexpected_error"
            }

    def stream(self, user_message: str, history: list = None) -> Generator[str, None, None]:
        """
        Version streaming de run(). Génère des événements SSE.
        Format : data: <json>\n\n
        Types d'événements : tool_start, tool_end, token, done, error
        """
        history = history or []
        tool_calls_log = []

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        max_iterations = 10
        iteration = 0

        def sse(event_type: str, data: dict) -> str:
            payload = json.dumps({"type": event_type, **data}, ensure_ascii=False)
            return f"data: {payload}\n\n"

        try:
            while iteration < max_iterations:
                iteration += 1

                # Appel non-streaming pour gérer les tool calls proprement
                raw = self._call_ollama(messages, tools=TOOLS_DEFINITIONS, stream=False)
                message = raw.get("message", {})

                if message.get("tool_calls"):
                    messages.append({
                        "role": "assistant",
                        "content": message.get("content", ""),
                        "tool_calls": message["tool_calls"]
                    })

                    for tool_call in message["tool_calls"]:
                        fn = tool_call.get("function", {})
                        tool_name = fn.get("name", "")
                        tool_args = fn.get("arguments", {})
                        if isinstance(tool_args, str):
                            try:
                                tool_args = json.loads(tool_args)
                            except Exception:
                                tool_args = {}

                        yield sse("tool_start", {"tool": tool_name, "arguments": tool_args})

                        result = execute_tool(tool_name, tool_args)
                        tool_calls_log.append({
                            "tool": tool_name,
                            "arguments": tool_args,
                            "result": result
                        })

                        yield sse("tool_end", {
                            "tool": tool_name,
                            "result_summary": _summarize_tool_result(tool_name, result)
                        })

                        messages.append({
                            "role": "tool",
                            "content": json.dumps(result, ensure_ascii=False)
                        })
                else:
                    # Réponse finale — on streame token par token via l'API streaming Ollama
                    final_messages = list(messages)
                    try:
                        stream_response = self._call_ollama(final_messages, stream=True)
                        buffer = ""
                        for line in stream_response.iter_lines():
                            if not line:
                                continue
                            try:
                                chunk = json.loads(line)
                                token = chunk.get("message", {}).get("content", "")
                                if token:
                                    buffer += token
                                    yield sse("token", {"content": token})
                                if chunk.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
                        yield sse("done", {"tool_calls_log": tool_calls_log})
                    except Exception:
                        # Fallback : envoyer la réponse complète
                        final_response = message.get("content", "").strip()
                        yield sse("token", {"content": final_response})
                        yield sse("done", {"tool_calls_log": tool_calls_log})
                    return

        except RuntimeError as e:
            yield sse("error", {"message": str(e)})
        except Exception as e:
            logger.exception(f"Erreur stream agent : {e}")
            yield sse("error", {"message": f"Erreur inattendue : {str(e)}"})


def _summarize_tool_result(tool_name: str, result: dict) -> str:
    """Génère un résumé court d'un résultat d'outil pour l'affichage SSE."""
    if "erreur" in result:
        return f"Erreur : {result['erreur']}"
    if tool_name == "pappers_rechercher_entreprise":
        total = result.get("total", 0)
        return f"{total} entreprise(s) trouvée(s)"
    if tool_name == "pappers_fiche_entreprise":
        nom = result.get("denomination", "?")
        statut = result.get("statut", "?")
        return f"{nom} — {statut}"
    if tool_name == "pappers_dirigeants":
        nb = len(result.get("dirigeants", []))
        return f"{nb} dirigeant(s) trouvé(s)"
    if tool_name == "pappers_comptes_annuels":
        nb = len(result.get("finances", []))
        return f"{nb} exercice(s) disponible(s)"
    if tool_name == "calculer_tva":
        return f"HT: {result.get('montant_ht')}€ → TVA: {result.get('montant_tva')}€ → TTC: {result.get('montant_ttc')}€"
    if tool_name == "calculer_is":
        return f"IS estimé: {result.get('is_estime')}€ (taux effectif {result.get('taux_effectif')}%)"
    if tool_name == "info_date_echeance":
        nb = len(result.get("prochaines_echeances", []))
        return f"{nb} échéances listées"
    return "Résultat disponible"


# Instance singleton de l'agent
agent = MesoutilsAgent()
