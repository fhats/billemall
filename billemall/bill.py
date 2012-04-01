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
        
        primary_name = request.params.get('primary_name', None)

        bill_total = sum([entry['amount'] for entry in request_body])

        primary_placeholder = None
        user_placeholder = None # placeholder of the logged in user

        # Create the Bill
        # This shit is all done in a single transaction in order to have nice ROLLBACK
        # semantics if any one of these transactions fails.
        with transaction.manager:

            users_billshares = DBSession.query(BillShare).\
                join(Bill).\
                join(BillShareUserPlaceholder).\
                filter(BillShareUserPlaceholder.claimed_user_id == request.session['user']['id']).all()
            user_bill_ids = [billshare.bill_id for billshare in users_billshares]

            previously_billed_placeholders = DBSession.query(BillShareUserPlaceholder).\
                join(BillShare).\
                join(Bill).\
                filter(
                    and_(BillShare.bill_id.in_(user_bill_ids), 
                        BillShare.billshare_user_placeholder_id != Bill.primary_user_id)
                    ).all()

            placeholders = []
            for entry in request_body:
                name = entry['name']
                amount = entry['amount']
                # Create a placeholder for the BillShares of this bill

                # Use existing placeholders if they already exist for users that
                # have been billed before by this user.
                existing_user_placeholder = None
                for previously_billed_placeholder in previously_billed_placeholders:
                    if previously_billed_placeholder.name == name:
                        existing_user_placeholder = previously_billed_placeholder

                if name == request.session['user']['name']:
                    placeholder = DBSession.query(BillShareUserPlaceholder).filter_by(id=request.session['placeholder']).first()
                elif existing_user_placeholder:
                    placeholder = existing_user_placeholder
                else:
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

            bill = Bill(primary_user_id=primary_placeholder.id, total=bill_total)
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
        try:
            people = json.loads(request.params['people'])
        except (KeyError, ValueError):
            return {}

        return {
            "people": people,
            "amount": request.params["amount"]
        }


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
        b['amount'] = cents_to_dollar_str(billee.amount)

        billees.append(b)

    total = bill.total

    primary = {
        'name': bill.primary_user.name,
        'id': bill.primary_user.id
    }

    return {
        "billees": billees,
        "primary": primary,
        "total": cents_to_dollar_str(total)
    }

def cents_to_dollar_str(cents):
    return "%0.2f" % (cents / 100)
