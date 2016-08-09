from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    ForeignKey,
    String
)
from sqlalchemy.orm import (
    relationship,
    backref,
    object_session
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.util import classproperty
from . import Base


def root_factory(request):
    return request.dbsession.query(Node).filter_by(parent_id=None).one()


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('nodes.id'))
    children = relationship(
        "Node",
        lazy='dynamic',
        backref=backref('parent', remote_side=[id])
    )
    type = Column(String(50))

    @property
    def session(self):
        return object_session(self)

    @classproperty
    def __mapper_args__(cls):
        return dict(
            polymorphic_on='type',
            polymorphic_identity=cls.__name__.lower(),
            with_polymorphic='*'
        )

    def __setitem__(self, key, node):
        session = self.session
        node.name = str(key)
        if self.id is None:
            session.flush()
        node.parent_id = self.id
        session.add(node)
        session.flush()

    def __getitem__(self, key):
        try:
            return self.children.filter_by(name=key, parent=self).one()

        except NoResultFound:
            raise KeyError(key)

    @property
    def __name__(self):
        return self.name

    @property
    def __parent__(self):
        return self.parent
