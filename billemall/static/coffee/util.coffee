split_currency_string = (currency_string, num_fields) ->
  total = currency_string_to_cents(currency_string)
  target_value = total / num_fields

  diff = target_value - Math.floor(target_value)
  target_value -= diff

  if isNaN(target_value)
    target_value = 0

  values = []
  for _ in [0...num_fields-1]
    values.push(target_value)
    total -= target_value

  values.push(total)

  values

currency_string_to_cents = (currency_string) ->
  parseFloat(currency_string, 10) * 100

cents_to_dollar_str = (cents) ->
  dollars_str = Math.floor(cents/100).toString()
  cents_str = Math.floor(cents % 100).toString()
  while cents_str.length < 2
    cents_str += '0'
  all = dollars_str + '.' + cents_str.split('.')[0]
  return all
