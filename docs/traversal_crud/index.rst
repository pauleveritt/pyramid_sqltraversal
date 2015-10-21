==============
Traversal CRUD
==============

Let's make a more meaningful demo: a web UI letting you add folders and
documents inside a folder, or delete a folder. This will pave the way
for several points later, such as hooking into Pyramid's security model.

In this section we:

- Add a Document model

- Make a web UI for browsing/deleting/adding items in a folder

``setup.py`` and ``development.ini``
====================================

In ``setup.py`` we add a dependency on ``pyramid_jinja2``. Then in our
configuration file, we set ``pyramid.reload_templates`` for debugging
purposes.

Models
======

We add a simple Document model in ``models/document.py``:

.. literalinclude:: mysite/models/document.py
    :caption: mysite/models/document.py
    :linenos:

Initialize
==========

Small changes to support adding a document by default in a subfolder:

.. literalinclude:: mysite/scripts/initialize_db.py
    :caption: mysite/scripts/initialize_db.py
    :emphasize-lines: 16, 49
    :linenos:

Static Assets
=============

We won't include the full source here, but we have a ``base.jinja2``
master template, then per-view templates for viewing the root folder,
viewing a folder, and viewing a document. We also have a macro for
displaying folder contents, to share between the root folder and folder
templates.

Views
=====

Some big changes here, obviously, as we are adding a web UI:

.. literalinclude:: mysite/views.py
    :caption: mysite/views.py
    :linenos:

We change into view classes for each of the models: ``RootViews``,
``FolderViews``, and ``DocumentViews``. These views are registered
against a ``context``, not a route name. The framework finds the object
for a URL, and based on the class of that object, you can make named
views without routes.

The views are changed to use Jinja2 renderers.

Finally, our view classes find the "parents" of a resource, to show in
breadcrums, with ``reversed(list(lineage(context)))``. We'll look at
this more later.

WSGI Init
=========

Our ``__init__.py`` adds an include for ``pyramid_jinja2`` and a static
view for the CSS and favicon.

.. literalinclude:: mysite/__init__.py
    :caption: mysite/__init__.py
    :emphasize-lines: 10,13
    :linenos:
