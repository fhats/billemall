$ = jQuery

$ ->
  $("#bill-amount-total").keyup (event_object) ->
    split_currency_field(event_object.target.value, 'bill-share-field')

split_currency_field = (src_text, target_class) ->
  fields = $("." + target_class)

  values = split_currency_string(src_text, fields.length)
  currency_strings = (cents_to_dollar_str(v) for v in values)

  for field, i in fields
    fields[i].value = currency_strings[i]
