from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
)

from .node import Node


class Folder(Node):
    __tablename__ = 'folders'
    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    title = Column(Text)


class RootFolder(Folder):
    pass
