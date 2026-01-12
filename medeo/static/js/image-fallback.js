// Détection du support WebP et fallback automatique pour les images
(function() {
    'use strict';
    
    // Fonction pour détecter le support WebP
    function supportsWebP() {
        return new Promise(function(resolve) {
            const webP = new Image();
            webP.onload = webP.onerror = function() {
                resolve(webP.height === 2);
            };
            webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
        });
    }
    
    // Fonction pour remplacer les images WebP par des fallbacks si nécessaire
    function replaceWebPImages() {
        const images = document.querySelectorAll('img[src*=".webp"]');
        
        images.forEach(function(img) {
            const src = img.src;
            if (src.includes('.webp')) {
                // Créer une image de test pour vérifier si le WebP se charge
                const testImg = new Image();
                testImg.onerror = function() {
                    // Si le WebP ne se charge pas, utiliser le fallback JPEG
                    const fallbackSrc = src.replace('.webp', '.jpg')
                                          .replace('.webp', '.jpeg')
                                          .replace('images/', 'images/');
                    
                    // Essayer plusieurs variantes de fallback
                    const fallbacks = [
                        src.replace('.webp', '.jpg'),
                        src.replace('.webp', '.jpeg'),
                        src.replace('woman_phone.webp', 'woman_home.jpg'),
                        src.replace('main-img.webp', 'main-img.jpeg'),
                        src.replace('eiffel_tower.webp', 'news/juridique/eiffel_tower.jpeg')
                    ];
                    
                    // Tester chaque fallback
                    let fallbackIndex = 0;
                    function tryFallback() {
                        if (fallbackIndex < fallbacks.length) {
                            const fallbackImg = new Image();
                            fallbackImg.onload = function() {
                                img.src = fallbacks[fallbackIndex];
                                img.onerror = null; // Éviter les boucles infinies
                            };
                            fallbackImg.onerror = function() {
                                fallbackIndex++;
                                tryFallback();
                            };
                            fallbackImg.src = fallbacks[fallbackIndex];
                        }
                    }
                    tryFallback();
                };
                testImg.src = src;
            }
        });
    }
    
    // Exécuter au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            supportsWebP().then(function(webPSupported) {
                if (!webPSupported) {
                    replaceWebPImages();
                }
            });
        });
    } else {
        supportsWebP().then(function(webPSupported) {
            if (!webPSupported) {
                replaceWebPImages();
            }
        });
    }
    
    // Observer les nouvelles images ajoutées dynamiquement
    if ('MutationObserver' in window) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'IMG' && node.src && node.src.includes('.webp')) {
                            const testImg = new Image();
                            testImg.onerror = function() {
                                node.src = node.src.replace('.webp', '.jpg').replace('.webp', '.jpeg');
                            };
                            testImg.src = node.src;
                        }
                        // Vérifier aussi les images dans les nœuds enfants
                        const webpImages = node.querySelectorAll && node.querySelectorAll('img[src*=".webp"]');
                        if (webpImages && webpImages.length > 0) {
                            webpImages.forEach(function(img) {
                                const testImg = new Image();
                                testImg.onerror = function() {
                                    img.src = img.src.replace('.webp', '.jpg').replace('.webp', '.jpeg');
                                };
                                testImg.src = img.src;
                            });
                        }
                    }
                });
            });
        });
        
        // Attendre que le body soit disponible avant d'observer
        function startObserving() {
            if (document.body && document.body instanceof Node) {
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            } else {
                // Si le body n'existe pas encore, attendre le chargement du DOM
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', startObserving);
                } else {
                    // Si le DOM est déjà chargé mais le body n'existe toujours pas, réessayer après un court délai
                    setTimeout(startObserving, 100);
                }
            }
        }
        
        startObserving();
    }
})();

