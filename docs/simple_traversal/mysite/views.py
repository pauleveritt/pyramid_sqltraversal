from pyramid.view import view_config, view_defaults

from .models.folder import RootFolder, Folder


@view_defaults(renderer='json')
class MySite:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context=RootFolder)
    def root_view(self):
        return dict(id=self.context.id, is_root=True)

    @view_config(context=Folder)
    def folder_view(self):
        return dict(id=self.context.id, is_root=False)
