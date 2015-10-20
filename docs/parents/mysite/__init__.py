from pyramid.config import Configurator
from .models.node import root_factory


def main(global_config, **settings):
    config = Configurator(
        settings=settings,
        root_factory=root_factory
    )
    config.include('pyramid_jinja2')
    config.include('.models')
    config.scan('.views')
    config.add_static_view('static', 'mysite:static')
    return config.make_wsgi_app()
