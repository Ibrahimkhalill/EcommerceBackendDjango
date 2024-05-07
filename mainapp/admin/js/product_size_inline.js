(function($) {
    $(document).ready(function() {
        $('.inline-group').on('click', '.add-row', function() {
            var totalForms = $('#id_productimage_set-TOTAL_FORMS').val();
            var regex = /^(id_productimage_set-\d+-).+$/;
            var replacement = '$1size_quantity_';
            var newElement = $('#id_productimage_set-__prefix__-size_quantity').clone(true);
            newElement.attr('id', newElement.attr('id').replace(regex, replacement + totalForms));
            newElement.attr('name', newElement.attr('name').replace(regex, replacement + totalForms));
            newElement.find('input').val('');
            newElement.appendTo($(this).parent().prev());
            $('#id_productimage_set-TOTAL_FORMS').val(parseInt(totalForms) + 1);
        });
    });
})(django.jQuery);
