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

    def __json__(self, request):

        return dict(
            id=self.id,
            title=self.title,
            __acl__=self.__acl__,
        )


class RootFolder(Folder):
    pass
