import unittest
import transaction

from pyramid import testing


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class DummyContext:
    id = 1


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        settings = self.config.get_settings()

        from .models import (
            get_session,
            get_engine,
            get_dbmaker,
        )

        self.engine = get_engine(settings)
        dbmaker = get_dbmaker(self.engine)

        self.session = get_session(transaction.manager, dbmaker)

    def init_database(self):
        from .models import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.create_all(self.engine)


class TestMyViewSuccessCondition(BaseTest):
    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from .models.folder import RootFolder, Folder
        from .models.document import Document
        root = RootFolder(name='',
                          title='sqltraversal Demo'
                          )
        self.session.add(root)
        f1 = root['f1'] = Folder(
            title='Folder 1'
        )
        f1['da'] = Document(title='Document 1A')

    def test_passing_root_view(self):
        from .views import MySite
        info = MySite(DummyContext(), dummy_request(self.session)).root_view()
        self.assertEqual(info['id'], 1)

    def test_passing_folder_view(self):
        from .views import MySite
        info = MySite(DummyContext(), dummy_request(self.session)).folder_view()
        self.assertEqual(info['id'], 1)

    def test_passing_document_view(self):
        from .views import MySite
        info = MySite(DummyContext(), dummy_request(self.session)).document_view()
        self.assertEqual(info['id'], 1)


class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('development.ini')
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_hello_world(self):
        res = self.testapp.get('/', status=200)
        self.assertEqual(res.json_body['id'], 1)
