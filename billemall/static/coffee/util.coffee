float_to_currency_string = (target_value) ->
  target_text = target_value.toString()

  items = target_text.split('.')

  # add another split item in case we don't have one
  items[items.length] = '00'

  # add a zero in case we don't have one
  items[1] = items[1] + '0'

  # now make the .00 part
  items[1] = items[1][0] + items[1][2]

  # return 00.00
  items[0] + '.' + items[1]

split_currency_string = (currency_string, num_fields) ->
  target_value = parseInt(currency_string, 10) / num_fields

  if isNaN(target_value)
    target_value = 0

  strings = []

  for _ in [0...num_fields]
    strings.push(float_to_currency_string(target_value))

  # return list of strings
  strings
