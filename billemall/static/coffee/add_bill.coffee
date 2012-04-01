$ = jQuery

$ ->
  $("#bill-amount-total").keyup (event_object) ->
    split_currency_field(event_object.target.value, 'bill-share-field')

split_currency_field = (src_text, target_class) ->
  fields = $("." + target_class)

  currency_strings = split_currency_strings(src_text, fields.length)

  for field, i in fields
    fields[i].value = currency_strings[i]
