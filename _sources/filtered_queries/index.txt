================
Filtered Queries
================

In our last example, we finished by security filtering the retrieved
children using Pyramid's ``has_permission``. This works ok, but has
some negatives:

- You have to get a bunch of objects back and then filter in Python, so
  you can't use ``LIMIT`` at the SQL level

- If you're going to be doing a richer SQLAlchemy query, you'd like to
  combine permission filtering with all the other clauses, to get the
  most efficient query, instead of bunches of queries to bring rows
  back into Python for further narrowing

There are several hard things ``pyramid_sqlalchemy`` hopes to do. This
is the first one. In this section, we'd like to add an "All Folders"
link in the header. Clicking it will look through the entire hierarchy,
showing the first 20 Folders, sorted by title.

And, filtered by permission.

Strategy
========

There are a few key points in this step:

- *Permission filtering in SQL*. We can't bring rows back to Python and
  let Pyramid pick them apart. If we have 100,000 folders, that's
  100,000 queries.

- *ACL parsing in SQL*. In a related sense, we need pure-SQL logic to
  take a sequence of principals and a permission, then analyze a JSONB
  structure of access control entries. When you find a match, stop
  looking and return allow or deny.

- *Instance and class ACLs*. Most resources will *not* have a custom
  ACL on the resource. They'll get their ACL from the model. That
  model-based ACL needs to get passed into the SQL query, presumably as
  a JSONB type.

- *Recursion*. If you don't find a matching ACE on a resource, keep
  looking up the parents. As part of the query, bailing out when you
  find a matching ACE.

- *Natural and performant in SQLAlchemy*. We need permission filtering
  to combine with other parts of the query -- filters, sorting, and
  especially limits -- in a natural way. Not just natural, but
  performant.

The approach attempted here is to use a SQLAlchemy hybrid method, and
have the "expression" part construct a SQL statement. Then, combine
this in some way with a recursive CTE that, for each node, looks at the
parents.

Some notes:

- This likely should be done in a way that only the ``nodes`` table is
  used. Thus, no polymorphism. We'll have to get the class-based ACLs via
  reflection at startup, then find a way to make them available in the
  queries.

- Sure wish there was a way, during the execution of a query, to cache
  the ACL result on intermediate parent nodes. If you evaluate the
  hierarchical ACL for ``/f1/f2/f3/doc1`` during a query, when you then
  look at ``/f1/f2/f3/doc2``, you know the answer for
  ``/f1/f2/f3``.

- It really is critical for the optimizer to do all the other parts of
  a query, and kick in the limit on this part. Of course sorting then
  blows that out the window.

To Do
=====

- Improve initialize_db to clear out all the tables and data before
  running, to save a dropdb createdb step

- Make an ACLType to consolidate all of this

- Simpler way to let the class provide a default ACL for the type/model

- Need to get the class-based ACLs coerced into the generated SQL

    http://techspot.zzzeek.org/2011/10/29/value-agnostic-types-part-ii/