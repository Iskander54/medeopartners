from flask import render_template, request, Blueprint, g, current_app, abort, url_for, redirect, jsonify
from flask_babel import _
from medeo.models import BlogArticle, BlogCategory, BlogTag, KeywordResearch
from medeo import db
from medeo.blog.blog_config import get_article_metadata, get_related_articles, get_category_info
from medeo.utils.indexnow import notify_indexnow
import json
from datetime import datetime
import re

blog = Blueprint('blog', __name__, url_prefix='/<lang_code>/blog')

@blog.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@blog.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')

@blog.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = current_app.url_map.bind('')
        try:
            endpoint, args = adapter.match('/en/blog' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)

@blog.route("/")
@blog.route("/index")
def index():
    """Page d'accueil du blog avec articles récents"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 12
        
        # Gestion d'erreur pour les requêtes DB
        try:
            articles = BlogArticle.query.filter_by(status='published').order_by(
                BlogArticle.published_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            current_app.logger.error(f"Erreur requête articles: {e}")
            articles = None
        
        # Articles populaires
        try:
            popular_articles = BlogArticle.query.filter_by(status='published').order_by(
                BlogArticle.view_count.desc()
            ).limit(5).all()
        except Exception as e:
            current_app.logger.error(f"Erreur requête articles populaires: {e}")
            popular_articles = []
        
        # Catégories principales
        try:
            categories = BlogCategory.query.filter_by(parent_id=None).all()
        except Exception as e:
            current_app.logger.error(f"Erreur requête catégories: {e}")
            categories = []
        
        return render_template('blog/index.html',
                             articles=articles,
                             popular_articles=popular_articles,
                             categories=categories,
                             title='Blog - Expertise Comptable et Fiscalité',
                             meta_description='Découvrez nos articles d\'expertise en comptabilité, fiscalité et conseil d\'entreprise. Actualités, guides pratiques et conseils d\'experts.')
    except Exception as e:
        current_app.logger.error(f"Erreur critique dans blog.index: {e}", exc_info=True)
        # Retourner une page d'erreur plutôt qu'une 500
        abort(500)

@blog.route("/categorie/<slug>")
def category(slug):
    """Page de catégorie avec articles filtrés"""
    category = BlogCategory.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    articles = BlogArticle.query.filter_by(
        category_id=category.id,
        status='published'
    ).order_by(BlogArticle.published_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('blog/category.html',
                         category=category,
                         articles=articles,
                         title=f'{category.name} - Blog Medeo Partners',
                         meta_description=category.meta_description or f'Articles sur {category.name}')

@blog.route("/article/<slug>")
def article(slug):
    """Page d'article individuel — DB en priorité, fallback sur templates statiques."""

    # Templates statiques legacy (3 articles HTML existants)
    STATIC_ARTICLE_TEMPLATES = {
        'tva-obligations-declaratives-dirigeants': 'blog/articles/tva-obligations-declaratives-dirigeants.html',
        'creation-entreprise-erreurs-comptables-fiscales-premiere-annee': 'blog/articles/creation-entreprise-erreurs-comptables-fiscales-premiere-annee.html',
        'loi-finances-2026-impact-entreprise': 'blog/articles/loi-finances-2026-impact-entreprise.html',
    }

    try:
        # 1. Chercher l'article en DB (published)
        db_article = BlogArticle.query.filter_by(slug=slug, status='published').first()

        if db_article:
            # Incrémenter le compteur de vues
            try:
                db_article.view_count = (db_article.view_count or 0) + 1
                from medeo import db as _db
                _db.session.commit()
            except Exception:
                pass

            # Notifier Bing/IndexNow si c'est la première vue (indexation fraîche)
            try:
                if db_article.view_count == 1:
                    article_url = f"https://www.medeo-partners.com{url_for('blog.article', slug=slug, lang_code='fr')}"
                    notify_indexnow(article_url)
            except Exception:
                pass

            # Articles liés (même catégorie, excl. article courant)
            try:
                related = BlogArticle.query.filter(
                    BlogArticle.category_id == db_article.category_id,
                    BlogArticle.id != db_article.id,
                    BlogArticle.status == 'published'
                ).order_by(BlogArticle.published_at.desc()).limit(3).all()
            except Exception:
                related = []

            return render_template('blog/article.html',
                                   article=db_article,
                                   related_articles=related,
                                   title=db_article.meta_title or db_article.title,
                                   meta_description=db_article.meta_description or db_article.excerpt)

        # 2. Fallback sur template statique
        template_path = STATIC_ARTICLE_TEMPLATES.get(slug)
        if template_path:
            try:
                metadata = get_article_metadata(slug)
            except Exception:
                metadata = {}
            try:
                related_articles = get_related_articles(slug)
            except Exception:
                related_articles = []
            return render_template(template_path,
                                   article_metadata=metadata,
                                   related_articles=related_articles)

        # 3. Introuvable
        current_app.logger.warning(f"Article non trouvé: {slug}")
        abort(404)

    except Exception as e:
        current_app.logger.error(f"Erreur lors du rendu de l'article {slug}: {e}", exc_info=True)
        abort(404)

@blog.route("/tag/<slug>")
def tag(slug):
    """Page de tag avec articles filtrés"""
    tag = BlogTag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    articles = tag.articles.filter_by(status='published').order_by(
        BlogArticle.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('blog/tag.html',
                         tag=tag,
                         articles=articles,
                         title=f'Articles taggés "{tag.name}" - Blog Medeo Partners')

@blog.route("/recherche")
def search():
    """Recherche d'articles"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    if query:
        articles = BlogArticle.query.filter(
            BlogArticle.status == 'published',
            (BlogArticle.title.contains(query) |
             BlogArticle.content.contains(query) |
             BlogArticle.excerpt.contains(query))
        ).order_by(BlogArticle.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        articles = None
    
    return render_template('blog/search.html',
                         articles=articles,
                         query=query,
                         title=f'Résultats de recherche pour "{query}" - Blog Medeo Partners')

@blog.route("/plan-du-site")
def sitemap():
    """Plan du site du blog"""
    categories = BlogCategory.query.all()
    articles = BlogArticle.query.filter_by(status='published').order_by(
        BlogArticle.published_at.desc()
    ).all()
    tags = BlogTag.query.all()
    
    return render_template('blog/sitemap.html',
                         categories=categories,
                         articles=articles,
                         tags=tags,
                         title='Plan du site - Blog Medeo Partners')

# API pour le chatbot
@blog.route("/api/articles")
def api_articles():
    """API pour récupérer les articles (pour le chatbot)"""
    try:
        articles = BlogArticle.query.filter_by(status='published').order_by(
            BlogArticle.published_at.desc()
        ).limit(10).all()
        return jsonify([{
            'id': article.id,
            'title': article.title,
            'excerpt': article.excerpt,
            'category': article.category.name,
            'url': url_for('blog.article', slug=article.slug, lang_code=g.lang_code),
            'published_at': article.published_at.isoformat() if article.published_at else None
        } for article in articles])
    except Exception as e:
        current_app.logger.warning(f"Blog api_articles DB error: {e}")
        return jsonify([]), 200

@blog.route("/api/categories")
def api_categories():
    """API pour récupérer les catégories (pour le chatbot)"""
    try:
        categories = BlogCategory.query.all()
        return jsonify([{
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'description': cat.description
        } for cat in categories])
    except Exception as e:
        current_app.logger.warning(f"Blog api_categories DB error: {e}")
        return jsonify([]), 200 