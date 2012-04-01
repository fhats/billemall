import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Bill,
    BillShare,
    BillShareUserPlaceholder,
    User,
    Base,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        user = User(name="Fred Hatfull", email="lurkingfridge79@gmail.com", password="password")
        DBSession.add(user)

        other_user = User(name="Steve Johnson", email="suckawang@steveasleep.com", password="password")
        DBSession.add(other_user)

        DBSession.flush()
        DBSession.refresh(user)
        DBSession.refresh(other_user)

        fred_holder = BillShareUserPlaceholder(user=user)
        DBSession.add(fred_holder)

        steve_holder = BillShareUserPlaceholder(user=other_user)
        DBSession.add(steve_holder)

        toby_holder = BillShareUserPlaceholder(name="Toby Waite")
        DBSession.add(toby_holder)

        DBSession.flush()
        DBSession.refresh(fred_holder)
        DBSession.refresh(steve_holder)
        DBSession.refresh(toby_holder)

        # Add a test bill
        bill = Bill(primary_user_id=fred_holder.id, description="Sexy times and stuff", total=1100)
        DBSession.add(bill)

        DBSession.flush()
        DBSession.refresh(bill)

        bs = BillShare(bill_id=bill.id, billshare_user_placeholder_id=steve_holder.id, amount=300)
        DBSession.add(bs)

        f_bs = BillShare(bill_id=bill.id, billshare_user_placeholder_id=fred_holder.id, amount=300)
        DBSession.add(f_bs)

        t_bs = BillShare(bill_id=bill.id, billshare_user_placeholder_id=toby_holder.id, amount=500)
        DBSession.add(t_bs)
