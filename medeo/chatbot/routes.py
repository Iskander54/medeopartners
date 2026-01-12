from flask import render_template, request, Blueprint, g, current_app, jsonify, redirect, url_for, abort, session
from flask_babel import _
import openai
import json
import os
from datetime import datetime
import requests

chatbot = Blueprint('chatbot', __name__, url_prefix='/<lang_code>/chatbot')

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
        except:
            abort(404)

class FiscalChatbot:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
        self.conversation_history = []
        
    def get_knowledge_base(self):
        """Base de connaissances fiscales et comptables"""
        return """
        Tu es un expert-comptable senior et assistant fiscal hautement qualifié pour le cabinet Medeo Partners, 
        un cabinet d'expertise comptable situé au 97 Boulevard Malesherbes, 75008 Paris.
        
        DOMAINES D'EXPERTISE PROFONDE :
        - Comptabilité générale et plan comptable français (PCG) : écritures comptables, balance, grand livre, 
          comptes annuels (bilan, compte de résultat, annexe), normes comptables françaises
        - Fiscalité des entreprises : TVA (régimes, déclarations, déductibilité), Impôt sur les Sociétés (IS), 
          CVAE (Cotisation sur la Valeur Ajoutée des Entreprises), CFE (Cotisation Foncière des Entreprises), 
          optimisation fiscale légale, crédits d'impôt
        - Fiscalité des particuliers : Impôt sur le Revenu (IR), Impôt sur la Fortune Immobilière (IFI), 
          LMNP (Loueur Meublé Non Professionnel), défiscalisation, Pinel, Malraux
        - Droit social et paie : DSN (Déclaration Sociale Nominative), cotisations sociales, bulletins de paie, 
          conventions collectives, droit du travail appliqué à la comptabilité
        - Audit et contrôle : audit légal, commissariat aux comptes, contrôle interne, conformité réglementaire
        - Droit des sociétés : création d'entreprise, statuts, assemblées générales, fusions, scissions, 
          transformations, cessions d'entreprises
        - Comptabilité internationale : IFRS (International Financial Reporting Standards), consolidation
        - Gestion de patrimoine et conseil en investissement pour les entreprises
        
        RÈGLES PROFESSIONNELLES STRICTES :
        - Tu es un expert-comptable diplômé avec une expérience approfondie
        - Donne des conseils généraux et pédagogiques, mais toujours précis et factuels
        - Précise systématiquement que pour un conseil personnalisé adapté à la situation spécifique du client, 
          il faut consulter un expert-comptable en rendez-vous
        - Cite toujours les sources officielles (BOFIP, Légifrance, Code de commerce, Code général des impôts)
        - Reste factuel, précis et à jour avec la réglementation française en vigueur
        - Utilise un ton professionnel, expert mais accessible et pédagogique
        - Si la question nécessite une analyse approfondie de la situation du client, oriente vers un rendez-vous
        
        SOURCES OFFICIELLES DE RÉFÉRENCE :
        - BOFIP (Bulletin Officiel des Finances Publiques) - source officielle de la fiscalité française
        - Légifrance - portail officiel du droit français
        - Code général des impôts (CGI)
        - Code de commerce
        - Plan comptable général (PCG)
        - Instructions fiscales et administratives de la DGFiP
        
        CONTEXTE DU CABINET :
        Medeo Partners est un cabinet d'expertise comptable situé à Paris (97 Boulevard Malesherbes, 75008).
        Le cabinet offre des services d'expertise comptable, d'audit, de conseil fiscal et de gestion d'entreprise.
        Pour un accompagnement personnalisé, les clients peuvent contacter le cabinet au 01 83 64 16 04 
        ou via le formulaire de contact sur le site web.
        """
    
    def get_relevant_articles(self, query):
        """Récupère les articles pertinents du blog"""
        try:
            # Appel à l'API du blog pour récupérer les articles
            response = requests.get(f"{request.url_root}api/articles")
            if response.status_code == 200:
                articles = response.json()
                
                # Recherche simple par mots-clés
                relevant_articles = []
                query_words = query.lower().split()
                
                for article in articles:
                    title_words = article['title'].lower().split()
                    excerpt_words = article['excerpt'].lower().split()
                    
                    # Calcul de pertinence basique
                    relevance = 0
                    for word in query_words:
                        if word in title_words:
                            relevance += 3
                        if word in excerpt_words:
                            relevance += 1
                    
                    if relevance > 0:
                        relevant_articles.append({
                            'title': article['title'],
                            'excerpt': article['excerpt'],
                            'url': article['url'],
                            'relevance': relevance
                        })
                
                # Trier par pertinence
                relevant_articles.sort(key=lambda x: x['relevance'], reverse=True)
                return relevant_articles[:3]  # Top 3
                
        except Exception as e:
            print(f"Erreur récupération articles : {e}")
        
        return []
    
    def generate_response(self, user_message, conversation_id=None):
        """Génère une réponse avec OpenAI"""
        
        # Récupérer les articles pertinents
        relevant_articles = self.get_relevant_articles(user_message)
        
        # Construire le contexte de conversation
        conversation_context = ""
        if self.conversation_history:
            conversation_context = "\n\nHISTORIQUE DE LA CONVERSATION RÉCENTE :\n"
            for i, conv in enumerate(self.conversation_history[-5:], 1):
                conversation_context += f"Q{i}: {conv.get('user', '')}\n"
                conversation_context += f"R{i}: {conv.get('assistant', '')}\n\n"
        
        # Construire le contexte des articles
        articles_context = ""
        if relevant_articles:
            articles_context = "\n\nARTICLES PERTINENTS DU BLOG MEDEO PARTNERS :\n"
            for article in relevant_articles:
                articles_context += f"- {article['title']} : {article['excerpt']}\n"
            articles_context += "\nSi ces articles sont pertinents pour répondre à la question, mentionne-les dans ta réponse avec leur titre.\n"
        
        # Construire le prompt utilisateur
        prompt = f"""
        QUESTION DE L'UTILISATEUR : {user_message}
        
        {conversation_context}
        {articles_context}
        
        INSTRUCTIONS POUR TA RÉPONSE :
        1. Réponds en tant qu'expert-comptable senior avec précision et professionnalisme
        2. Si des articles du blog Medeo Partners sont pertinents, mentionne-les avec leur titre
        3. Précise toujours que pour un conseil personnalisé adapté à sa situation spécifique, l'utilisateur doit consulter un expert-comptable en rendez-vous
        4. Cite les sources officielles (BOFIP, Légifrance, Code général des impôts) quand c'est pertinent
        5. Reste factuel, précis et à jour avec la réglementation française en vigueur
        6. Utilise un ton professionnel, expert mais accessible et pédagogique
        7. Si la question nécessite une analyse approfondie de la situation du client, oriente vers un rendez-vous avec le cabinet
        8. Réponds en français de manière claire et structurée
        
        RÉPONSE (sois concis mais complet, maximum 500 mots) :
        """
        
        if not self.client:
            return {
                'response': "L'assistant fiscal n'est pas disponible pour le moment. Veuillez nous contacter directement pour vos questions.",
                'relevant_articles': relevant_articles,
                'conversation_id': conversation_id
            }
            
        try:
            # Utiliser la base de connaissances comme message système
            system_message = self.get_knowledge_base()
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Ajouter à l'historique
            self.conversation_history.append({
                'user': user_message,
                'assistant': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Limiter l'historique
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return {
                'response': ai_response,
                'relevant_articles': relevant_articles,
                'conversation_id': conversation_id
            }
            
        except Exception as e:
            print(f"Erreur génération réponse : {e}")
            return {
                'response': "Désolé, je rencontre une difficulté technique. Veuillez réessayer ou nous contacter directement.",
                'relevant_articles': [],
                'conversation_id': conversation_id
            }

# Instance globale du chatbot
fiscal_chatbot = FiscalChatbot()

@chatbot.route("/")
def index():
    """Page principale du chatbot"""
    # Initialiser le compteur si nécessaire
    if 'chatbot_question_count' not in session:
        session['chatbot_question_count'] = 0
    
    questions_remaining = 3 - session.get('chatbot_question_count', 0)
    
    return render_template('chatbot/index.html',
                         title='Assistant Fiscal - Medeo Partners',
                         meta_description='Posez vos questions fiscales et comptables à notre assistant expert. Conseils gratuits et personnalisés.',
                         questions_remaining=questions_remaining,
                         contact_phone='01 83 64 16 04',
                         contact_email='contact@medeo-partners.com')

@chatbot.route("/api/chat", methods=['POST'])
def chat():
    """API pour le chat avec limite de 3 questions par session"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Initialiser le compteur de questions dans la session si nécessaire
        if 'chatbot_question_count' not in session:
            session['chatbot_question_count'] = 0
        
        # Vérifier si l'utilisateur a déjà posé 3 questions
        if session['chatbot_question_count'] >= 3:
            return jsonify({
                'response': '',
                'limit_reached': True,
                'message': (
                    "Merci pour vos questions ! Vous avez atteint la limite de 3 questions gratuites. "
                    "Pour obtenir des conseils personnalisés et approfondis adaptés à votre situation, "
                    "nous vous invitons à contacter directement notre cabinet d'expertise comptable."
                ),
                'contact_info': {
                    'phone': '01 83 64 16 04',
                    'email': 'contact@medeo-partners.com',
                    'address': '97 Boulevard Malesherbes, 75008 Paris',
                    'contact_url': url_for('main.nouscontacter', lang_code=g.lang_code)
                },
                'relevant_articles': [],
                'conversation_id': conversation_id,
                'questions_remaining': 0
            })
        
        # Incrémenter le compteur de questions
        session['chatbot_question_count'] += 1
        questions_remaining = 3 - session['chatbot_question_count']
        
        # Générer la réponse
        result = fiscal_chatbot.generate_response(user_message, conversation_id)
        
        # Ajouter les informations sur le nombre de questions restantes
        result['questions_remaining'] = questions_remaining
        result['limit_reached'] = False
        
        # Si c'est la dernière question, ajouter un message d'avertissement
        if questions_remaining == 0:
            result['warning_message'] = (
                "C'était votre dernière question gratuite. Pour des conseils personnalisés, "
                "contactez-nous au 01 83 64 16 04 ou via notre formulaire de contact."
            )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Erreur chat API : {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@chatbot.route("/api/reset", methods=['POST'])
def reset_chat():
    """API pour réinitialiser le compteur de questions (pour tests ou nouvelle session)"""
    session.pop('chatbot_question_count', None)
    return jsonify({'success': True, 'message': 'Compteur réinitialisé'})

@chatbot.route("/api/faq")
def faq():
    """API pour les questions fréquentes"""
    faqs = [
        {
            'question': 'Comment calculer ma TVA ?',
            'answer': 'Le calcul de la TVA dépend de votre régime fiscal et du taux applicable. Consultez notre guide sur la TVA pour plus de détails.'
        },
        {
            'question': 'Quels sont les seuils de TVA en 2024 ?',
            'answer': 'Les seuils de TVA en 2024 sont : 85 800€ pour les prestations de services et 34 400€ pour les ventes de biens.'
        },
        {
            'question': 'Comment optimiser fiscalement mon entreprise ?',
            'answer': 'L\'optimisation fiscale doit respecter la légalité. Consultez un expert comptable pour un conseil personnalisé.'
        },
        {
            'question': 'Quelles sont les obligations comptables d\'une SARL ?',
            'answer': 'Une SARL doit tenir une comptabilité régulière, établir des comptes annuels et les déposer au greffe.'
        },
        {
            'question': 'Comment déclarer mes impôts en ligne ?',
            'answer': 'La déclaration en ligne se fait sur impots.gouv.fr. Consultez notre guide pour les étapes détaillées.'
        }
    ]
    
    return jsonify({'faqs': faqs})

@chatbot.route("/api/categories")
def categories():
    """API pour les catégories de questions"""
    categories = [
        {
            'id': 'comptabilite',
            'name': 'Comptabilité Générale',
            'description': 'Plan comptable, écritures, bilan, compte de résultat'
        },
        {
            'id': 'fiscalite-entreprise',
            'name': 'Fiscalité des Entreprises',
            'description': 'TVA, IS, CVAE, CFE, optimisation fiscale'
        },
        {
            'id': 'fiscalite-particulier',
            'name': 'Fiscalité des Particuliers',
            'description': 'IR, IFI, LMNP, défiscalisation'
        },
        {
            'id': 'social',
            'name': 'Social et Paie',
            'description': 'DSN, cotisations, bulletins de paie'
        },
        {
            'id': 'audit',
            'name': 'Audit et Contrôle',
            'description': 'Audit légal, CAC, conformité'
        },
        {
            'id': 'droit-societes',
            'name': 'Droit des Sociétés',
            'description': 'Statuts, fusion, transformation'
        }
    ]
    
    return jsonify({'categories': categories}) 