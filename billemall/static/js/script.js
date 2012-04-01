(function() {
  var $, remove_from_bill, split_currency_field;

  $ = jQuery;

  $(function() {
    return $("#bill-amount-total").keyup(function(event_object) {
      return split_currency_field(event_object.target.value, 'bill-share-field');
    });
  });

  split_currency_field = function(src_text, target_class) {
    var field, fields, items, target_text, target_value, _i, _len, _results;
    fields = $("." + target_class);
    target_value = parseInt(src_text, 10) / fields.length;
    if (isNaN(target_value)) target_value = 0;
    target_text = target_value.toString();
    items = target_text.split('.');
    items[items.length] = '00';
    items[1] = items[1] + '0';
    items[1] = items[1][0] + items[1][2];
    target_text = items[0] + '.' + items[1];
    _results = [];
    for (_i = 0, _len = fields.length; _i < _len; _i++) {
      field = fields[_i];
      _results.push((function(field) {
        return field.value = target_text;
      })(field));
    }
    return _results;
  };

  $ = jQuery;

  $(function() {
    return $('.add-to-bill-link').click(function(event_object) {
      var add_elem, elem, name;
      add_elem = event_object.target;
      if (add_elem.getAttribute('data-can-add') !== "false") {
        name = add_elem.getAttribute('data-name');
        $('#people').append('<a class="person">' + name + ' </a>');
        elem = $('#people').children().last();
        elem.click(function(event_object) {
          $(add_elem).show();
          return $(event_object.target).remove();
        });
        return $(add_elem).hide();
      }
    });
  });

  remove_from_bill = function(event_object) {
    return event_object.target;
  };

}).call(this);
