"""
Service chatbot Groq — utilise l'API OpenAI-compatible de Groq.
Modèle par défaut : llama-3.3-70b-versatile
Gratuit jusqu'à ~14 400 req/jour sans carte bancaire.
Définir : GROQ_API_KEY, GROQ_CHAT_MODEL (optionnel)
"""
import os
from .base import BaseChatbotService, SYSTEM_PROMPT

GROQ_API_BASE = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqService(BaseChatbotService):
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.model = os.getenv('GROQ_CHAT_MODEL', DEFAULT_MODEL)
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=GROQ_API_BASE)
        return self._client

    def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            client = self._get_client()
            client.models.list()
            return True
        except Exception:
            return False

    def get_response(self, messages: list, articles_context: str = '') -> dict:
        """
        messages : liste de dicts {'role': 'user'|'assistant', 'content': str}
        articles_context : contexte des articles blog pertinents (str)
        Retourne un dict avec 'response', 'provider', 'model', tokens.
        """
        if not self.api_key:
            return self._unavailable()

        try:
            client = self._get_client()

            system_content = SYSTEM_PROMPT
            if articles_context:
                system_content += f"\n\nARTICLES PERTINENTS DU BLOG MEDEO PARTNERS :\n{articles_context}\n"
                system_content += "Si ces articles sont pertinents, mentionne-les dans ta réponse avec leur titre.\n"

            api_messages = [{"role": "system", "content": system_content}]
            api_messages += [{"role": m["role"], "content": m["content"]} for m in messages]

            completion = client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                max_tokens=1024,
                temperature=0.3,
            )

            response_text = completion.choices[0].message.content or ''
            usage = completion.usage

            return {
                'response': response_text,
                'provider': 'groq',
                'model': self.model,
                'prompt_tokens': usage.prompt_tokens if usage else 0,
                'completion_tokens': usage.completion_tokens if usage else 0,
            }

        except Exception as e:
            import logging
            logging.error(f"[GroqService] Erreur: {e}")
            return self._error(str(e))

    def _unavailable(self):
        return {
            'response': (
                "L'assistant fiscal n'est pas disponible (clé API manquante). "
                "Contactez-nous au 01 83 64 16 04."
            ),
            'provider': 'groq',
            'model': self.model,
            'prompt_tokens': 0,
            'completion_tokens': 0,
        }

    def _error(self, detail: str):
        return {
            'response': (
                "Désolé, je rencontre une difficulté technique. "
                "N'hésitez pas à nous contacter directement au **01 83 64 16 04** "
                "ou via notre [formulaire de contact](/fr/nouscontacter)."
            ),
            'provider': 'groq',
            'model': self.model,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'error': detail,
        }
