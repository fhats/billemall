from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import transaction

from sqlalchemy.exc import DBAPIError

from .forms.login import LoginForm
from .forms.registration import RegistrationForm
from .models import DBSession, User

def dump_flashed_messages(request):
    msgs = []
    while request.session.peek_flash():
        msgs.append(request.session.pop_flash())

    return msgs

@view_config(route_name='home', renderer='login.jinja2')
def home(request):
    if 'user' in request.session:
        return HTTPFound(location='/overview')
    login_form = LoginForm(request.params)
    registration_form = RegistrationForm(request.params)
    return {
        "flashed_messages": dump_flashed_messages(request),
        "forms": {
            "login": login_form,
            "registration": registration_form
        }
    }

@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    if request.method == "POST" and 'user' not in request.session:
        # TODO(fhats): get sanitary
        incoming_email = request.params['email']
        incoming_password = request.params['password']

        login_form = LoginForm(request.params)
        if not login_form.validate():
            for field, error in login_form.errors.iteritems():
                request.session.flash("Invalid input for field %s: %s" % (field, error))
            return HTTPFound(location='/')

        proposed_user = DBSession.query(User).filter_by(email=incoming_email).first()
        if proposed_user.check_password(incoming_password):
            do_user_login(request, proposed_user)
            if 'redirect_url' in request.session:
                redirect_url = request.session['redirect_url']
            else:
                redirect_url = '/overview'
            request.session.flash("Hi!")
            return HTTPFound(location=redirect_url)
        else:
            request.session.flash("Incorrect email address/password combination.")
            return HTTPFound(location='/')
    else:
        return HTTPFound(location='/')

@view_config(route_name='logout')
def logout(request):
    request.session.invalidate()
    return HTTPFound(location='/')

@view_config(route_name='register')
def register(request):
    """Takes an HTTP POST and creates a user with the given information."""

    # Redirect to login/registration if this is not a POST
    if request.method == "POST":
        return HTTPFound(location="/")

    # TODO(fhats): Input validation
    user_name = request.params['name']
    user_email = request.params['email']
    user_password = request.params['password']

    registration_form = RegistrationForm(request.params)
    if not registration_form.validate():
        for field, error in registration_form.errors.iteritems():
            request.session.flash("Invalid input for field %s: %s" % (field, error))
        return HTTPFound(location='/')

    # Make sure a user with that email address doesn't already exist
    if DBSession.query(User).filter_by(email=user_email).count() > 0:
        request.session.flash("Someone has already registered using that email!")
        return HTTPFound(location='/')

    # Add the user
    with transaction.manager:
        new_user = User(user_name, user_email, user_password)
        DBSession.add(new_user)

    added_user = DBSession.query(User).filter_by(email=user_email).first()

    do_user_login(request, added_user)

    return HTTPFound(location='/overview')

def do_user_login(request, user):
    session = request.session
    session['user'] = user.as_dict()

@view_config(route_name='overview', renderer='overview.jinja2')
def overview(request):
    return {"status": "ok"}

@view_config(route_name='add_bill', renderer='add_bill.jinja2')
def add_bill(request):
    return {"status": "ok"}

@view_config(route_name='view_bill', renderer='view_bill.jinja2')
def view_bill(request):
    return {"status": "ok"}

@view_config(route_name='user_overview', renderer='user_overview.jinja2')
def user_overview(request):
    return {"status": "ok"}

@view_config(route_name='account', renderer='account.jinja2')
def account(request):
    return {"status": "ok"}
