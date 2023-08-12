$(function () {
    // Add AJAX loader
    $('.plugin-list .text').click(function () {
        const $target = $(this).parent().parent().parent().parent().children("div.plugin-editor");
        const $icon = $('<i/>').attr('id', 'elegant-loading-icon');
        $icon.css({'display': 'inline-block', 'top': -25, 'left': 15, 'position': 'absolute'});
        $target.prepend($icon);
    });
});
