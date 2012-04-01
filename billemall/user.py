from collections import defaultdict
import json
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import transaction

from sqlalchemy import and_, or_
from sqlalchemy.exc import DBAPIError

from .forms.login import LoginForm
from .forms.registration import RegistrationForm
from .models import DBSession, Bill, BillShare, BillShareUserPlaceholder, User

def login_context(request):
    login_form = LoginForm(request.params)
    return {
        "flashed_messages": request.session.pop_flash(),
        "forms": {
            "login": login_form,
        }
    }


def registration_context(request):
    registration_form = RegistrationForm(request.params)
    return {
        "flashed_messages": request.session.pop_flash(),
        "forms": {
            "registration": registration_form
        }
    }


@view_config(route_name='home', renderer='index.jinja2')
def home(request):
    if 'user' in request.session:
        return HTTPFound(location='/overview')
    return login_context(request)

@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    if request.method == "POST" and 'user' not in request.session:
        # TODO(fhats): get sanitary
        incoming_email = request.params['email']
        incoming_password = request.params['password']

        login_form = LoginForm(request.params)
        if not login_form.validate():
            for field, errors in login_form.errors.iteritems():
                for error in errors:
                    request.session.flash("%s: %s" % (field, error))
            return login_context(request)

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
            return login_context(request)
    else:
        return login_context(request)

@view_config(route_name='logout')
def logout(request):
    request.session.invalidate()
    return HTTPFound(location='/')

@view_config(route_name='register', renderer='register.jinja2')
def register(request):
    if request.method == "POST" and 'user' not in request.session:
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
            DBSession.flush()
            DBSession.refresh(new_user)

            new_user_placeholder = BillShareUserPlaceholder(new_user)
            DBSession.add(new_user_placeholder)

            do_user_login(request, new_user, new_user_placeholder)

        return HTTPFound(location='/overview')
    else:
        return registration_context(request)

def do_user_login(request, user, placeholder=None):
    if not placeholder:
        placeholder = DBSession.query(BillShareUserPlaceholder).filter_by(claimed_user_id=user.id).first()
    session = request.session
    session['user'] = user.as_dict()
    session['placeholder'] = placeholder.id
