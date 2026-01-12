from datetime import datetime
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from medeo import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    dob = db.Column(db.DateTime, unique=True, nullable=False)
    addresses = db.relationship('Address', backref='account', lazy=True)
    taxreturns = db.relationship('Taxreturn', backref='user',lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    line1 = db.Column(db.String(120), unique=True, nullable=False)
    line2 = db.Column(db.String(120), unique=True, nullable=False)
    zip = db.Column(db.String(6), unique=True, nullable=False)
    city = db.Column(db.String(30), unique=True, nullable=False)
    state = db.Column(db.String(30), unique=True, nullable=False)

class Taxreturn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=False,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    taxdocs = db.relationship('Taxdoc', backref='taxreturn',lazy=True)


class Taxdoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    path = db.Column(db.String(50), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=False,nullable=False)
    taxreturn_id = db.Column(db.Integer, db.ForeignKey('taxreturn.id'),nullable=False)

# ===== NOUVEAUX MODÈLES POUR LE BLOG =====

class BlogCategory(db.Model):
    """Catégories principales du blog (silos SEO)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'))
    seo_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    children = db.relationship('BlogCategory', backref=db.backref('parent', remote_side=[id]))
    articles = db.relationship('BlogArticle', backref='category', lazy=True)

class BlogArticle(db.Model):
    """Articles du blog avec optimisation SEO"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255))
    alt_image = db.Column(db.String(255))
    
    # SEO
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    focus_keyword = db.Column(db.String(100))
    secondary_keywords = db.Column(db.Text)  # JSON array
    
    # Statut et dates
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    category_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('BlogTag', secondary='article_tags', backref='articles')
    
    # Analytics
    view_count = db.Column(db.Integer, default=0)
    reading_time = db.Column(db.Integer)  # en minutes

class BlogTag(db.Model):
    """Tags pour les articles"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

# Table de liaison pour les tags
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('blog_article.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('blog_tag.id'), primary_key=True)
)

class KeywordResearch(db.Model):
    """Recherche de mots-clés et leur performance"""
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    search_volume = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)  # 1-100
    cpc = db.Column(db.Float)  # Cost per click
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance tracking
    current_position = db.Column(db.Integer)
    target_position = db.Column(db.Integer)
    last_checked = db.Column(db.DateTime)

class ContentCalendar(db.Model):
    """Calendrier éditorial"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_brief = db.Column(db.Text)
    target_keywords = db.Column(db.Text)  # JSON array
    category_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'))
    planned_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, published
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
