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

})