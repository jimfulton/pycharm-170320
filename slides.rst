Why Postgres Should Be Your Document Database




Why you might use a document database
=====================================

Ease of use:

- Dynamic schema

  Easy to change your mind about what to store.

  Easy to deal with structured data, like lists and dicts in your data.

- No joins, no ORM

Scalability:

- No joins

- No transaction -- wait...

Transactions/ACID
=================

ACID:

Atomicity
  If you make changes and then error, the system tolls back changes for you.
  This is HUGE

Consistency
  The database provides a consistent view of the database, which is a
  view of the database that would be produced by application logic
  operating on it sequentially.

Isolation
  Concurrent database activity is managed by the database system.  No
  locks, queues, etc, (but transaction errors and retries -- there's
  no free lunch)

Durable
  Changes made to the database persist reliabily

Tranactions/ACID shouldn't be traded away lightly
=================================================

A quote from the O'Reilly Mongo DB book:

  Updating a document is atomic: if two updates happen at the same time,
  whichever one reaches the server first will be applied, and then the
  next one will be applied. Thus, conflicting updates can safely be sent
  in rapid-fire succession without any documents being corrupted: the
  last update will “win.”

Chodorow, Kristina (2013-05-10). MongoDB: The Definitive Guide:
Powerful and Scalable Data Storage (Kindle Locations
1084-1087). O'Reilly Media. Kindle Edition.

Scalability
===========

Transactional databases generally have to be scaled vertically

- Limited

- But limits are high: 10s of thousanda of transactions per second.

- Ongoing improvements

- Sharding

- Microservices

80/20 rule
==========

90/10? 99/1? 99.9/.1?

The vast majority of applications don't need to scale.

Special case: Data collection
=============================

- Single operations (single document)

- Only inserts, or

  no concurrent updates(/deletes)

- Collecting raw data

Only need durability.

Typical of data collection/logging,
not business processing.

Postgres JSONB
==============

- Storage of JSON documents.

- Indexing and SQL queries

- As simple as JSON

- And therefore as complex as JSON:

  - Only one numeric type

  - No date/time type

  - No custom types

- Less forgiving than Python json

  - No nulls

  - Text-encoding (surrogate-pair issues)

Demo
====

Relational, document, and OO implementations of a Two-Tiered Kanban demo.

Quick demo of Two-Tiered Kanban project.

Flask/SQLAlchemy relational (partial) implementation

Flask/SQLAlchemy/JSONB (partial) implementation

Bobo/Newt/OO implementation
