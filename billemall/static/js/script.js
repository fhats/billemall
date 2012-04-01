(function() {
  var $, cents_to_dollar_str, currency_string_to_cents, split_currency_string, update_currency_fields, update_people;

  $ = jQuery;

  $(function() {
    $("#bill-amount-total").keyup(function(event) {
      return update_currency_fields();
    });
    $(".bill-primary-link").click(function(event) {
      $(".bill-primary").removeClass('bill-primary');
      return $(event.target).addClass('bill-primary');
    });
    return update_currency_fields();
  });

  update_currency_fields = function() {
    var currency_strings, field, fields, i, name, name_child, people, row, v, values, _i, _len, _len2, _ref;
    if ($('#auto-split').length > 0 && $('#auto-split')[0].checked) {
      fields = $(".bill-share-field");
      values = split_currency_string($("#bill-amount-total")[0].value, fields.length);
      currency_strings = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = values.length; _i < _len; _i++) {
          v = values[_i];
          _results.push(cents_to_dollar_str(v));
        }
        return _results;
      })();
      for (i = 0, _len = fields.length; i < _len; i++) {
        field = fields[i];
        fields[i].value = currency_strings[i];
      }
      people = [];
      _ref = $(".add-bill-row");
      for (_i = 0, _len2 = _ref.length; _i < _len2; _i++) {
        row = _ref[_i];
        name_child = $(row.children[0]).children('.name');
        name = $.trim(name_child[0].textContent);
        field = $(row.children[1]).children('.bill-share-field')[0];
        people.push({
          'name': name,
          'amount': currency_string_to_cents(field.value)
        });
      }
      $("#add-person-people")[0].value = window.JSON.stringify(people);
      return $("#people")[0].value = window.JSON.stringify(people);
    }
  };

  $ = jQuery;

  $(function() {
    $('.add-to-bill-link').click(function(event) {
      var add_elem, elem, name;
      add_elem = event.target;
      name = add_elem.getAttribute('data-name');
      $("#people-container").append('<a class="bill-person">' + name + ' </a>');
      elem = $('#people-container').children().last();
      elem.click(function(event) {
        $(add_elem).show();
        return $(event.target).remove();
      });
      $(add_elem).hide();
      return update_people();
    });
    $('#add-to-bill-field-button').click(function(event) {
      var elem, field, name;
      event.preventDefault();
      field = $('#person-field')[0];
      name = field.value;
      field.value = '';
      $('#people-container').append('<a class="bill-person">' + name + ' </a>');
      elem = $('#people-container').children().last();
      elem.click(function(event) {
        return $(event.target).remove();
      });
      return update_people();
    });
    return $("#amount-field").keyup(function(event) {
      return update_people();
    });
  });

  update_people = function() {
    var amounts, dollar_str, i, people, people_elems, person, _len;
    people_elems = $(".bill-person");
    if (people_elems.length < 1) return;
    people = [];
    dollar_str = $("#amount-field")[0].value;
    amounts = split_currency_string(dollar_str, people_elems.length);
    for (i = 0, _len = people_elems.length; i < _len; i++) {
      person = people_elems[i];
      people.push({
        'name': $.trim(person.textContent),
        'amount': amounts[i]
      });
    }
    return $("#people")[0].value = window.JSON.stringify(people);
  };

  split_currency_string = function(currency_string, num_fields) {
    var diff, target_value, total, values, _, _ref;
    total = currency_string_to_cents(currency_string);
    target_value = total / num_fields;
    diff = target_value - Math.floor(target_value);
    target_value -= diff;
    if (isNaN(target_value)) target_value = 0;
    values = [];
    for (_ = 0, _ref = num_fields - 1; 0 <= _ref ? _ < _ref : _ > _ref; 0 <= _ref ? _++ : _--) {
      values.push(target_value);
      total -= target_value;
    }
    values.push(total);
    return values;
  };

  currency_string_to_cents = function(currency_string) {
    return parseFloat(currency_string, 10) * 100;
  };

  cents_to_dollar_str = function(cents) {
    var all, cents_str, dollars_str;
    dollars_str = Math.floor(cents / 100).toString();
    cents_str = Math.floor(cents % 100).toString();
    while (cents_str.length < 2) {
      cents_str += '0';
    }
    all = dollars_str + '.' + cents_str.split('.')[0];
    return all;
  };

}).call(this);
