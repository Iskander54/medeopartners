# Ajouter dans .env ou app.yaml :
CHATBOT_PROVIDER=groq
GROQ_API_KEY=gsk_...

# Insérer les articles (une seule fois) :
cd /path/to/medeopartners
python scripts/insert_editorial_articles.py

# Mettre à jour les tables DB (nouvelles tables chatbot) :
python -c "from medeo import create_app, db; app = create_app(); app.app_context().__enter__(); db.create_all()"