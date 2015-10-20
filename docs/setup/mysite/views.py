from pyramid.view import view_config, view_defaults

from .models.node import Node


@view_defaults(renderer='json')
class MySite:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context=Node)
    def root_view(self):
        return dict(id=self.context.id)
