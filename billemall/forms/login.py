import wtforms.fields
import wtforms.form
import wtforms.validators

class LoginForm(wtforms.form.Form):
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