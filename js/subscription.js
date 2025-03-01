$(document).ready(function() {
    $(".plan-item").on({
        mouseenter: function(){
            $('.current-plan').removeClass('active')
        },
        mouseleave: function(){
            $('.current-plan').addClass('active')
        }
    });
})