# Architecture du Chatbot Expert-Comptable

## Vue d'ensemble

Le chatbot expert-comptable est un assistant intelligent qui répond aux questions sur la comptabilité, la fiscalité et la gestion d'entreprise. Il utilise OpenAI GPT-4 pour générer des réponses expertes et limite les utilisateurs à 3 questions gratuites avant de les rediriger vers le formulaire de contact.

## Architecture Technique

### 1. Backend (Flask)

**Fichier principal :** `medeo/chatbot/routes.py`

#### Composants principaux :

- **Blueprint Flask** : `/<lang_code>/chatbot`
  - Route principale : `/` - Page d'interface du chatbot
  - API `/api/chat` - Endpoint pour les messages
  - API `/api/faq` - Questions fréquentes
  - API `/api/categories` - Catégories de questions
  - API `/api/reset` - Réinitialisation du compteur (pour tests)

#### Classe `FiscalChatbot` :

- **Initialisation** : Configure le client OpenAI avec la clé API depuis les variables d'environnement
- **Base de connaissances** : Prompt système détaillé avec expertise comptable/fiscale
- **Génération de réponses** : Utilise GPT-4 avec contexte enrichi

#### Gestion de session Flask :

- **Compteur de questions** : Stocké dans `session['chatbot_question_count']`
- **Limite** : Maximum 3 questions par session
- **Après 3 questions** : Retourne un message avec informations de contact

### 2. Frontend (HTML/JavaScript)

**Fichier :** `medeo/templates/chatbot/index.html`

#### Fonctionnalités :

- **Interface de chat** : Zone de messages avec historique
- **Compteur visuel** : Affiche le nombre de questions restantes (X/3)
- **Gestion de la limite** :
  - Désactive le formulaire après 3 questions
  - Affiche un message de contact avec numéro de téléphone
  - Affiche un avertissement à la dernière question
- **Intégration FAQ et catégories** : Sidebar avec suggestions

### 3. Configuration OpenAI

- **Modèle** : GPT-4
- **Max tokens** : 1000
- **Temperature** : 0.7 (équilibre créativité/précision)
- **Prompt système** : Base de connaissances expert-comptable détaillée

## Flux d'utilisation

1. **Utilisateur arrive sur la page** :
   - Compteur initialisé à 3 questions
   - Message de bienvenue affiché

2. **Utilisateur pose une question** :
   - Question envoyée à `/api/chat`
   - Compteur décrémenté dans la session
   - Réponse générée par GPT-4
   - Compteur mis à jour dans l'interface

3. **Après 3 questions** :
   - Formulaire désactivé
   - Message de contact affiché avec :
     - Numéro de téléphone : **01 83 64 16 04**
     - Email : contact@medeo-partners.com
     - Adresse : 97 Boulevard Malesherbes, 75008 Paris
     - Lien vers le formulaire de contact

## Base de connaissances

Le prompt système inclut :

- **Domaines d'expertise** :
  - Comptabilité générale (PCG)
  - Fiscalité entreprises (TVA, IS, CVAE, CFE)
  - Fiscalité particuliers (IR, IFI, LMNP)
  - Droit social et paie
  - Audit et contrôle
  - Droit des sociétés
  - Comptabilité internationale (IFRS)

- **Règles professionnelles** :
  - Conseils généraux uniquement
  - Orientation vers consultation personnalisée
  - Citations de sources officielles
  - Ton professionnel et pédagogique

- **Sources officielles** :
  - BOFIP
  - Légifrance
  - Code général des impôts
  - Code de commerce
  - Plan comptable général

## Variables d'environnement requises

```bash
OPENAI_API_KEY=votre_clé_api_openai
```

## Améliorations futures possibles

1. **Gestion de conversation persistante** : Stocker l'historique en base de données
2. **Analytics** : Tracker les questions les plus fréquentes
3. **Personnalisation** : Adapter les réponses selon le type d'entreprise
4. **Multilingue** : Support anglais complet
5. **Intégration calendrier** : Permettre de prendre rendez-vous directement

## Tests

Pour tester le chatbot :

1. Lancer l'application Flask
2. Accéder à `/fr/chatbot/`
3. Poser 3 questions
4. Vérifier que le formulaire se désactive et affiche les informations de contact

Pour réinitialiser le compteur (tests) :
```bash
POST /fr/chatbot/api/reset
```

## Notes importantes

- Le compteur est basé sur les sessions Flask (cookies)
- Chaque nouvelle session repart à 3 questions
- Le chatbot oriente toujours vers une consultation personnalisée pour les cas complexes
- Les réponses sont limitées à 1000 tokens pour contrôler les coûts

