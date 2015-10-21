====================
Parents in One Query
====================

Now we get more ambitious. It turns out that getting the parents for a
resource is something we'll do a lot of in traversal applications.
Particularly for hierarchical security filtering of a query.

Our current approach uses Pyramid's lineage to travel the
``__parent__`` link, hopping up the parents with
``reversed(list(lineage(context)))``. But each call to ``__parent__``
generates a separate SQL query. That's inefficient. What if we could do
it one query?

This is where common table expressions (CTE) comes in, specifically, a
recursive CTE. In this step we add a ``lineage`` method to our
``Node`` model, which returns all the parents in one query.

Node
====

First our ``node.py`` changes:

.. literalinclude:: mysite/models/node.py
    :caption: mysite/models/node.py, Node.lineage
    :pyobject: Node.lineage
    :linenos:

This is complicated SQLAlchemy, but it does the trick. For performance
reasons, it turns off polymorphism during the query for the recursion,
then once it has found the nodes in the lineage, returns those with
polymorphism back on.

Views
=====

The only change in our views is to remove
``self.parents = reversed(list(lineage(context)))`` from the view class
constructor. The context is an instance of a model that derives from
Node. Pyramid templates have a ``context`` available (in addition to
``request`` and ``view``.) So instead, we can just do this directly:

.. literalinclude:: mysite/templates/base.jinja2
    :language: jinja
    :caption: base.jinja2
    :emphasize-lines: 32
    :linenos:

That is, we use ``context.lineage|reverse``.

To Do
=====

- At this point, probably time to start thinking about synthesizing
  huge data sets, bulk loading, then measuring some PG query planner
  time