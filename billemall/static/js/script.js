(function() {
  var $, float_to_currency_string, split_currency_field, split_currency_string, update_people;

  $ = jQuery;

  $(function() {
    return $("#bill-amount-total").keyup(function(event_object) {
      return split_currency_field(event_object.target.value, 'bill-share-field');
    });
  });

  split_currency_field = function(src_text, target_class) {
    var currency_strings, field, fields, i, _len, _results;
    fields = $("." + target_class);
    currency_strings = split_currency_strings(src_text, fields.length);
    _results = [];
    for (i = 0, _len = fields.length; i < _len; i++) {
      field = fields[i];
      _results.push(fields[i].value = currency_strings[i]);
    }
    return _results;
  };

  $ = jQuery;

  $(function() {
    $('.add-to-bill-link').click(function(event) {
      var add_elem, elem, name;
      add_elem = event.target;
      name = add_elem.getAttribute('data-name');
      $("#people").append('<a class="bill-person">' + name + ' </a>');
      elem = $('#people').children().last();
      elem.click(function(event) {
        $(add_elem).show();
        return $(event.target).remove();
      });
      $(add_elem).hide();
      return update_people();
    });
    return $('#add-to-bill-field-button').click(function(event) {
      var elem, field, name;
      event.preventDefault();
      field = $('#person-field')[0];
      name = field.value;
      field.value = '';
      $('#people').append('<a class="bill-person">' + name + ' </a>');
      elem = $('#people').children().last();
      elem.click(function(event) {
        return $(event.target).remove();
      });
      return update_people();
    });
  });

  update_people = function() {
    var amounts, i, people, people_elems, person, _len;
    people_elems = $(".bill-person");
    people = [];
    amounts = split_currency_string($("#amount-field")[0].value, people_elems.length);
    for (i = 0, _len = people_elems.length; i < _len; i++) {
      person = people_elems[i];
      people.push({
        'name': person.textContent.substring(0, person.textContent.length - 1),
        'amount': amounts[i]
      });
    }
    console.log(people);
    console.log(window.JSON.stringify(people));
    console.log($("#sneaky-people")[0].value);
    return $("#sneaky-people")[0].value = window.JSON.stringify(people);
  };

  float_to_currency_string = function(target_value) {
    var items, target_text;
    target_text = target_value.toString();
    items = target_text.split('.');
    items[items.length] = '00';
    items[1] = items[1] + '0';
    items[1] = items[1][0] + items[1][2];
    return items[0] + '.' + items[1];
  };

  split_currency_string = function(currency_string, num_fields) {
    var strings, target_value, _;
    target_value = parseInt(currency_string, 10) / num_fields;
    if (isNaN(target_value)) target_value = 0;
    strings = [];
    for (_ = 0; 0 <= num_fields ? _ < num_fields : _ > num_fields; 0 <= num_fields ? _++ : _--) {
      strings.push(float_to_currency_string(target_value));
    }
    return strings;
  };

}).call(this);
