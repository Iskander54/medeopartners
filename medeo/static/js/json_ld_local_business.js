document.addEventListener("DOMContentLoaded", function() {
    var json_ld_local_business = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Medeo Partners - Cabinet d'Expertise Comptable à Paris",
        "url": "https://www.medeo-partners.com",
        "logo": "https://www.medeo-partners.com/path-to-logo.jpg",
        "image": "https://www.medeo-partners.com/path-to-image.jpg",
        "description": "Découvrez comment Medeo Partners, avec plus de 10 ans d'expertise en comptabilité et fiscalité, optimise la gestion financière et fiscale de votre société.",
        "telephone": "+33183641604",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "97 boulevard de Malesherbes",
            "addressLocality": "Paris",
            "addressRegion": "Île-de-France",
            "postalCode": "75008",
            "addressCountry": "FR"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "48.870816",
            "longitude": "2.304779"
        },
        "sameAs": [
            "https://www.linkedin.com/company/medeo-partners/",
            "https://instagram.com/medeo_partners"
        ],
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                ],
                "opens": "09:00",
                "closes": "18:00"
            }
        ]
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(json_ld_local_business);
    document.head.appendChild(script);
});
