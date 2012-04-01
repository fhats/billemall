$ = jQuery

$ ->
  $('.add-to-bill-link').click (event) ->
    add_elem = event.target
    name = add_elem.getAttribute('data-name')

    $("#people").append('<a class="bill-person">' + name + ' </a>')
    elem = $('#people').children().last()

    elem.click (event) ->
      $(add_elem).show()
      $(event.target).remove()

    $(add_elem).hide()

    update_people()

  $('#add-to-bill-field-button').click (event) ->
    event.preventDefault()
    field = $('#person-field')[0]
    name = field.value
    field.value = ''

    $('#people').append('<a class="bill-person">' + name + ' </a>')
    elem = $('#people').children().last()

    elem.click (event) ->
      $(event.target).remove()

    update_people()

  $("#amount-field").keyup (event) ->
    update_people()

update_people = () ->
    people_elems = $(".bill-person")
    if people_elems.length < 1
      return

    people = []
    dollar_str = $("#amount-field")[0].value
    amounts = split_currency_string(dollar_str, people_elems.length)

    for person, i in people_elems
      people.push({
        'name': person.textContent.substring(0, person.textContent.length-1),
        'amount': amounts[i]
      })

    $("#sneaky-people")[0].value = window.JSON.stringify(people)
