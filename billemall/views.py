from collections import defaultdict, OrderedDict
import json
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import transaction

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

        added_user = DBSession.query(User).filter_by(email=user_email).first()

        do_user_login(request, added_user)

        return HTTPFound(location='/overview')
    else:
        return registration_context(request)

def do_user_login(request, user):
    session = request.session
    session['user'] = user.as_dict()

@view_config(route_name='overview', renderer='overview.jinja2')
def overview(request):
    """Shows the overview for the logged-in user."""
    if 'user' not in request.session:
        return HTTPFound(location="/")

    # this queries is so awesome
    # first get all the bills we are on
    user_bills = DBSession.query(Bill).\
        join(BillShare).\
        join(BillShareUserPlaceholder).\
        filter_by(claimed_user_id=request.session['user']['id']).\
        all()

    # now get all the users we have any association with
    # a dicts containing a user id and a cumulative amount owed
    # NOTE: We aggregate based on name for unclaimed placeholders
    # this is prone to name collisions
    # + = this user is getting money
    # - = this user owes money
    users = defaultdict(int)
    for bill in user_bills:
        bill_shares = DBSession.query(BillShare).\
            join(Bill).\
            filter(Bill.id == bill.id).\
            all()
        
        for share in bill_shares:
            if share.billshare_user_placeholder.claimed_user_id == request.session['user']['id']:
                continue
            
            if bill.primary_user_id == request.session['user']['id']:
                users[share.billshare_user_placeholder.name] += share.amount
            else:
                users[share.billshare_user_placeholder.name] -= share.amount

    return {
        "users": dict(users)
    }

@view_config(route_name='add_bill', renderer='add_bill.jinja2')
def add_bill(request):
    if 'user' not in request.session:
        return HTTPFound(location="/")

    if request.method == "POST":
        # We expect the request body to just be a list of {name:person, amount:xxx}
        try:
            request_body = json.loads(request.params['people'])
        except (KeyError, ValueError):
            return HTTPBadRequest("Poorly formatted request")
        
        if not isinstance(request_body, list):
            return HTTPBadRequest("Expected type list")
        
        primary_name = request.params['name']

        bill_total = sum([entry['amount'] for entry in request_body])

        primary_placeholder = None
        user_placeholder = None # placeholder of the logged in user

        # Create the Bill
        # This shit is all done in a single transaction in order to have nice ROLLBACK
        # semantics if any one of these transactions fails.
        with transaction.manager:
            placeholders = []
            for entry in request_body:
                name = entry['name']
                amount = entry['amount']
                # Create a placeholder for the BillShares of this bill

                # TODO(fhats): Change this to add users if they exist and are in a mapping
                # of allowed users for this user to bill
                placeholder = BillShareUserPlaceholder(name=name)
                DBSession.add(placeholder)
                # Note: we call encrypt() on this placeholder to generate an ID that can be passed
                # around and not easily guessed.
                DBSession.flush()
                DBSession.refresh(placeholder)
                placeholder.encrypt()
                DBSession.add(placeholder)

                placeholders.append({
                    "placeholder": placeholder,
                    "amount": amount
                })

                if name == primary_name:
                    primary_placeholder = placeholder

                if name == request.session['user']['name']:
                    user_placeholder = placeholder

            if not primary_placeholder:
                primary_placeholder = user_placeholder

            bill = Bill(primary_user_id=primary_placeholder, total=bill_total)
            DBSession.add(bill)

            DBSession.flush()
            DBSession.refresh(bill)

            for placeholder in placeholders:
                bill_share = BillShare(
                    billshare_user_placeholder_id=placeholder["placeholder"].id,
                    bill_id=bill.id,
                    amount=placeholder["amount"])
                DBSession.add(bill_share)

            bill_id = bill.id
        return HTTPFound(location="/bill/%d" % bill_id)
    else:
        return {}

@view_config(route_name='view_bill', renderer='view_bill.jinja2')
def view_bill(request):
    bill_id = int(request.matchdict['id'])
    # Redirect if not logged in
    if 'user' not in request.session:
        return HTTPFound(location='/')    

    bill = DBSession.query(Bill).filter_by(id=bill_id).first()

    # Find the billees on this bill
    billed_users = DBSession.query(BillShare).filter_by(bill_id=bill_id).all()

    billees = []

    for billee in billed_users:
        b = {}
        b['name'] = billee.billshare_user_placeholder.name
        
        b['id'] = billee.billshare_user_placeholder.id
        
        b['amount'] = "%0.2f" % (billee.amount / 100)

        billees.append(b)

    total = bill.total

    primary = {
        'name': bill.primary_user.name,
        'id': bill.primary_user.id
    }

    return {
        "billees": billees,
        "primary": primary,
        "total": "%0.2f" % (total / 100)
    }

@view_config(route_name='user_overview', renderer='user_overview.jinja2')
def user_overview(request):


    return {"status": "ok"}

@view_config(route_name='account', renderer='account.jinja2')
def account(request):
    return {"status": "ok"}
