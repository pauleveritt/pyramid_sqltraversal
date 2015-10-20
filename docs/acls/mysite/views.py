from random import randint

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from .models.folder import RootFolder, Folder
from .models.document import Document


class RootViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/root.jinja2', context=RootFolder)
    def view(self):
        print ('acl', self.context.__acl__)
        return dict(children=self.context.children)

    @view_config(name='delete')
    def delete(self):
        self.request.dbsession.delete(self.context)
        url = self.request.resource_url(self.context.__parent__)
        return HTTPFound(url)


class FolderViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer="templates/folder.jinja2",
                 context=Folder)
    def view(self):
        print ('acl', self.context.__acl__)
        return dict(children=self.context.children)

    @view_config(name="add_folder", context=Folder)
    def add(self):
        # Make a new Folder
        title = self.request.POST['folder_title']
        name = str(randint(0, 999999))
        new_folder = self.context[name] = Folder(title=title)

        # Redirect to the new folder
        url = self.request.resource_url(new_folder)
        return HTTPFound(location=url)


class DocumentViews:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name="add_document", context=Folder)
    def add(self):
        # Make a new Document
        title = self.request.POST['document_title']
        name = str(randint(0, 999999))
        new_document = self.context[name] = Document(title=title)

        # Redirect to the new document
        url = self.request.resource_url(new_document)
        return HTTPFound(location=url)

    @view_config(renderer="templates/document.jinja2",
                 context=Document)
    def view(self):
        return dict()
