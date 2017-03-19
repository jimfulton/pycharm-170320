==============================================================
PyCharm Webinar: Why Postgres Should Be Your Document Database
==============================================================

with Jim Fulton, March 20, 2017

In this webinar, we'll talk about why you might use `PostgreSQL
<https://www.postgresql.org/>`_ as your document database.  We'll also
talk about transactions, why they're important, and some common
pitfalls.

As an example, we'll look at implementing a two-tiered Kanban system
using 3 approaches:

- relational,

- document oriented, and

- object oriented.

All of the examples will use the `Python programming language
<https://www.python.org/>`_.


You'll be able to follow along by looking at the databases using
database connection information that I'll share at the time of the Webinar.

The first two examples are in directories in this repository:

rtasks
  A (partial) relational implementation using `Flask
  <http://flask.pocoo.org/>`_ and `SQL Alchemy
  <https://www.sqlalchemy.org/>`_.

jtasks
  A (partial) document-oriented and relational implementation also
  using `Flask <http://flask.pocoo.org/>`_ and `SQL Alchemy
  <https://www.sqlalchemy.org/>`_.

The third example looks a `two-tiered kanban
<https://github.com/zc/twotieredkanban>`_, which uses a hybrid
object-oriented and document-oriented implementation.  It uses `bobo
<http://bobo.readthedocs.io>`_ for it's web framework and `Newt DB
<http://www.newtdb.org>`_ to provide the hybrid object-oriented
document-oriented database on top of Postgres.

Links
=====

PostgreSQL
  https://www.postgresql.org/

Python
  https://www.python.org/

SQL Alchemy object-relational mapper
  https://www.sqlalchemy.org/

Newt DB, hybrid object-oriented and document-oriented database
  http://www.newtdb.org

pq, a PostgreSQL-based transactional queuing system
  https://github.com/malthe/pq/

pjpersist, an object-oriented interface to PostgreSQL.
  https://github.com/Shoobx/pjpersist

Flask web framework
  http://flask.pocoo.org/

Bobo web framework
  http://bobo.readthedocs.io

Two-tiered Kanban
  https://github.com/zc/twotieredkanban
