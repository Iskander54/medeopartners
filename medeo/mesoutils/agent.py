"""
Agent IA pour Mesoutils.
Utilise Groq (llama-3.3-70b-versatile) avec tool/function calling.
Monitoring optionnel via Langfuse si les variables d'environnement sont configurées.
"""
import os
import json
import logging
import time
from typing import Generator

from groq import Groq, RateLimitError, APIStatusError

from medeo.mesoutils.tools import TOOLS_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = """Tu es un assistant IA interne pour les collaborateurs experts-comptables du cabinet Medeo Partners.
Tu as accès aux outils suivants. Utilise-les systématiquement dès qu'une question s'y prête.

OUTILS ENTREPRISES (APIs publiques) :
- pappers_rechercher_entreprise : recherche par nom / SIREN / SIRET (avec fallback Annuaire data.gouv.fr si Pappers est indisponible). Retourne directement le numéro TVA intracommunautaire.
- pappers_fiche_entreprise : fiche complète (dirigeants, capital, bilans, bénéficiaires effectifs).
- pappers_dirigeants : dirigeants et mandataires sociaux.
- pappers_comptes_annuels : bilans et comptes de résultat publics.
- bodacc_annonces : annonces légales BODACC (procédures collectives, liquidations, jugements, radiations). Indispensable pour due diligence avant prise de mission.
- calculer_tva_intracommunautaire : calcule le n° TVA FR depuis un SIREN.
- valider_tva_vies : valide un n° TVA intracommunautaire EU via le système VIES (Commission Européenne). Obligatoire avant toute facturation intra-UE en exonération.

OUTILS CALCULS FISCAUX ET SOCIAUX :
- calculer_tva : calcul TVA HT↔TTC (taux 20%, 10%, 5.5%, 2.1%).
- calculer_is : IS estimé selon barème PME ou taux normal.
- calculer_cotisations_tns : cotisations sociales SSI pour TNS (gérant maj. SARL, EI, indépendant).
- calculer_penalites_retard : pénalités retard B2B (art. L441-10 C.com.) avec indemnité forfaitaire 40€.
- baremes_fiscaux_sociaux : PASS, SMIC, plafonds micro BIC/BNC, tranches IR, taux IS, taux légaux.
- info_date_echeance : prochaines échéances TVA, IS, DSN, CFE selon régime.

Règles de comportement :
1. Réponds en français, de manière professionnelle et structurée (utilise des listes et tableaux markdown).
2. Utilise TOUJOURS les outils disponibles avant de répondre de mémoire.
3. Pour trouver le n° TVA d'une entreprise : utilise pappers_rechercher_entreprise (champ tva_intracommunautaire inclus) ou calculer_tva_intracommunautaire si tu as le SIREN.
4. Pour valider un n° TVA reçu d'un client EU : utilise valider_tva_vies.
5. Pour un nouveau client : propose de consulter BODACC pour détecter d'éventuelles procédures en cours.
6. Mentionne toujours la source des données (Pappers / Annuaire Entreprises / BODACC / VIES).
7. Pour les calculs fiscaux et sociaux, précise qu'il s'agit d'estimations indicatives à valider.
8. En cas de situation complexe, cite les textes de référence (CGI, BOFIP, C.com., URSSAF).

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
# Health check
# ---------------------------------------------------------------------------

def check_groq_health() -> dict:
    """Vérifie si la clé API Groq est configurée."""
    if not GROQ_API_KEY:
        return {
            "status": "error",
            "message": "Clé API Groq non configurée (variable GROQ_API_KEY manquante)."
        }
    return {"status": "ok", "model": GROQ_MODEL}


# ---------------------------------------------------------------------------
# Agent principal
# ---------------------------------------------------------------------------

class MesoutilsAgent:
    """
    Agent IA qui orchestre les appels LLM (Groq) et l'exécution des outils.
    Utilise la boucle : LLM → tool_calls → execute → LLM → réponse finale.
    """

    def __init__(self):
        self.model = GROQ_MODEL
        # max_retries=0 : désactive le sleep automatique du SDK Groq en cas de 429.
        # Sans ça, time.sleep() bloque le worker gunicorn qui se fait tuer (SIGKILL → 500).
        self.client = Groq(api_key=GROQ_API_KEY, max_retries=0) if GROQ_API_KEY else None

    def _call_groq(self, messages: list, tools: list = None) -> object:
        """Appelle l'API Groq et retourne la réponse complète."""
        if not self.client:
            raise RuntimeError(
                "Clé API Groq non configurée. "
                "Ajoutez GROQ_API_KEY dans votre fichier .env ou app.yaml."
            )
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        try:
            return self.client.chat.completions.create(**kwargs)
        except RateLimitError:
            raise RuntimeError(
                "⏳ Limite de requêtes Groq atteinte (429). "
                "Patientez quelques secondes puis réessayez. "
                "Si le problème persiste, contactez l'administrateur pour upgrader le plan Groq."
            )
        except APIStatusError as e:
            raise RuntimeError(f"Erreur API Groq ({e.status_code}) : {e.message}")
        except Exception as e:
            raise RuntimeError(f"Erreur API Groq : {e}")

    def _get_final_response(self, messages: list) -> str:
        """
        Appelle Groq SANS tools pour forcer une réponse textuelle.
        Nécessaire car Groq retourne parfois content=None après des tool_calls.
        """
        response = self._call_groq(messages, tools=None)
        return (response.choices[0].message.content or "").strip()

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

                response = self._call_groq(messages, tools=TOOLS_DEFINITIONS)
                choice = response.choices[0]
                message = choice.message
                finish_reason = choice.finish_reason

                if generation:
                    try:
                        generation.end(
                            output=message.content,
                            usage=getattr(response, "usage", None)
                        )
                    except Exception:
                        pass

                if finish_reason == "tool_calls" and message.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })

                    for tc in message.tool_calls:
                        tool_name = tc.function.name
                        try:
                            tool_args = json.loads(tc.function.arguments)
                        except Exception:
                            tool_args = {}

                        logger.info(f"Outil appelé : {tool_name} avec args : {tool_args}")

                        if lf and trace:
                            try:
                                span = trace.span(name=f"tool-{tool_name}", input=tool_args)
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
                            "tool_call_id": tc.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })

                else:
                    final_response = (message.content or "").strip()

                    # Groq retourne parfois content=None après des tool_calls.
                    # On relance sans tools pour forcer une réponse textuelle.
                    if not final_response and tool_calls_log:
                        logger.info("Contenu vide après tool_calls, relance sans tools.")
                        final_response = self._get_final_response(messages)

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

        except RateLimitError:
            msg = ("⏳ Limite de requêtes Groq atteinte (429). "
                   "Patientez quelques secondes puis réessayez.")
            logger.warning("Groq 429 Rate Limit dans run()")
            return {
                "response": msg,
                "tool_calls_log": tool_calls_log,
                "elapsed_seconds": round(time.time() - start_time, 2),
                "model": self.model,
                "error": "rate_limit"
            }
        except RuntimeError as e:
            logger.error(f"Erreur agent : {e}")
            return {
                "response": str(e),
                "tool_calls_log": tool_calls_log,
                "elapsed_seconds": round(time.time() - start_time, 2),
                "model": self.model,
                "error": "groq_error"
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
        Format : data: <json>\\n\\n
        Types d'événements : tool_start, tool_end, token, done, error

        Les phases de tool_calls utilisent l'API non-streaming (nécessaire pour récupérer
        les tool_call_id). La réponse finale est streamée token par token.
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

                response = self._call_groq(messages, tools=TOOLS_DEFINITIONS)
                choice = response.choices[0]
                message = choice.message
                finish_reason = choice.finish_reason

                if finish_reason == "tool_calls" and message.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })

                    for tc in message.tool_calls:
                        tool_name = tc.function.name
                        try:
                            tool_args = json.loads(tc.function.arguments)
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
                            "tool_call_id": tc.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })

                else:
                    # Réponse finale — on envoie le contenu déjà reçu
                    final_response = (message.content or "").strip()

                    # Groq retourne parfois content=None après des tool_calls.
                    # On relance sans tools pour forcer une réponse textuelle.
                    if not final_response and tool_calls_log:
                        logger.info("Contenu vide après tool_calls, relance sans tools.")
                        final_response = self._get_final_response(messages)

                    if final_response:
                        yield sse("token", {"content": final_response})
                    yield sse("done", {"tool_calls_log": tool_calls_log})
                    return

        except RuntimeError as e:
            msg = str(e)
            logger.warning(f"Erreur agent (stream) : {msg}")
            yield sse("error", {"message": msg})
        except RateLimitError:
            msg = ("⏳ Limite de requêtes Groq atteinte. "
                   "Patientez quelques secondes puis réessayez.")
            logger.warning("Groq 429 Rate Limit dans stream()")
            yield sse("error", {"message": msg})
        except Exception as e:
            logger.exception(f"Erreur inattendue stream agent : {e}")
            yield sse("error", {"message": f"Erreur inattendue : {str(e)}"})


def _summarize_tool_result(tool_name: str, result: dict) -> str:
    """Génère un résumé court d'un résultat d'outil pour l'affichage SSE."""
    if "erreur" in result:
        return f"Erreur : {result['erreur']}"
    if tool_name == "pappers_rechercher_entreprise":
        return f"{result.get('total', 0)} entreprise(s) trouvée(s)"
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
