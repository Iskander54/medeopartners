document.addEventListener("DOMContentLoaded", function() {
    var json_ld_local_business = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Medeo Partners - Cabinet d'Experts Comptables à Paris",
            "url": "https://www.medeopartners.com",
            "logo": "",
            "image": "",
            "description": "Découvrez comment Medeo Partners, avec plus de 10 ans d'expertise en comptabilité et fiscalité, optimise la gestion financière et fiscale de votre société.",
            "telephone": "+33123456789",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "07 boulevard de Malesharbes",
                "addressLocality": "Paris",
                "addressRegion": "Île-de-France",
                "postalCode": "75009",
                "addressCountry": "FR"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "48.870816",
                "longitude": "2.304779"
            },
            "sameAs": [
                "https://www.facebook.com/medeopartners",
                "https://www.linkedin.com/company/medeopartners"
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
            }

            var script = document.createElement('script');
                script.type = 'application/ld+json';
                script.text = JSON.stringify(json_ld_local_business);
                document.head.appendChild(script);
            });
