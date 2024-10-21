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

    $('#expertise_dropdown').on('click', function() {
        let menu = $('#expertise_dropdown_menu');
        menu.toggleClass('hidden');
        // Set X and Y position of dropdown menu
        menu = $('#expertise_dropdown_menu > div');
        let rect = this.getBoundingClientRect();
        menu.css('top', (rect.bottom + 8) + 'px');
        menu.css('left', rect.left + 'px');
    });

    $('#expertise_dropdown_menu').on('click', function(e) {
        $('#expertise_dropdown_menu').addClass('hidden');
        e.stopPropagation();
    });

})