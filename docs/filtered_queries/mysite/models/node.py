from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    ForeignKey,
    String,
    literal
)
from sqlalchemy.orm import (
    relationship,
    backref,
    object_session,
    aliased
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_method
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
    acl = Column(JSONB)

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

    @property
    def lineage(self):
        session = self.session
        init_cte = (
            session.query(
                Node.id,
                Node.parent_id,
                literal(0).label('index'))
                .filter(Node.id == self.id)
                .cte(name='lineage', recursive=True)
        )
        child_alias = aliased(init_cte, name='child')
        parent_alias = aliased(Node, name='parent')
        lineage_cte = init_cte.union_all(
            session.query(
                parent_alias.id,
                parent_alias.parent_id,
                child_alias.c.index + 1)
                .filter(parent_alias.id == child_alias.c.parent_id))
        q = (
            session.query(Node).with_polymorphic('*')
                .join(lineage_cte, Node.id == lineage_cte.c.id)
                .order_by(lineage_cte.c.index))
        return q.all()

    @property
    def all(self):
        return self.session.query(self.__class__)

    @property
    def __acl__(self):
        # Later, use some trickeration to get the class acl without
        # resorting to polymorphism
        return getattr(self, 'acl', None) or self.__class__.default_acl

    @hybrid_method
    def has_permission(self, principal, permission):
        # Shouldn't get in here
        raise KeyError('Should not get in Python expression')

    @has_permission.expression
    def has_permission(cls, principal, permission):
        # This will need to emit some SQL that iterates through a
        # sequence of ACEs, looking for allows or denies. Fake some
        # simple case for now.
        from sqlalchemy.sql import case
        return case(
            [
                (cls.id == 2,
                 True),
            ], else_=False)

    def filtered_children(self, principal='editor', permission='view'):
        return self.children.filter(self.__class__.has_permission(
            principal, permission
        ))
