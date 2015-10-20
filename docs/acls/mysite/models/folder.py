from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
)
from pyramid.security import Allow, Everyone
from .node import Node


class Folder(Node):
    __tablename__ = 'folders'
    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    title = Column(Text)
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'add')]


class RootFolder(Folder):
    pass
