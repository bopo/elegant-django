(function ($) {

    // Register callbacks to perform after inline has been added
    Elegant.after_inline = function () {
        var functions = {};
        var register = function (fn_name, fn_callback) {
            functions[fn_name] = fn_callback;
        };

        var run = function (inline_prefix, row) {
            for (var fn_name in functions) {
                functions[fn_name](inline_prefix, row);
            }
        };

        return {
            register: register,
            run: run
        };
    }();

    // Backwards compatiblity
    ElegantAfterInline = Elegant.after_inline;

    /**
     * Fixed submit buttons.
     */
    $.fn.elegant_fixed = function () {
        $(this).each(function () {
            // extra_offset: 70 (60 Footer height + 10 top offset)
            var $fixed_item = $(this), pos = $fixed_item.offset(), extra_offset = 70;
            $(window).bind('scroll.sl resize.sl load.sl', function (e) {
                var $win = $(this), scroll_top = $win.scrollTop();
                if ($fixed_item.height() < $win.height() &&
                    scroll_top > (pos.top - 10) &&
                    $fixed_item.height() < $win.height()) {
                    !$fixed_item.hasClass('fixed') && $fixed_item.addClass('fixed');
                    var max_top = Math.min(10, $(document).height() - $fixed_item.height() - scroll_top - extra_offset);
                    $fixed_item.css('top', max_top + 'px');
                } else if (scroll_top <= (pos.top - 10) &&
                    $fixed_item.hasClass('fixed')) {
                    $fixed_item.removeClass('fixed');
                }
            });

            $(window).trigger('scroll.sl');
        });
    };


    /**
     * Search filters - submit only changed fields
     */
    $.fn.elegant_search_filters = function () {
        $(this).change(function () {
            var $field = $(this);
            var $option = $field.find('option:selected');
            var select_name = $option.data('name');
            if (select_name) {
                $field.attr('name', select_name);
            } else {
                $field.removeAttr('name');
            }
            // Handle additional values for date filters
            var additional = $option.data('additional');
            if (additional) {
                var hidden_id = $field.data('name') + '_add';
                var $hidden = $('#' + hidden_id);
                if (!$hidden.length) {
                    $hidden = $('<input/>').attr('type', 'hidden').attr('id', hidden_id);
                    $field.after($hidden);
                }
                additional = additional.split('=');
                $hidden.attr('name', additional[0]).val(additional[1])
            }
        });
        $(this).trigger('change');
    };

    /**
     * Linked select - shows link to related item after Select
     */
    $.fn.elegant_linked_select = function () {

        var get_link_name = function ($select) {
            var text = $select.find('option:selected').text();
            return text && $select.val() ? text + '' : '';
        };

        var get_url = function ($add_link, $select) {
            var value = $select.val();
            return $add_link.attr('href').split('?')[0] + '../' + value + '/';
        };

        var add_link = function ($select) {
            var $add_link = $select.next();
            if ($add_link.hasClass('add-another')) {
                var $link = $add_link.next('a');
                if (!$link.length) {
                    $link = $('<a/>').addClass('linked-select-link');
                    $add_link.after($link).after(' &nbsp; ');
                }
                $link.text(get_link_name($select));
                $link.attr('href', get_url($add_link, $select));
            }
        };

        $(this).each(function () {
            add_link($(this));
        });

        $(document).on('change', this.selector, function () {
            add_link($(this));
        });
    };

    /**
     * Content tabs
     */
    $.fn.elegant_form_tabs = function () {

        var $tabs = $(this);
        var tab_prefix = $tabs.data('tab-prefix');
        if (!tab_prefix)
            return;

        var $tab_links = $tabs.find('a');

        function tab_contents($link) {
            return $('.' + tab_prefix + '-' + $link.attr('href').replace('#', ''));
        }

        function activate_tabs() {
            // Init tab by error, by url hash or init first tab
            if (window.location.hash) {
                var found_error;
                $tab_links.each(function () {
                    var $link = $(this);
                    if (tab_contents($link).find('.error').length != 0) {
                        $link.addClass('error');
                        $link.trigger('click');
                        found_error = true;
                    }
                });
                !found_error && $($tabs).find('a[href=\\' + window.location.hash + ']').click();
            } else {
                $tab_links.first().trigger('click');
            }
        }

        $tab_links.click(function () {
            var $link = $(this);
            $link.parent().parent().find('.active').removeClass('active');
            $link.parent().addClass('active');
            $('.' + tab_prefix).removeClass('show').addClass('hide');
            tab_contents($link).removeClass('hide').addClass('show')
        });

        activate_tabs();
    };

    /**
     * Avoids double-submit issues in the change_form.
     */
    $.fn.elegant_form_debounce = function () {
        var $form = $(this),
            $saveButtons = $form.find('.submit-row button'),
            submitting = false;

        $form.submit(function () {
            if (submitting) {
                return false;
            }

            submitting = true;
            $saveButtons.addClass('disabled');

            setTimeout(function () {
                $saveButtons.removeClass('disabled');
                submitting = false;
            }, 5000);
        });
    };

    $(function () {

        // Fixed submit buttons
        $('.inner-right-column').elegant_fixed();

        // Show link to related item after Select
        $('.linked-select').elegant_linked_select();

        // Handle change list filter null values
        $('.search-filter').elegant_search_filters();

        $('.object-tools>li>a').addClass('btn')

        // reversion
        $('#content-main>p').addClass('alert alert-info')
        $('div.module>p').addClass('alert alert-warn')

//        $('div.submit-row>input[type=submit]').addClass('btn btn-info')

        $('a.import_link').prepend('<i class="icon-upload"></i>&nbsp;')
        $('a.export_link').prepend('<i class="icon-download-alt"></i>&nbsp;')
        $('#content').css("cssText",'margin-left:0px!important;');

    });

}(Elegant.$));
