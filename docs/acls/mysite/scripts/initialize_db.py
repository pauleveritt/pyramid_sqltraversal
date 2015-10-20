import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models import (
    Base,
    get_session,
    get_engine,
    get_dbmaker,
)
from ..models.folder import RootFolder, Folder
from ..models.document import Document


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def initialize(Base, engine, dbsession):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        __acl__ = [
            ['Allow', 'paul', 'read'],
            ['Allow', 'jane', 'read'],
            ['Allow', 'paul', 'write']
        ]
        root = RootFolder(name='',
                          title='sqltraversal Demo 22',
                          __acl__=__acl__
                          )
        dbsession.add(root)
        f1 = root['f1'] = Folder(
            title='Folder 1'
        )
        f1['da'] = Document(title='Document 1A')


def playground(dbsession):
    with transaction.manager:
        root = dbsession.query(Folder).filter_by(parent_id=None).one()
        print("result", root.__acl__[0][0])


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    dbmaker = get_dbmaker(engine)

    dbsession = get_session(transaction.manager, dbmaker)

    initialize(Base, engine, dbsession)
    playground(dbsession)
