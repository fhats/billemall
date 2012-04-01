$ = jQuery

$ ->
  $("#bill-amount-total").keyup (event) ->
    update_currency_fields()

  $(".bill-primary-link").click (event) ->
    $(".bill-primary").removeClass('bill-primary')
    $(event.target).addClass('bill-primary')

  update_currency_fields()


update_currency_fields = () ->
  if $('#auto-split')[0].checked
    fields = $(".bill-share-field")

    values = split_currency_string($("#bill-amount-total")[0].value, fields.length)
    currency_strings = (cents_to_dollar_str(v) for v in values)

    for field, i in fields
      fields[i].value = currency_strings[i]
