$(() => {

    // Toggle header background color and shadow on scroll
    handleHeaderScroll = () => {
        if ($(this).scrollTop() > 0) {
            $('#header').addClass('bg-white shadow-sm');
        } else {
            $('#header').removeClass('bg-white shadow-sm');
        }
    }
    handleHeaderScroll();
    $(window).scroll(handleHeaderScroll);

    let listenMenu = (idAction, idMenu, setXY = true) => {
        $('#' + idAction).on('click', function() {
            let menu = $('#' + idMenu);
            menu.toggleClass('hidden');
            // Set X and Y position of dropdown menu
            menu = $('#' + idMenu + ' > div');
            menu.on('click', function(e) {
                e.stopPropagation();
            });
            if (setXY) {
                let rect = this.getBoundingClientRect();
                menu.css('top', (rect.bottom + 8) + 'px');
                menu.css('left', rect.left + 'px');
            }
        });

        $('#' + idMenu).on('click', function(e) {
            $('#' + idMenu).addClass('hidden');
        });
    }

    listenMenu('expertise_dropdown', 'expertise_dropdown_menu');
    listenMenu('mobile_menu', 'mobile_menu_dropdown', false);

    $('#close_mobile_menu').on('click', function() {
        $('#mobile_menu_dropdown').addClass('hidden');
    });

})