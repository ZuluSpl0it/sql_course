# Lesson 03: Writing Data

So far you've only *read* the database. Today you make it change — and, just
as importantly, you learn the safety net that keeps a bad write from
destroying your data. Three verbs do the writing: `INSERT` (add a row),
`UPDATE` (change rows), `DELETE` (remove rows). And one idea sits above all
of them: the **transaction**, which lets you bundle several writes into one
all-or-nothing unit.

The rules of the road for this lesson:

- Work against Jasper's in-memory copy of the database; never overwrite the
  repository file.
- Each statement is **committed immediately** unless you start a transaction.
  Reload the original file to reset the browser session.

## 1. The concept

### 1.1 INSERT — adding rows

```sql
INSERT INTO Artist (Name)
VALUES ('The Course Test Band');
```

`INSERT INTO <table> (columns...) VALUES (values...)`. The column list and
the value list must match **position by position**: the first value goes to
the first named column.

You don't have to name every column — only the ones you're providing
values for (or that can't be defaulted). `Artist.ArtistId` is the primary
key, and SQLite will assign the next free number (276 here) automatically.
If you want to know which number it picked:

```sql
SELECT last_insert_rowid();
```

One statement can insert many rows by adding comma-separated value lists:

```sql
INSERT INTO Artist (Name)
VALUES ('Second Test Artist'),
       ('Third Test Artist');
```

### 1.2 UPDATE — changing rows

```sql
UPDATE Customer
SET    City = 'Ottawa'
WHERE  CustomerId = 1;
```

`SET` lists the assignments; `WHERE` decides which rows are touched.
**The `WHERE` is the whole safety story** — see Pitfall 1. After an update
(or insert/delete) the function `changes()` tells you how many rows were
actually affected:

```sql
SELECT changes();
```

If `changes()` is 0, your `WHERE` matched nothing; if it's more than you
expected, your `WHERE` was too broad.

### 1.3 DELETE — removing rows

```sql
DELETE FROM Track
WHERE  TrackId = 123;
```

Same shape, same warning: a `DELETE` with no `WHERE` deletes **every row in
the table**. And in a table that references another (like `InvoiceLine`
referring to `Invoice`), you must delete the *child* rows before the
*parent* row, or the database refuses.

### 1.4 Transactions — the all-or-nothing unit

A **transaction** groups statements so they apply together or not at all:

```sql
BEGIN;          -- start: nothing in between is permanent yet
-- ... writes ...
COMMIT;         -- make it permanent (all of it)
--  or
ROLLBACK;       -- undo it (none of it)
```

- `BEGIN` opens the transaction.
- `COMMIT` makes everything since `BEGIN` permanent.
- `ROLLBACK` throws it all away, as if it never happened.

Between `BEGIN` and `COMMIT`, your changes are visible *to you* (you can
query them), but if you `ROLLBACK`, or if something fails, the database
reverts to exactly the state it was in before `BEGIN`.

Why this matters beyond accidents: a business operation that spans several
tables must be atomic, or you can end up with half-finished states.
"Move an invoice from customer A to B" touches two tables — if the first
write succeeds and the second fails, you've corrupted both. One transaction
makes that impossible.

### 1.5 CREATE TABLE — briefly

You've been using tables all along; here's what making one looks like.
Full schema design is Lesson 09 — this is just enough to write a first
table:

```sql
CREATE TABLE AuditLog (
    LogId      INTEGER PRIMARY KEY,   -- auto-assigned row number
    What       TEXT,
    WhenHappened TEXT
);
```

`INTEGER PRIMARY KEY` in SQLite is special: it auto-increments (1, 2, 3,
…) — you never supply a value for it. Other column types you'll meet:
`TEXT`, `NUMERIC`/`REAL`, `INTEGER`, `DATETIME` (stored as text).

## 2. Worked examples

(All in the Jasper database session.)

### Example 1 — the first INSERT

Goal: add an artist and find out what id SQLite gave it.

```sql
INSERT INTO Artist (Name)
VALUES ('The Course Test Band');

SELECT last_insert_rowid();
SELECT COUNT(*) FROM Artist;
```

```
last_insert_rowid()
-------------------
276

COUNT(*)
--------
276
```

The table had 275 artists; the new one got id 276. The row is live
immediately — no `COMMIT` needed, because without a `BEGIN`, SQLite
autocommits every statement.

### Example 2 — several rows at once

```sql
INSERT INTO Artist (Name)
VALUES ('Second Test Artist'),
       ('Third Test Artist');

SELECT COUNT(*) FROM Artist;
```

```
COUNT(*)
--------
278
```

Two statements' worth of rows in one statement. One transaction, one
atomic step.

### Example 3 — UPDATE with a WHERE, and what `changes()` proved

Goal: move every Canadian customer to Vancouver. From here until the end
of the examples we stay inside **one open transaction**, so everything we
do can still be undone:

```sql
BEGIN;

UPDATE Customer
SET    City = 'Vancouver'
WHERE  Country = 'Canada';

SELECT changes();
```

```
changes()
---------
8
```

Then check:

```sql
SELECT City, COUNT(*)
FROM   Customer
WHERE  Country = 'Canada'
GROUP  BY City;
```

```
City         COUNT(*)
-----------  --------
Vancouver    8
```

Canada has 8 customers, one per city; the `WHERE` narrowed the update to
exactly those 8, and `changes()` confirmed it. (The `GROUP BY City` and
`COUNT(*)` here are a small peek at Lesson 04 — they're just making the
result readable; you could also list the rows and count by eye.) We'll roll
this back in Example 5.

### Example 4 — the UPDATE with no WHERE

Goal: none — demonstration only. We're still inside the transaction opened
in Example 3:

```sql
UPDATE Customer SET City = 'Nowhere';     -- no WHERE!
SELECT changes();
```

```
changes()
---------
59
```

All 59 customers, in one statement, now live in "Nowhere". This is the
single most dangerous thing in SQL, and it took one missing line. The fix
is the next example.

### Example 5 — ROLLBACK: undoing Example 4 (and 3)

Still inside the transaction we opened in Example 3:

```sql
ROLLBACK;

SELECT City FROM Customer WHERE CustomerId = 1;
```

```
City
---------------------
São José dos Campos
```

The `ROLLBACK` erased *everything* since `BEGIN` — including the Vancouver
update from Example 3, which was in the same open transaction. Customer 1
is back in São José dos Campos, exactly as before. Nothing to undo manually;
the database just… didn't keep it.

**Check for yourself.** Run this:

```sql
SELECT City FROM Customer
WHERE  Country = 'Canada'
ORDER  BY City;
```

Expected output (the original 8 cities):

```
City
-----------
Edmonton
Halifax
Montréal
Ottawa
Toronto
Vancouver
Winnipeg
Yellowknife
```

One of those rows says **Vancouver** — and that's fine. Do not conclude
the rollback failed. Customer 15 was *already* in Vancouver in the
original data (Canada's 8 customers lived in 8 different cities). The
rollback restored exactly the original state; nothing from the two UPDATEs
survived. If your output differs from the list above, *that* would be the
problem — go back to Example 3 and check you were inside the transaction
when you ran the updates.

(If you had run Example 3 *without* the `BEGIN` — i.e. autocommitted — the
`ROLLBACK` in this example would have had nothing to roll back. That's the
whole point of opening a transaction *before* the writes you want to be
undoable.)

For the next examples, reload a clean database copy, so
we're not carrying any state forward:

### Example 6 — DELETE, in the right order

Goal: remove invoice 10 — but its 6 line items reference it, so they go
first.

```sql
SELECT COUNT(*) FROM Invoice    WHERE InvoiceId = 10;   -- 1
SELECT COUNT(*) FROM InvoiceLine WHERE InvoiceId = 10;  -- 6

BEGIN;
DELETE FROM InvoiceLine WHERE InvoiceId = 10;
DELETE FROM Invoice     WHERE InvoiceId = 10;
COMMIT;

SELECT COUNT(*) FROM Invoice    WHERE InvoiceId = 10;   -- 0
SELECT COUNT(*) FROM InvoiceLine WHERE InvoiceId = 10;  -- 0
```

The child table (`InvoiceLine`) is emptied first; then the parent row is
free to go. Delete parent-first (with foreign keys enforced) and the
second statement fails with `FOREIGN KEY constraint failed` — leaving you
with a half-deleted mess unless you're in a transaction (and then you
`ROLLBACK`).

### Example 7 — a transaction spanning two tables

Goal: raise invoice 2's total and record a marker artist, as one unit.

```sql
BEGIN;
UPDATE  Invoice SET Total = 99.99 WHERE InvoiceId = 2;
INSERT  INTO Artist (Name) VALUES ('Txn Artist');
COMMIT;

SELECT Total FROM Invoice WHERE InvoiceId = 2;
SELECT COUNT(*) FROM Artist WHERE Name = 'Txn Artist';
```

```
Total
-----
99.99

COUNT(*)
--------
1
```

Both writes stand or fall together. Had the `INSERT` failed, the `COMMIT`
would never happen — and a `ROLLBACK` would have restored the old total
*and* removed the artist, keeping the two tables consistent.

### Example 8 — your first table

```sql
CREATE TABLE IF NOT EXISTS AuditLog (
    LogId        INTEGER PRIMARY KEY,
    What         TEXT,
    WhenHappened TEXT
);

INSERT INTO AuditLog (What, WhenHappened)
VALUES ('first audit entry', '2026-08-27');

SELECT * FROM AuditLog;
```

```
LogId  What              WhenHappened
-----  ----------------- ------------
1      first audit entry 2026-08-27
```

`LogId` was never specified — `INTEGER PRIMARY KEY` auto-filled it with 1.
The playground's schema panel shows exactly what was created.

### Example 9 — what keeps a bad INSERT out

Goal: reference an artist that doesn't exist.

```sql
PRAGMA foreign_keys = ON;

INSERT INTO Album (Title, ArtistId)
VALUES ('Phantom Album', 9999);
```

```
Error: FOREIGN KEY constraint failed
```

No row created. The database checked that `ArtistId 9999` exists in
`Artist` and refused. (That `PRAGMA` line is doing real work — see
Pitfall 3. And note the statement failed *cleanly*: if you'd been in a
transaction, a `ROLLBACK` would restore everything else you'd done in it.)

## 3. Your turn

All in the Jasper database session. Reload `data/chinook.db` first so you start
from the same state as the examples.

1. Insert a new artist called "Your Band Name Here". Show its id.
2. Insert two new genres (ids 26 and 27 — supply them yourself this time:
   `INSERT INTO Genre (GenreId, Name) VALUES …`).
3. Update customer 2's phone number to '555-0100'. Show `changes()`.
4. Delete playlist 18. (You'll need its `PlaylistTrack` rows too — look up
   the ids with a `SELECT` first.)
5. Inside one transaction: rename the genre named "Rock" to "Rock (renamed)",
   then `ROLLBACK`. Show the genre name before, during, and after.
6. (stretch) Create a table `ScratchNote (NoteId INTEGER PRIMARY KEY,
   Note TEXT)`, insert three notes, list them.

## 4. Quiz

Reload `data/chinook.db` before starting so the expected outputs below match
yours. Each question is independent; answer keys in `answers.md`.

1. Insert an artist named "Quiz New Artist". Show its id and name.
2. Change customer 5's city to "Montreal". Show the city before and after.
3. Delete invoice 10 and its line items (in the safe order). Show the
   counts before and after.
4. Inside a transaction, delete track 1. Then `ROLLBACK`. Show the track
   count after the delete and after the rollback.
5. In one transaction: set invoice 2's total to 99.99 **and** insert an
   artist named "Txn Artist". `COMMIT`. Show both results.
6. (stretch) Create the `AuditLog` table from Example 8 (use
   `CREATE TABLE IF NOT EXISTS`), insert a row, and show it.

## 5. Pitfalls

**Pitfall 1 — `UPDATE`/`DELETE` without `WHERE`.**
They run. They affect every row. There is no confirmation prompt. Habit:
write the `WHERE` first, and run a `SELECT` with the same `WHERE` before
the write to see what you're about to touch. After the write, check
`changes()` — a surprising number means your filter was wrong, and you're
still in time for a `ROLLBACK` if you were in a transaction.

**Pitfall 2 — INSERT columns and values out of sync.**

```sql
PRAGMA foreign_keys = OFF;

INSERT INTO Album (Title, ArtistId)
VALUES (42, 'Some Title');
```

SQLite stores 42 as the title and `'Some Title'`… into an integer column.
It's legal, silent, and corrupting. The column list and the value list must
match position by position — read yours out loud before running.

**Pitfall 3 — SQLite does not enforce foreign keys by default.**
Off the shelf, a fresh SQLite connection enforces *no* foreign keys — you
can insert `ArtistId 9999` happily. Every session needs
`PRAGMA foreign_keys = ON;` (it doesn't persist across connections).
The playground does not set it for you. This is a SQLite quirk; PostgreSQL, MySQL,
and SQL Server enforce FKs always.

**Pitfall 4 — "I'll undo it" doesn't exist outside a transaction.**
Outside an explicit transaction, each statement commits immediately. A
`DELETE` you just ran is gone — the only undo is reloading the original file
(or a backup). The discipline: *open the
`BEGIN` before the first write you're unsure about*. If you never `BEGIN`,
you can never `ROLLBACK`.

**Pitfall 5 — Deleting parents before children.**
`DELETE FROM Invoice WHERE …` fails (with FKs on) while `InvoiceLine` rows
still point at it. Children first, parents second. Same order matters for
`UPDATE`s that change a referenced key.

**Pitfall 6 — Trusting `last_insert_rowid()` across sessions.**
It returns the id of the last insert *in this connection*. Fine for the
row you just added; meaningless for "who's the latest artist overall" —
for that use `SELECT ArtistId FROM Artist ORDER BY ArtistId DESC LIMIT 1`.

## 6. Recap

- `INSERT INTO t (cols) VALUES (vals)` — add rows; multiple value lists in
  one statement; `last_insert_rowid()` for the assigned key.
- `UPDATE t SET col = … WHERE …` — the `WHERE` is the safety; `changes()`
  tells you what actually happened.
- `DELETE FROM t WHERE …` — no `WHERE` = empty table. Children before
  parents.
- `BEGIN … COMMIT` makes a group of writes permanent together; `BEGIN …
  ROLLBACK` makes none of them happen at all.
- SQLite commits statements outside an explicit transaction; the transaction
  is the only SQL-level undo.
- `CREATE TABLE` with `INTEGER PRIMARY KEY` gives you auto-numbered keys.
- SQLite FKs need `PRAGMA foreign_keys = ON;` each session.
- Work in Jasper's in-memory copy; the course DB stays pristine.

## 7. Look ahead

Lesson 04 turns your one-row-at-a-time thinking into **groups**: `COUNT`,
`SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY`, and the difference between `WHERE`
(filter rows first) and `HAVING` (filter groups after). It's the lesson
where "how many albums per artist?" becomes a two-line query.
