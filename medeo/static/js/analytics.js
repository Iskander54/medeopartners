// Système de tracking analytics avancé pour Medeo Partners

class MedeoAnalytics {
    constructor() {
        this.events = [];
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
        this.init();
    }

    init() {
        this.trackPageView();
        this.trackUserBehavior();
        this.trackConversions();
        this.trackFormSubmissions();
        this.trackPhoneCalls();
        this.trackEmailClicks();
        this.trackSocialInteractions();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    trackEvent(eventName, eventData = {}) {
        const event = {
            event: eventName,
            timestamp: new Date().toISOString(),
            sessionId: this.sessionId,
            url: window.location.href,
            userAgent: navigator.userAgent,
            referrer: document.referrer,
            ...eventData
        };

        this.events.push(event);
        this.sendToAnalytics(event);
    }

    trackPageView() {
        this.trackEvent('page_view', {
            pageTitle: document.title,
            pagePath: window.location.pathname,
            pageUrl: window.location.href
        });
    }

    trackUserBehavior() {
        // Tracking du scroll
        let maxScroll = 0;
        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
                if (scrollPercent % 25 === 0) { // Track tous les 25%
                    this.trackEvent('scroll_depth', { depth: scrollPercent });
                }
            }
        });

        // Tracking du temps passé
        setInterval(() => {
            const timeSpent = Math.round((Date.now() - this.startTime) / 1000);
            if (timeSpent % 30 === 0) { // Track toutes les 30 secondes
                this.trackEvent('time_spent', { seconds: timeSpent });
            }
        }, 1000);

        // Tracking des clics sur les liens
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                this.trackEvent('link_click', {
                    linkText: e.target.textContent,
                    linkUrl: e.target.href,
                    linkType: this.getLinkType(e.target.href)
                });
            }
        });
    }

    trackConversions() {
        // Tracking des formulaires de contact
        const contactForms = document.querySelectorAll('form');
        contactForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.trackEvent('form_submit', {
                    formId: form.id || 'unknown',
                    formAction: form.action,
                    formMethod: form.method
                });
            });
        });

        // Tracking des CTA
        const ctaButtons = document.querySelectorAll('[data-cta]');
        ctaButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.trackEvent('cta_click', {
                    ctaType: button.dataset.cta,
                    ctaText: button.textContent,
                    ctaUrl: button.href || 'none'
                });
            });
        });
    }

    trackFormSubmissions() {
        // Tracking spécifique pour les formulaires de devis
        const quoteForms = document.querySelectorAll('.quote-form, [data-form-type="quote"]');
        quoteForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.trackEvent('quote_request', {
                    formType: 'quote',
                    source: window.location.pathname
                });
            });
        });

        // Tracking pour les formulaires de contact
        const contactForms = document.querySelectorAll('.contact-form, [data-form-type="contact"]');
        contactForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.trackEvent('contact_request', {
                    formType: 'contact',
                    source: window.location.pathname
                });
            });
        });
    }

    trackPhoneCalls() {
        // Tracking des clics sur les numéros de téléphone
        const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
        phoneLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                this.trackEvent('phone_call', {
                    phoneNumber: link.href.replace('tel:', ''),
                    source: window.location.pathname
                });
            });
        });
    }

    trackEmailClicks() {
        // Tracking des clics sur les emails
        const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
        emailLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                this.trackEvent('email_click', {
                    emailAddress: link.href.replace('mailto:', ''),
                    source: window.location.pathname
                });
            });
        });
    }

    trackSocialInteractions() {
        // Tracking des clics sur les réseaux sociaux
        const socialLinks = document.querySelectorAll('a[href*="linkedin"], a[href*="instagram"], a[href*="whatsapp"]');
        socialLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const platform = this.getSocialPlatform(link.href);
                this.trackEvent('social_click', {
                    platform: platform,
                    url: link.href,
                    source: window.location.pathname
                });
            });
        });
    }

    getLinkType(url) {
        if (url.includes('tel:')) return 'phone';
        if (url.includes('mailto:')) return 'email';
        if (url.includes('linkedin.com')) return 'social';
        if (url.includes('instagram.com')) return 'social';
        if (url.includes('whatsapp.com')) return 'social';
        if (url.startsWith('http') && !url.includes(window.location.hostname)) return 'external';
        return 'internal';
    }

    getSocialPlatform(url) {
        if (url.includes('linkedin.com')) return 'linkedin';
        if (url.includes('instagram.com')) return 'instagram';
        if (url.includes('whatsapp.com')) return 'whatsapp';
        return 'other';
    }

    sendToAnalytics(event) {
        // Envoi vers Google Analytics 4
        if (typeof gtag !== 'undefined') {
            gtag('event', event.event, {
                event_category: 'user_interaction',
                event_label: event.url,
                value: 1,
                custom_parameters: event
            });
        }

        // Envoi vers un endpoint personnalisé (optionnel)
        fetch('/api/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(event)
        }).catch(error => {
            console.log('Analytics tracking error:', error);
        });
    }

    // Méthodes utilitaires
    trackLeadGeneration(source, type) {
        this.trackEvent('lead_generated', {
            leadType: type,
            leadSource: source,
            timestamp: new Date().toISOString()
        });
    }

    trackServiceInterest(service) {
        this.trackEvent('service_interest', {
            service: service,
            source: window.location.pathname
        });
    }

    trackContentEngagement(contentType, contentId) {
        this.trackEvent('content_engagement', {
            contentType: contentType,
            contentId: contentId,
            source: window.location.pathname
        });
    }
}

// Initialisation du tracking
document.addEventListener('DOMContentLoaded', () => {
    window.medeoAnalytics = new MedeoAnalytics();
});

// Tracking des événements de conversion spécifiques
window.trackConversion = function(type, data = {}) {
    if (window.medeoAnalytics) {
        window.medeoAnalytics.trackEvent('conversion', {
            conversionType: type,
            ...data
        });
    }
}; 