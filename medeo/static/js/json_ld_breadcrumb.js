// Breadcrumbs JSON-LD dynamiques
function generateBreadcrumbs() {
    const currentPath = window.location.pathname;
    const pathSegments = currentPath.split('/').filter(segment => segment);
    
    let breadcrumbs = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Accueil",
            "item": "https://www.medeo-partners.com/fr/accueil"
        }
    ];
    
    let currentUrl = "https://www.medeo-partners.com";
    let position = 2;
    
    // Mapping des segments vers des noms lisibles
    const segmentNames = {
        'fr': 'Français',
        'en': 'English',
        'accueil': 'Accueil',
        'home': 'Home',
        'votre_cabinet': 'Votre Cabinet',
        'your_firm': 'Your Firm',
        'notre_expertise': 'Notre Expertise',
        'our_expertise': 'Our Expertise',
        'expertise_comptable': 'Expertise Comptable',
        'accounting': 'Accounting',
        'audit': 'Audit',
        'auditing': 'Auditing',
        'conseil_optimisation': 'Conseil et Optimisation',
        'council_optimization': 'Council and Optimization',
        'actualites': 'Actualités',
        'news': 'News',
        'nouscontacter': 'Nous Contacter',
        'contactus': 'Contact Us',
        'espace_clients': 'Espace Clients',
        'account': 'Client Area',
        'blog': 'Blog',
        'article': 'Article',
        'categorie': 'Catégorie',
        'category': 'Category'
    };
    
    for (let i = 0; i < pathSegments.length; i++) {
        const segment = pathSegments[i];
        currentUrl += '/' + segment;
        
        // Ignorer les segments de langue pour les breadcrumbs
        if (segment === 'fr' || segment === 'en') {
            continue;
        }
        
        // Gérer les articles de blog
        if (segment === 'article' && pathSegments[i + 1]) {
            const articleSlug = pathSegments[i + 1];
            breadcrumbs.push({
                "@type": "ListItem",
                "position": position,
                "name": "Blog",
                "item": currentUrl.replace('/article/' + articleSlug, '/blog')
            });
            position++;
            
            breadcrumbs.push({
                "@type": "ListItem",
                "position": position,
                "name": "Article",
                "item": currentUrl
            });
            break;
        }
        
        // Gérer les catégories de blog
        if (segment === 'categorie' && pathSegments[i + 1]) {
            const categorySlug = pathSegments[i + 1];
            breadcrumbs.push({
                "@type": "ListItem",
                "position": position,
                "name": "Blog",
                "item": currentUrl.replace('/categorie/' + categorySlug, '/blog')
            });
            position++;
            
            breadcrumbs.push({
                "@type": "ListItem",
                "position": position,
                "name": "Catégorie",
                "item": currentUrl
            });
            break;
        }
        
        const name = segmentNames[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
        
        breadcrumbs.push({
            "@type": "ListItem",
            "position": position,
            "name": name,
            "item": currentUrl
        });
        
        position++;
    }
    
    const breadcrumbSchema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumbs
    };
    
    // Ajouter le script JSON-LD au head
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(breadcrumbSchema);
    document.head.appendChild(script);
}

// Exécuter au chargement de la page
document.addEventListener('DOMContentLoaded', generateBreadcrumbs);
