from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    )

@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    return {"status": "ok"}

@view_config(route_name='overview', renderer='overview.jinja2')
def overview(request):
    return {"status": "ok"}

@view_config(route_name='add_bill', renderer='add_bill.jinja2')
def add_bill(request):
    return {"status": "ok"}

@view_config(route_name='user_overview', renderer='user_overview.jinja2')
def user_overview(request):
    return {"status": "ok"}

@view_config(route_name='account', renderer='account.jinja2')
def account(request):
    return {"status": "ok"}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_billemall_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

