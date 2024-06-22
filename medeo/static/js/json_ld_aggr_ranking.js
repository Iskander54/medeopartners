document.addEventListener("DOMContentLoaded", function() {
    var jsonld = {
        "@context": "https://schema.org",
        "@type": "AggregateRating",
        "ratingValue": "4.9",
        "reviewCount": "24",
        "bestRating": "5",
        "worstRating": "1"
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(jsonld);
    document.head.appendChild(script);
});
