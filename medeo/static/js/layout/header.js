$(document).ready(function() {

    // Toggle header background color and shadow on scroll
    var handleHeaderScroll = function() {
        if ($(window).scrollTop() > 0) {
            $('#header').addClass('bg-white shadow-sm');
        } else {
            $('#header').removeClass('bg-white shadow-sm');
        }
    };
    handleHeaderScroll();
    $(window).scroll(handleHeaderScroll);

    var listenMenu = function(idAction, idMenu, setXY) {
        if (setXY === undefined) setXY = true;
        
        var actionElement = $('#' + idAction);
        var menuElement = $('#' + idMenu);
        
        // Vérifier que les éléments existent
        if (actionElement.length === 0 || menuElement.length === 0) {
            console.warn('Menu elements not found:', idAction, idMenu);
            return;
        }
        
        actionElement.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            var menu = $('#' + idMenu);
            var isHidden = menu.hasClass('hidden');
            menu.toggleClass('hidden');
            
            // Mettre à jour aria-expanded pour l'accessibilité
            if (idMenu === 'mobile_menu_dropdown') {
                var mobileMenuButton = $('#mobile_menu');
                if (mobileMenuButton.length > 0) {
                    mobileMenuButton.attr('aria-expanded', !isHidden);
                }
            }
            
            // Animation pour le menu mobile
            if (idMenu === 'mobile_menu_dropdown') {
                var menuVisible = $('#menu_visible');
                if (menuVisible.length > 0) {
                    menuVisible.removeClass('animate-slide-right');
                    // Forcer le reflow pour réinitialiser l'animation
                    void menuVisible[0].offsetWidth;
                    menuVisible.addClass('animate-slide-right');
                }
            }
            
            // Set X and Y position of dropdown menu
            var menuContent = $('#' + idMenu + ' > div');
            menuContent.on('click', function(e) {
                e.stopPropagation();
            });
            
            if (setXY && idMenu !== 'mobile_menu_dropdown') {
                var rect = this.getBoundingClientRect();
                menuContent.css('top', (rect.bottom + 8) + 'px');
                menuContent.css('left', rect.left + 'px');
            }
        });

        menuElement.on('click', function(e) {
            // Ne fermer que si on clique sur le backdrop, pas sur le contenu du menu
            if (e.target === this) {
                $('#' + idMenu).addClass('hidden');
                // Mettre à jour aria-expanded pour l'accessibilité
                if (idMenu === 'mobile_menu_dropdown') {
                    var mobileMenuButton = $('#mobile_menu');
                    if (mobileMenuButton.length > 0) {
                        mobileMenuButton.attr('aria-expanded', 'false');
                    }
                }
            }
        });
    };

    listenMenu('expertise_dropdown', 'expertise_dropdown_menu');
    listenMenu('mobile_menu', 'mobile_menu_dropdown', false);

    var closeMobileMenu = $('#close_mobile_menu');
    if (closeMobileMenu.length > 0) {
        closeMobileMenu.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $('#mobile_menu_dropdown').addClass('hidden');
            // Mettre à jour aria-expanded pour l'accessibilité
            var mobileMenuButton = $('#mobile_menu');
            if (mobileMenuButton.length > 0) {
                mobileMenuButton.attr('aria-expanded', 'false');
            }
        });
    }
    
    // Fermer le menu mobile quand on clique sur un lien
    $('#mobile_menu_dropdown a').on('click', function() {
        $('#mobile_menu_dropdown').addClass('hidden');
        // Mettre à jour aria-expanded pour l'accessibilité
        var mobileMenuButton = $('#mobile_menu');
        if (mobileMenuButton.length > 0) {
            mobileMenuButton.attr('aria-expanded', 'false');
        }
    });

});