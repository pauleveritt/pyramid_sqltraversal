from sqlalchemy import (
    Column,
    Integer
)

from . import Base


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)


def root_factory(request):
    return request.dbsession.query(Node).first()


sample_data = [
    dict(),
    dict()
]
