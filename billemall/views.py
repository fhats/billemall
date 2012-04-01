from collections import defaultdict, OrderedDict
import json
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
import transaction

from sqlalchemy import and_, or_
from sqlalchemy.exc import DBAPIError

from .bill import cents_to_dollar_str
from .forms.login import LoginForm
from .forms.registration import RegistrationForm
from .models import DBSession, Bill, BillShare, BillShareUserPlaceholder, User

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
            
            if bill.primary_user.claimed_user_id == request.session['user']['id']:
                users[share.billshare_user_placeholder.name] += share.amount
            else:
                users[share.billshare_user_placeholder.name] -= share.amount

    for user, cents in users.iteritems():
        users[user] = cents_to_dollar_str(cents)

    return {
        "users": dict(users)
    }

@view_config(route_name='user_overview', renderer='user_overview.jinja2')
def user_overview(request):
    if 'user' not in request.session:
        return HTTPFound(location='/')

    user_id = int(request.matchdict['id'])

    if user_id == request.session['user']['id']:
        return HTTPFound(location='/overview')

    shares = DBSession.query(BillShare).\
        join(BillShareUserPlaceholder).\
        filter(
            or_(BillShareUserPlaceholder.claimed_user_id == request.session['user']['id'],
                BillShareUserPlaceholder.claimed_user_id == user_id)
        ).all()

    my_shares = [{
        "description": share.bill.description,
        "amount": share.amount,
    } for share in shares if share.bill.primary_user_id == request.session['user']['id']]

    their_shares = [{
        "description": share.bill.description,
        "amount": share.amount,
    } for share in shares if share.bill.primary_user_id == user_id]

    return {
        "my_shares": my_shares,
        "their_shares": their_shares
    }

@view_config(route_name='account', renderer='account.jinja2')
def account(request):
    return {"status": "ok"}
