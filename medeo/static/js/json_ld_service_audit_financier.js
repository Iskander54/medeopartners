document.addEventListener("DOMContentLoaded", function() {
    var jsonld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Audit Financier",
        "description": "Audit financier détaillé pour assurer la conformité et l'optimisation des processus financiers de votre entreprise.",
        "provider": {
            "@type": "Organization",
            "name": "Medeo Partners",
            "url": "https://www.medeo-partners.com"
        }
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(jsonld);
    document.head.appendChild(script);
});
