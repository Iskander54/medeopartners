// Système de Lead Magnets pour Medeo Partners

class LeadMagnetSystem {
    constructor() {
        this.leadMagnets = [
            {
                id: 'guide-fiscal-2024',
                title: 'Guide Fiscal 2024',
                description: 'Téléchargez notre guide complet sur les nouveautés fiscales 2024',
                cta: 'Télécharger le guide',
                formFields: ['name', 'email', 'company'],
                trigger: 'scroll', // scroll, time, exit
                triggerValue: 70, // 70% de scroll
                active: false  // Désactivé temporairement
            },
            {
                id: 'audit-gratuit',
                title: 'Audit Gratuit de Votre Situation',
                description: 'Bénéficiez d\'un audit gratuit de votre situation comptable et fiscale',
                cta: 'Demander un audit',
                formFields: ['name', 'email', 'phone', 'company', 'message'],
                trigger: 'time',
                triggerValue: 30000, // 30 secondes
                active: true
            },
            {
                id: 'newsletter',
                title: 'Newsletter Mensuelle',
                description: 'Recevez nos conseils d\'experts en comptabilité et fiscalité',
                cta: 'S\'abonner',
                formFields: ['name', 'email'],
                trigger: 'exit',
                triggerValue: null,
                active: false  // Désactivé temporairement
            }
        ];
        
        this.init();
    }

    init() {
        this.createLeadMagnetModal();
        this.setupTriggers();
        this.setupFormHandling();
    }

