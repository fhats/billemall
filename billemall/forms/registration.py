import wtforms.fields
import wtforms.form
import wtforms.validators

class RegistrationForm(wtforms.form.Form):
    name = wtforms.fields.TextField(
        "Name",
        [
            wtforms.validators.Required(),
            wtforms.validators.Length(min=1, max=32, message="Please enter a name between 1 and 32 characters.")
        ])

    email = wtforms.fields.TextField(
        "Email Address",
        [
            wtforms.validators.Required(),
            wtforms.validators.Email("You must enter a valid email address!")
        ])

    password = wtforms.fields.PasswordField(
        "Password",
        [
            wtforms.validators.Required()
        ])
