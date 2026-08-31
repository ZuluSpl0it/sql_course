# Lesson 09 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file. Expected outputs were
verified against the database as shipped (SQLite 3.31.1). Compare **outputs**,
not query text.

---

## Quiz

### Q1 — declared type vs. storage class

A declared type (`NVARCHAR(40)`, `NUMERIC(10,2)`, `DATETIME`) is only an *affinity* — a rule for how to try to convert a value on insert. The **storage class** is what actually lives in the database, one of the five: `NULL`, `INTEGER`, `REAL`, `TEXT`, `BLOB`. SQLite never stores an `NVARCHAR`; it stores `TEXT`, and `typeof()` will tell you so.

### Q2 — why did the bad `TrackId` insert succeed?

Because the connection's `PRAGMA foreign_keys` was `OFF` (the default), so the `FOREIGN KEY` clause on `InvoiceLine.TrackId` wasn't being enforced. Turn it on in the *same* session and the same insert fails with `FOREIGN KEY constraint failed`. The setting is per-connection and resets to off on every new one — there is no database-level switch.

### Q3 — `ADD COLUMN … UNIQUE`

Error: `Cannot add a UNIQUE column`. A `UNIQUE` (or `PRIMARY KEY`) column has to be part of the `CREATE TABLE`; 3.31 can't add one after the fact, and there's no `ADD CONSTRAINT` at all. The workaround is a rebuild: `CREATE TABLE` a new version with the constraint, `INSERT … SELECT` the rows into it, `DROP TABLE` the old one, and `ALTER TABLE … RENAME TO` the new one to the original name.

### Q4 — `CREATE TABLE` in a rolled-back block

**False.** DDL runs inside the transaction like any other statement, so the `ROLLBACK` undoes the `CREATE` entirely — the table doesn't exist afterwards at all (Example 11: the count of `TxnTable` in `sqlite_master` is 0 after the rollback).

### Q5 — `Track`'s foreign keys

`PRAGMA foreign_key_list(Track)` returns, in order: **`MediaType`** (from `MediaTypeId`), **`Genre`** (from `GenreId`), and **`Album`** (from `AlbumId`) — each with `NO ACTION` on update and delete. (The order is the order the clauses appear in the DDL, which is why `Album` comes last even though it's the most important relationship.)

### Q6 — why can't you drop the autoindex?

`sqlite_autoindex_PlaylistTrack_1` isn't an object you created — SQLite built it automatically to enforce `PlaylistTrack`'s `UNIQUE(PlaylistId, TrackId)` constraint. Dropping it would remove the enforcement, so SQLite refuses it (you'd get `cannot drop 'sqlite_autoindex_PlaylistTrack_1' — index is in use`). You can only get rid of it by dropping the constraint, which means rebuilding the table.

---
