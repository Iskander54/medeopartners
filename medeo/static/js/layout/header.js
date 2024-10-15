$(() => {

    // Toggle header background color and shadow on scroll
    $(window).scroll(() => {
        if ($(this).scrollTop() > 0) {
            $('#header').addClass('bg-white shadow-sm');
        } else {
            $('#header').removeClass('bg-white shadow-sm');
        }
    });

})