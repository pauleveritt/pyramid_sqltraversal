============================
Pyramid and SQLAlchemy Setup
============================

Pyramid and SQLAlchemy are great friends, but there are different
approaches to integrating the two. ``pyramid_sqlalchemy`` is one, but
uses globals. Recently, the Pyramid scaffold has adopted some best
practices.

In this step we make a Pyramid application based on those best
practices. This app will:

- Connect to a SQLite database using SQLAlchemy

- Provide a console script that populates the database

- Give one view that returns JSON

- Provide a request hook helper for conveniently getting at the database
  session

We will *not* write this as a library in this step. We will instead go
all the way through writing an application, and *then* write a
``pyramid_sqltraversal`` library.

``setup.py``
============

Our ``setup.py`` is straightforward. It includes some packages and sets
up our Pyramid entry points:

.. literalinclude:: setup.py
  :linenos:

We will use SQLite for as long as we can, then switch to PostgreSQL.

Things that could be better:

- *Dependencies*. The dependencies need to be re-organized. Put sphinx,
  nose, webtest, etc. as dev dependences.*

- *pytest*. If that's considered more modern, use it.

- *Unit and functional tests*. I didn't actually write any. Not only
  that, sure would be nice for some ``pyramid_sqltraversal`` library
  to provide some fixture helpers.

``development.ini``
===================

Our ``pserve`` configuration file is simple:

.. literalinclude:: development.ini
    :language: ini
    :linenos:

Only thing to note: we include ``pyramid_tm`` in the ini file, rather
than imperatively in the code, because it should be possible to run a
site with transactions off (read-only).

Loader Console Script
=====================

Our ``setup.py`` entry point defined an ``initialize_db`` console
script:

.. literalinclude:: mysite/scripts/initialize_db.py
    :linenos:

After some basic imports, we get stuff needed from our models:

- The models themselves

- The imports of the engine-y stuff

Our main function parses the command-line argument to get the
configuration file, sets up logging, and then does a four-part dance
to get the database setup:

- Get the engine

- Get the dbmaker using the engine

- Get the session using the dbmaker

- Bootstrap the SQLAlchemy metadata base using the engine.

It is *important* for this module to import any models that are needed,
*before* bootstrapping the metadata. This point will lead to duplicate
model imports in this console script and in the actual running Pyramid
code.

Things that could be better:

- *request.dbsession in console script*. ``request.dbsession`` is
  awesome, when you're in a request. We're not, so we have to do all
  that work ourselves. Anyway to abstract the helper so it can provide
  a console-script-oriented helper?

- *Lots of boilerplate*. Later, when we write a library, we should make
  writing console scripts a lot easier. They are all going to want to
  parse the ini file passed in, get the settings.

- *Double model imports*. Any way to avoid duplication of imports for
  all of your models?

``models``
==========

Before getting into the app server code, let's look at the models, as
they were just used in the console script.

The ``models`` directory is a Python package with an ``__init__.py``.
Just like Pyramid uses this file as a place to wire together your WSGI
application, SQLAlchemy users commonly put their models in a directory
with common wire-up in the directory/package ``__init__.py``:

.. literalinclude:: mysite/models/__init__.py
    :caption: mysite/models/__init__.py
    :linenos:

This file acts as the central bootstrapping point for SQLAlchemy, as
well as its integration into Pyramid. We start with the basic imports
for SQLAlchemy in Pyramid.

The ``NAMING_CONVENTION`` block uses a SQLAlchemy best practice for
various definitions, as suggested by
`SQLAlchemy/Alembic documentation <http://alembic.readthedocs
.org/en/latest/naming.html>`_.

Then the important part: the SQLAlchemy metadata base is wired up in
*local* scope, with functions that return the session, engine, and
dbmaker to other modules.

It's import to import your models in this file, as we do with ``Node``.

Finally, we provide a Pyramid ``includeme`` function to make it easy to
apply all of our model and SQLAlchemy setup with a simple
``config.include('.models')`` in our Pyramid bootstrapping. This
``includeme`` function has a very important addition: we add a custom
method ``dbsession`` to Pyramid's request, allowing easy access to the
session in Pyramid code. Simply do ``request.dbsession`` to get the
session. ``reify=True`` turns the method into a property, one that is
cached for the duration of a request.

Our sample application at this point has one model called ``Node`` in
``models/node.py``:

.. literalinclude:: mysite/models/node.py
    :caption: mysite/models/node.py
    :linenos:

Nothing major here...a table with a single column ``id``. We follow the
convention of singular class name ``Node`` and plural table name
``nodes``. We also provide some sample data for this model that the
initializer script can use during development.

We do, however, make a Pyramid "root factory" for the application. This
is a function registered with the Pyramid configuration which, on each
request, gets run and returns an object to act as the "root" of the
resource tree.

- Pyramid/SQLAlchemy best practices

    - Class (singular) and table (plural)

    - root factory

    - config.include models, to put common model wiring in the subpackage

    - context-based views, versus routes

- Some kind of test console script that exercises the API

Things that could be improved:

- *Sample Data*. Putting sample data in each model won't really work,
  as we need to create a tree with a mixture of data from different
  models.

Web App Setup
=============

We not have a Python package with console scripts and database models.
We need to get Pyramid setup and add a view.

Our ``__init__.py``:

.. literalinclude:: mysite/__init__.py
    :caption: mysite/__init__.py
    :linenos:

We import the root factory and pass it into our ``Configurator`` setup.
We use ``config.include('.models')`` to do all the lifting for model
setup.

Our view is equally simple:

.. literalinclude:: mysite/views.py
    :caption: mysite/views.py
    :linenos:

We have a view class with one view. The view class grabs the request
*and* the context, which comes from the root factory.

Conclusion
==========

In this step we setup best practices for Pyramid and SQLAlchemy. We
stayed away from making this into a library. We also stayed away from
almost everything to do with traversal.
