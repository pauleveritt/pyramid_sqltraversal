from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from .models.node import root_factory
from .security import groupfinder


def main(global_config, **settings):
    config = Configurator(
        settings=settings,
        root_factory=root_factory
    )
    config.include('pyramid_jinja2')
    config.include('.models')
    config.scan('.views')
    config.add_static_view('static', 'mysite:static')

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'], callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    return config.make_wsgi_app()
