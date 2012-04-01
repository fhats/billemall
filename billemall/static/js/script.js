(function() {
  var $, echo_field;

  $ = jQuery;

  $(function() {
    return $("#bill-amount-total").keyup(function(event_object) {
      return echo_field(event_object.target.value, 'bill-share-field');
    });
  });

  echo_field = function(src_text, target_class) {
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

}).call(this);
