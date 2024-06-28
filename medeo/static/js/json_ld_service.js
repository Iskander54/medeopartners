document.addEventListener("DOMContentLoaded", function() {
    var jsonld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Expertise Comptable",
        "description": "Services complets d'expertise comptable pour les entreprises de toutes tailles.",
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
