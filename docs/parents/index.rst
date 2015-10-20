====================
Parents in One Query
====================

- Change node.py to add back the recursive CTE

- Change views and templates to use it

    - Get rid of view.parents and the call to lineage

    - In template, use context.lineage | reverse

To Do
=====

- At this point, probably time to start thinking about synthesizing
  huge data sets, bulk loading, then measuring some PG query planner
  time