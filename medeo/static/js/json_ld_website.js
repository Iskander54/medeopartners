document.addEventListener("DOMContentLoaded", function() {
    var jsonld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Medeo Partners",
        "url": "https://www.medeo-partners.com",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://www.medeo-partners.com/search?query={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(jsonld);
    document.head.appendChild(script);
});
