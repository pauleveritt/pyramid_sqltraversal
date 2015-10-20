================
Simple Traversal
================

Pyramid traversal makes a tree of "location-aware" resources. In this
step we add the basics of traversal, showing folders that can be store
"inside" other folders. To do this, we need to introduce two weird
SQL/SQLAlchemy concepts: adjacency list pattern and polymorphism.

Adjacency List Relationships
============================

Let's say we have a Folder model in SQLAlchemy with a ``folders`` table
in our database. Each folder in our system is a row in the table. But
we'd like a concept where a folder can be "in" a folder. How can we
model that in our square database?

SQL has many patterns for this, and SQLAlchemy provides help for many
of them. One of the most popular is `adjacency list
relationships
<http://docs.sqlalchemy.org/en/latest/orm/self_referential.html>`_.
With this, a folder row can point to another folder row as part of a
relationship. More specifically, the table can a foreign key reference to
itself.

For example:

.. code-block:: python

    class Folder(Base):
        __tablename__ = 'folders'
        id = Column(Integer, primary_key=True)
        parent_id = Column(Integer, ForeignKey('folders.id'))
        children = relationship(
            "Node",
            lazy='dynamic',
            backref=backref('parent', remote_side=[id])
        )

In this, a Folder stores its ``id`` but also can store a "parent", thus
recording a ``parent_id``. You can ask a folder for its parent or for
its children. Behind the scenes, SQL is doing a join, but to the same
table.

Polymorphism
============

In most systems you have multiple models: customers, invoices,
expenses, etc. Each of these wind up with separate tables. How can we
have a self-joining table in this case? And how can we partition out
the common complexity into something that can be re-used?

SQLAlchemy has a concept of polymorphism, where one table "subclasses"
from another table. In this case, we can have a "Folder" model with the
parts that are unique to folders. But to get our resource tree, we can
have the Folder model inherit from a "Node" model that use used in all
of our types:

.. code-block:: python

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

    class Folder(Node):
        __tablename__ = 'folders'
        id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
        title = Column(Text)

This is a really useful approach. All of our framework-y stuff can go
into an efficient ``nodes`` table. In fact, we could provide that in a
library. Then, our business objects can derive from it.

With this background in place, on to the code. Nothing different in
``setup.py`` and ``development.ini`` so let's start in models.

Models
======

We have some major changes:

- We make a ``node.py`` module with the framework-y parts of traversal.
  Namely, a base Node model.

- We add a small ``folder.py`` module with our business models.

Let's start with the tiny but weird change in ``models/__init__.py``:

.. literalinclude:: mysite/models/__init__.py
    :caption: mysite/models/__init__.py
    :linenos:
    :emphasize-lines: 18-19

We moved the imports of our models down below the definition of
``Base``. Why is that? Because our ``node.py`` imports ``Base``. This
``__init__.py`` can't import node until after ``Base`` is defined.
Other than that, most is the same from the previous section.

Let's take a look at this base model ``Node`` in ``models/node.py``:

.. literalinclude:: mysite/models/node.py
    :caption: mysite/models/node.py
    :linenos:

We make a base model with a number of columns, each requiring imports
from SQLAlchemy. This base ``Node`` implements the adjacency list
relationship and polymorphism discussed above. ``Node`` then implements
some methods:

- A ``session`` property which provides a convenient way for a model
  object to grab the session

- The ``__mapper_args__`` needed for polymorphism

- Python ``__setitem__`` and __getitem__`` dictionary behaviour used
  by Pyramid traversal

- The ``__name__`` and ``__parent__`` for Pyramid location-awareness

As one more note on ``node.py``, we also moved the root factory in
here. It is easy to get the root: just look for a row that has no
``parent_id``.

Our ``folder.py`` is super-simple:

.. literalinclude:: mysite/models/folder.py
    :caption: mysite/models/folder.py
    :linenos:

A SQLAlchemy model that inherits from our base ``Node`` model. You have
to give the (plural) name of the table, provide the id as a foreign
key, and any other columns unique to Folder. In our case, ``title``.
For fun, we also make a ``RootFolder`` type, just in case our views
want to render that resource differently.

Things that could be better:

- *After Base*. Surely there's a smarter approach to avoid that caveat.
  Perhaps the imports of ``Node`` and ``Folder`` should happen inside
  the ``includeme``?

- *Resource-wide common attributes*. Perhaps in your system, everything
  has a ``title``. You can just extend the base ``Node`` to add more in
  that table. It's not just a code simplification: in some queries
  which we'll see later, we'll turn off polymorphism and only look at
  the ``Node`` table and its indexes.

Initialize
==========

The initialize script isn't too different:

.. literalinclude:: mysite/scripts/initialize_db.py
    :caption: mysite/scripts/initialize_db.py
    :emphasize-lines: 40-47
    :linenos:

We make the root folder, then use normal Python dictionary assignment
to add a subfolder.

Views
=====

Our views are still simple, but we put in a small trick:

.. literalinclude:: mysite/views.py
    :caption: mysite/views.py
    :emphasize-lines: 12, 14, 15, 18
    :linenos:

We have one view that matches when the context is a ``RootFolder`` and
another when the context is a ``Folder``.

Note the absence of routes. Pyramid is usually configured to map URLs
to views using routes, but can also use traversal. Once the Pyramid
application gets a root object from the root factory, it can hop
through the URL segments doing dictionary access. That's why we set up
``__getitem__`` on the ``Node`` model.

.. note::

    Yes, it means a separate SQL query per hop. These are cheap
    queries. Also, there are ways to do traversal all in one query,
    which we might look at later.

Conclusion
==========

We already have a pretty awesome system. No routes, we have
containment, things can be added inside things. Let's build a little
bit bigger system, then start doing some of the hard stuff.