from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from .meta import Base


class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


Index('my_index', Todo.name, unique=True, mysql_length=255)
