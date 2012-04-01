(function() {
  var $, split_currency_field;

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
    $('.add-to-bill-link').click(function(event_object) {
      var add_elem, elem, name, people;
      add_elem = event_object.target;
      name = add_elem.getAttribute('data-name');
      people = $('#people');
      if (people.children().length > 0) people.append(", ");
      people.append('<a class="person">' + name + '</a>');
      elem = $('#people').children().last();
      elem.click(function(event_object) {
        $(add_elem).show();
        return $(event_object.target).remove();
      });
      return $(add_elem).hide();
    });
    return $('#add-to-bill-field-button').click(function(event_object) {
      var elem, field, name;
      event_object.preventDefault();
      field = $('#person-field')[0];
      name = field.value;
      field.value = '';
      $('#people').append('<a class="person">' + name + ' </a>');
      elem = $('#people').children().last();
      return elem.click(function(event_object) {
        return $(event_object.target).remove();
      });
    });
  });

}).call(this);
