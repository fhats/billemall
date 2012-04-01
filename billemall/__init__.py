from pyramid_beaker import session_factory_from_settings
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings)
    config.include('pyramid_beaker')
    config.include('pyramid_jinja2')
    config.set_session_factory(session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('overview', '/overview')
    config.add_route('add_bill', '/add_bill')
    config.add_route('user_overview', '/user/{id}')
    config.add_route('account', '/account')
    config.scan()
    return config.make_wsgi_app()

