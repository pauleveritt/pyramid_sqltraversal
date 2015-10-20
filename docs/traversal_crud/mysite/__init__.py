from pyramid.config import Configurator
from .models.node import root_factory


def main(global_config, **settings):
    config = Configurator(
        settings=settings,
        root_factory=root_factory
    )
    config.include('.models')
    config.scan('.views')
    return config.make_wsgi_app()
