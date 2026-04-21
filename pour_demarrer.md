# Ajouter dans .env ou app.yaml :
CHATBOT_PROVIDER=groq
GROQ_API_KEY=gsk_...         # Utilisé par le chatbot public ET l'agent Mesoutils

# Clés optionnelles :
PAPPERS_API_KEY=...           # Obligatoire pour les recherches entreprise dans Mesoutils
GROQ_MODEL=llama-3.3-70b-versatile  # Modèle par défaut (modifiable)

# Insérer les articles (une seule fois) :
cd /path/to/medeopartners
python scripts/insert_editorial_articles.py

# Mettre à jour les tables DB (nouvelles tables chatbot) :
python -c "from medeo import create_app, db; app = create_app(); app.app_context().__enter__(); db.create_all()"
