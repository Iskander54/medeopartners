document.addEventListener("DOMContentLoaded", function() {
    var jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Accueil",
                "item": "https://www.medeo-partners.com/fr/accueil"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Votre Cabinet",
                "item": "https://www.medeo-partners.com/fr/votre_cabinet"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": "Notre Expertise",
                "item": "https://www.medeo-partners.com/fr/notre_expertise"
            },
            {
                "@type": "ListItem",
                "position": 4,
                "name": "Expertise Comptable",
                "item": "https://www.medeo-partners.com/fr/expertise_comptable"
            },
            {
                "@type": "ListItem",
                "position": 5,
                "name": "Audit",
                "item": "https://www.medeo-partners.com/fr/audit"
            },
            {
                "@type": "ListItem",
                "position": 6,
                "name": "Conseil et Optimisation",
                "item": "https://www.medeo-partners.com/fr/conseil_optimisation"
            },
            {
                "@type": "ListItem",
                "position": 7,
                "name": "Actualités",
                "item": "https://www.medeo-partners.com/fr/actualites"
            },
            {
                "@type": "ListItem",
                "position": 8,
                "name": "Nous Contacter",
                "item": "https://www.medeo-partners.com/fr/nouscontacter"
            }
        ]
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(jsonld);
    document.head.appendChild(script);
});
