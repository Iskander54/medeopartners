document.addEventListener("DOMContentLoaded", function() {
    var jsonld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Audit Financier",
        "description": "Audit financier détaillé pour assurer la conformité et l'optimisation des processus financiers.",
        "provider": {
            "@type": "Organization",
            "name": "Medeo Partners",
            "url": "https://www.medeopartners.com"
        }
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(jsonld);
    document.head.appendChild(script);
});
