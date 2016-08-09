from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
)

from .node import Node


class Document(Node):
    __tablename__ = 'documents'
    id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    title = Column(Text)
