"""
Factory de services chatbot.
Sélectionne le provider via la variable d'environnement CHATBOT_PROVIDER.
  - groq   → GroqService  (llama-3.3-70b, OpenAI-compatible, gratuit jusqu'à 14 400 req/jour)
  - openai → OpenAIService (gpt-4o-mini)
  - gemini → GeminiService (gemini-2.0-flash, futur)
Par défaut : groq si GROQ_API_KEY présente, sinon openai.
"""
import os


def get_chatbot_service():
    """Retourne une instance du service chatbot selon CHATBOT_PROVIDER."""
    provider = os.getenv('CHATBOT_PROVIDER', '').lower()

    if provider == 'groq' or (not provider and os.getenv('GROQ_API_KEY')):
        from .groq_service import GroqService
        return GroqService()

    if provider == 'openai' or os.getenv('OPENAI_API_KEY'):
        from .openai_service import OpenAIService
        return OpenAIService()

    # Aucune clé disponible — service no-op
    from .base import BaseChatbotService
    return BaseChatbotService()
