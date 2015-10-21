====
ACLs
====

Pyramid has a rich security model based on access control lists (ACLs).
A location-aware resource can provide an ``__acl__`` sequence of access
control entries (ACE), either on the class or instance. Views can then
state a permission needed to get to a certain URL. Pyramid will then
check the ACL, using the credentials of the user and the permission, to
see if access is allowed.

In this section we're going to set this up to use ACLs stored in the
database. Specifically:

- Add the regular Pyramid authentication/authorization story, with a
  ``login`` view

- Make a database column capable of storing an ACL

- Add a class-based ACL on the ``Folder`` model, but provide some
  initial rows with an instance-based ACL in the column

- Make a method in ``Node`` capable of sorting all this out

ACL Column Type
===============

Needless to say, storing in a column an array where the second item can
be an array is a bit of a trick. PostgreSQL has some advanced
facilities, including arrays, JSONB, and hstore. We'll commit ourselves
to at this point to a ``pyramid_sqlalchemy`` that requires PostgreSQL
9.4+, and use JSONB.

This does mean that each change to the schema or initialize_db script
means:

.. code-block:: bash

    $ dropdb sqltraversal; createdb -O sqltraversal sqltraversal

As a note, though, we are ignoring for a moment:

- *Mutability*. SQLAlchemy can't detect changes to these column types
  without a little help. We'll deal with that later. For now, we just
  create the JSON data in ``initialize_db`` and don't change it.

- *Hierarchies*. A later section will address looking at the resource
  then its parents until finding a matching ACL.

- *Permission filtering in queries*. This is the big one, but out of
  scope for now. We are only concerned with a URL that traverses to an
  ACL-protected resource.

We will, though, look for an ACL in the column and, if not present, use
an ACL on the class.

Authentication and Authorizaton
===============================

Standard Pyramid stuff here. Our ``__init__.py`` needs some additions:

.. literalinclude:: mysite/__init__.py
    :caption: mysite/__init__.py
    :emphasize-lines: 1,2,5, 18-24
    :linenos:

We import our policies, as well as a "groupfinder" function used to get
principals from credentials. We then wire those policies into our
configuration.

Our configuration file needs a secret:

.. literalinclude:: development.ini
    :caption: development.ini
    :emphasize-lines: 7
    :linenos:

Here is a simple, in-memory database of users and roles, along with a
function used to retrieve from that "database:

.. literalinclude:: mysite/security.py
    :caption: mysite/security.py
    :linenos:

And finally, login/logout views on the ``RootFolder``:

.. literalinclude:: mysite/views.py
    :caption: mysite/views.py
    :emphasize-lines: 25-51
    :linenos:

This also means a simple login form:

.. literalinclude:: mysite/templates/login.jinja2
    :language: jinja
    :caption: mysite/templates/login.jinja2
    :linenos:

ACLs
====

Let's teach our models to do ACLs. First, our based model ``Node``:

.. literalinclude:: mysite/models/node.py
    :caption: mysite/models/node.py
    :emphasize-lines: 36, 99-103
    :linenos:

The ``__acl__`` property tries first on the row, to see if the resource
has a "persistent" ACL stored. If not, it returns the ACL from the
model (or None if not present there either.) Here's what the ACL on the
``Folder`` model might look like:

.. literalinclude:: mysite/models/folder.py
    :caption: mysite/models/folder.py
    :emphasize-lines: 15-16
    :linenos:

Let's setup our initialize script to make a folder without an ACL, as
we've done so far, but also a folder *with* an ACL:

.. literalinclude:: mysite/scripts/initialize_db.py
    :caption: mysite/scripts/initialize_db.py
    :emphasize-lines: 55-58
    :linenos:

For this ``/f2`` folder, you can only view it if you are the ``admin``
user.

Permissions
===========

So now the last step. We need to protect the "View Folder" view with
the permission:

.. literalinclude:: mysite/views.py
    :caption: mysite/views.py
    :emphasize-lines: 61
    :linenos:

Now, if you run the app and go to the root, you will see two folders
listed. If you are not logged in, then clicking on the second folder
will trigger forbidden.

We could fix this by hiding the second folder. That is, using
Pyramid's ``has_permission`` to only generate a ``<li>`` for
folders that the current user is allowed to view. Let's give that a try:

.. literalinclude:: mysite/templates/contents.jinja2
    :language: jinja
    :caption: mysite/templates/contents.jinja2
    :emphasize-lines: 6, 21
    :linenos:

We have now hidden any children that we're not allowed to see.

To Do
=====

- Better way to do class-based ``default_acl``? Perhaps a sqla hybrid
  property could differentiate between the class-based and table-based

- Move the ACL to an ACLType, which included mutation tracking and
  centralized the complexity

- The "trickeration" comment in Node.__acl__