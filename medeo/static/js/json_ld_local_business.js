document.addEventListener("DOMContentLoaded", function() {
    var json_ld_local_business = {
        "@context": "https://schema.org",
        "@type": ["AccountingService", "LocalBusiness"],
        "name": "Medeo Partners",
        "legalName": "Medeo Partners",
        "url": "https://www.medeo-partners.com",
        "logo": {
            "@type": "ImageObject",
            "url": "https://www.medeo-partners.com/static/medeo_images/Medeo_partners_couleur.webp",
            "width": 200,
            "height": 176
        },
        "image": "https://www.medeo-partners.com/static/medeo_images/Medeo_partners_couleur.webp",
        "description": "Cabinet d'expertise comptable, d'audit et de commissariat aux comptes à Paris 8e. Membre de l'Ordre des Experts-Comptables et de la Compagnie Nationale des Commissaires aux Comptes.",
        "slogan": "Votre partenaire comptable et fiscal à Paris",
        "telephone": "+33183641604",
        "email": "contact@medeo-partners.com",
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
        "hasMap": "https://maps.google.com/?q=97+boulevard+de+Malesherbes+75008+Paris",
        "priceRange": "€€",
        "currenciesAccepted": "EUR",
        "paymentAccepted": "Virement bancaire, Chèque",
        "areaServed": [
            {
                "@type": "City",
                "name": "Paris"
            },
            {
                "@type": "AdministrativeArea",
                "name": "Île-de-France"
            }
        ],
        "knowsAbout": [
            "Expertise comptable",
            "Commissariat aux comptes",
            "Audit financier",
            "Optimisation fiscale",
            "Conseil en gestion d'entreprise",
            "Fiscalité des entreprises",
            "Comptabilité PME",
            "Holding patrimoniale"
        ],
        "memberOf": [
            {
                "@type": "Organization",
                "name": "Ordre des Experts-Comptables",
                "url": "https://www.oec.fr"
            },
            {
                "@type": "Organization",
                "name": "Compagnie Nationale des Commissaires aux Comptes",
                "url": "https://www.cncc.fr"
            }
        ],
        "sameAs": [
            "https://www.linkedin.com/company/medeo-partners/",
            "https://instagram.com/medeo_partners",
            "https://www.societe.com/societe/medeo-partners",
            "https://www.pages-jaunes.fr/",
            "https://www.oec.fr/trouver-un-expert-comptable"
        ],
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00",
                "closes": "18:00"
            }
        ],
        "founder": {
            "@type": "Person",
            "name": "Medeo Partners",
            "jobTitle": "Expert-Comptable & Commissaire aux Comptes"
        },
        "numberOfEmployees": {
            "@type": "QuantitativeValue",
            "minValue": 5,
            "maxValue": 20
        }
    };

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(json_ld_local_business);
    document.head.appendChild(script);
});
