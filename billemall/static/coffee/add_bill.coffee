$ = jQuery

$ ->
  $("#bill-amount-total").keyup (event_object) ->
    split_currency_field(event_object.target.value, 'bill-share-field')

split_currency_field = (src_text, target_class) ->
  fields = $("." + target_class)
  target_value = parseInt(src_text, 10) / fields.length
  if isNaN(target_value)
    target_value = 0

  target_text = target_value.toString()

  items = target_text.split('.')

  # add another split item in case we don't have one
  items[items.length] = '00'

  # add a zero in case we don't have one
  items[1] = items[1] + '0'

  # now make the .00 part
  items[1] = items[1][0] + items[1][2]

  target_text = items[0] + '.' + items[1]

  for field in fields
    do (field) ->
      field.value = target_text
