/**
 * Created by msg on 3/29/17.
 */

function reset_bottom(el, bottom_height) {
    console.info("start reset");
    var div_el = $(el);
    div_el.css("position", "fixed");
    var height = $(window).height();
    var width = $(window).width();
    div_el.css({
        'left': (width / 2 - div_el.width() / 2) + "px",
        'top': (height - div_el.height() - bottom_height) + 'px'
    });
}

function register_reset_bottom(el, bottom_height) {
    if (bottom_height == null) {
        bottom_height = 60;
    }
    reset_bottom(el, bottom_height);
    $(window).resize(function () {
        reset_bottom(el, bottom_height);
    });
    el.resize(function () {
        console.info("el resize");
        reset_bottom(el, bottom_height);
    });
}