    createLeadMagnetModal() {
        const modalHTML = `
            <div id="lead-magnet-modal" class="fixed inset-0 z-50 hidden" style="overflow-y: auto; -webkit-overflow-scrolling: touch;">
                <div class="absolute inset-0 bg-black bg-opacity-50"></div>
                <div class="relative flex items-center justify-center min-h-screen p-4" style="min-height: 100vh; min-height: -webkit-fill-available;">
                    <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative" style="max-height: 90vh; overflow-y: auto; margin: auto;">
                        <button id="close-lead-magnet" class="absolute top-3 right-3 text-gray-600 hover:text-gray-900 z-20 p-1.5 rounded-full hover:bg-gray-200 transition-all duration-200" aria-label="Fermer" style="cursor: pointer; background-color: rgba(255, 255, 255, 0.9);">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="stroke-width: 2.5;">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                        
                        <div id="lead-magnet-content">
                            <!-- Contenu dynamique -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Fermeture du modal
        document.getElementById('close-lead-magnet').addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.hideModal();
        });
        
        document.getElementById('lead-magnet-modal').addEventListener('click', (e) => {
            if (e.target.id === 'lead-magnet-modal' || e.target.classList.contains('bg-black')) {
                this.hideModal();
            }
        });
    }

    setupTriggers() {
        this.leadMagnets.forEach(magnet => {
            if (!magnet.active) return;
            
            switch (magnet.trigger) {
                case 'scroll':
                    this.setupScrollTrigger(magnet);
                    break;
                case 'time':
                    this.setupTimeTrigger(magnet);
                    break;
                case 'exit':
                    this.setupExitTrigger(magnet);
                    break;
            }
        });
    }

    setupScrollTrigger(magnet) {
        let triggered = false;
        window.addEventListener('scroll', () => {
            if (triggered) return;
            
            const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
            if (scrollPercent >= magnet.triggerValue) {
                triggered = true;
                this.showLeadMagnet(magnet);
            }
        });
    }

    setupTimeTrigger(magnet) {
        setTimeout(() => {
            this.showLeadMagnet(magnet);
        }, magnet.triggerValue);
    }

    setupExitTrigger(magnet) {
        document.addEventListener('mouseleave', (e) => {
            if (e.clientY <= 0) {
                this.showLeadMagnet(magnet);
            }
        });
    }

    showLeadMagnet(magnet) {
        // Vérifier si l'utilisateur a déjà vu ce lead magnet
        if (this.hasSeenLeadMagnet(magnet.id)) return;
        
        const content = document.getElementById('lead-magnet-content');
        content.innerHTML = this.generateFormHTML(magnet);
        
        const modal = document.getElementById('lead-magnet-modal');
        modal.classList.remove('hidden');
        
        // Empêcher le scroll du body sans forcer le zoom
        const scrollY = window.scrollY;
        document.body.style.position = 'fixed';
        document.body.style.top = `-${scrollY}px`;
        document.body.style.width = '100%';
        document.body.style.overflow = 'hidden';
        
        // Stocker la position de scroll pour la restaurer
        modal.dataset.scrollY = scrollY;
        
        // Empêcher le zoom sur mobile en ajoutant une meta viewport dynamique
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
        }
        
        // Marquer comme vu
        this.markLeadMagnetAsSeen(magnet.id);
        
        // Tracking
        if (window.medeoAnalytics) {
            window.medeoAnalytics.trackEvent('lead_magnet_shown', {
                leadMagnetId: magnet.id,
                leadMagnetTitle: magnet.title
            });
        }
    }

    hideModal() {
        const modal = document.getElementById('lead-magnet-modal');
        modal.classList.add('hidden');
        
        // Restaurer le scroll du body
        const scrollY = modal.dataset.scrollY || 0;
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.style.overflow = '';
        
        // Restaurer la position de scroll
        window.scrollTo(0, parseInt(scrollY));
        
        // Restaurer le viewport pour permettre le zoom normal
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
        }
    }

    generateFormHTML(magnet) {
        let formHTML = `
            <div class="text-center mb-6">
                <h3 class="text-xl font-bold text-gray-900 mb-2">${magnet.title}</h3>
                <p class="text-gray-600">${magnet.description}</p>
            </div>
            
            <form id="lead-magnet-form" data-magnet-id="${magnet.id}">
        `;
        
        magnet.formFields.forEach(field => {
            formHTML += this.generateFieldHTML(field);
        });
        
        formHTML += `
                <button type="submit" class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200">
                    ${magnet.cta}
                </button>
            </form>
        `;
        
        return formHTML;
    }

    generateFieldHTML(field) {
        const fieldConfig = {
            name: { label: 'Nom', type: 'text', required: true },
            email: { label: 'Email', type: 'email', required: true },
            phone: { label: 'Téléphone', type: 'tel', required: false },
            company: { label: 'Entreprise', type: 'text', required: false },
            message: { label: 'Message', type: 'textarea', required: false }
        };
        
        const config = fieldConfig[field];
        if (!config) return '';
        
        const required = config.required ? 'required' : '';
        
        if (config.type === 'textarea') {
            return `
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">${config.label}</label>
                    <textarea name="${field}" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" rows="3" ${required}></textarea>
                </div>
            `;
        }
        
        return `
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">${config.label}</label>
                <input type="${config.type}" name="${field}" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" ${required}>
            </div>
        `;
    }

    setupFormHandling() {
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'lead-magnet-form') {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });
    }

    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        const magnetId = form.dataset.magnetId;
        
        try {
            const response = await fetch('/api/lead-magnet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    magnetId: magnetId,
                    ...data
                })
            });
            
            if (response.ok) {
                this.showSuccessMessage();
                
                // Tracking de conversion
                if (window.medeoAnalytics) {
                    window.medeoAnalytics.trackLeadGeneration('lead_magnet', magnetId);
                }
            } else {
                this.showErrorMessage();
            }
        } catch (error) {
            console.error('Lead magnet submission error:', error);
            this.showErrorMessage();
        }
    }

    showSuccessMessage() {
        const content = document.getElementById('lead-magnet-content');
        content.innerHTML = `
            <div class="text-center">
                <div class="text-green-500 text-6xl mb-4">✓</div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Merci !</h3>
                <p class="text-gray-600">Votre demande a été enregistrée. Nous vous contacterons rapidement.</p>
            </div>
        `;
        
        setTimeout(() => {
            this.hideModal();
        }, 3000);
    }

    showErrorMessage() {
        const content = document.getElementById('lead-magnet-content');
        content.innerHTML = `
            <div class="text-center">
                <div class="text-red-500 text-6xl mb-4">✗</div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Erreur</h3>
                <p class="text-gray-600">Une erreur s'est produite. Veuillez réessayer.</p>
                <button onclick="location.reload()" class="mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                    Réessayer
                </button>
            </div>
        `;
    }

    hasSeenLeadMagnet(magnetId) {
        return localStorage.getItem(`lead_magnet_${magnetId}`) === 'seen';
    }

    markLeadMagnetAsSeen(magnetId) {
        localStorage.setItem(`lead_magnet_${magnetId}`, 'seen');
    }
}

// Initialisation du système de lead magnets
document.addEventListener('DOMContentLoaded', () => {
    window.leadMagnetSystem = new LeadMagnetSystem();
}); 