from flask import render_template, request, Blueprint, g, current_app, abort, url_for, redirect, jsonify
from flask_babel import _
from medeo.models import BlogArticle, BlogCategory, BlogTag, KeywordResearch
from medeo import db
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
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    articles = BlogArticle.query.filter_by(status='published').order_by(
        BlogArticle.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Articles populaires
    popular_articles = BlogArticle.query.filter_by(status='published').order_by(
        BlogArticle.view_count.desc()
    ).limit(5).all()
    
    # Catégories principales
    categories = BlogCategory.query.filter_by(parent_id=None).all()
    
    return render_template('blog/index.html',
                         articles=articles,
                         popular_articles=popular_articles,
                         categories=categories,
                         title='Blog - Expertise Comptable et Fiscalité',
                         meta_description='Découvrez nos articles d\'expertise en comptabilité, fiscalité et conseil d\'entreprise. Actualités, guides pratiques et conseils d\'experts.')

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
    """Page d'article individuel avec optimisation SEO - Utilise des templates statiques comme les news"""
    # Mapping des slugs vers les templates
    article_templates = {
        'tva-obligations-declaratives-dirigeants': 'blog/articles/tva-obligations-declaratives-dirigeants.html',
        'creation-entreprise-erreurs-comptables-fiscales-premiere-annee': 'blog/articles/creation-entreprise-erreurs-comptables-fiscales-premiere-annee.html',
    }
    
    template_path = article_templates.get(slug)
    if not template_path:
        abort(404)
    
    return render_template(template_path)

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

@blog.route("/api/categories")
def api_categories():
    """API pour récupérer les catégories (pour le chatbot)"""
    categories = BlogCategory.query.all()
    
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description
    } for cat in categories]) 