================
Filtered Queries
================

- On to the holy grail, filtering in a query

- Add a "All Folders" link in header

- Setup initialize to provide a mixture of folders viewable by
  different principals

To Do
=====

- Improve initialize_db to clear out all the tables and data before
  running, to save a dropdb createdb step

- Make an ACLType to consolidate all of this

- Simpler way to let the class provide a default ACL for the type/model

- Need to get the class-based ACLs coerced into the generated SQL

    http://techspot.zzzeek.org/2011/10/29/value-agnostic-types-part-ii/