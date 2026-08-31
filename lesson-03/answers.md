# Lesson 03 — Quiz Answer Key

Attempt `lesson.md` → Quiz before opening this file. **Reload
`data/chinook.db` first** so the outputs match.

Expected outputs were verified against the database as shipped. Compare
**outputs**, not query text.

## Q1 — Insert "Quiz New Artist"; show id and name

```sql
INSERT INTO Artist (Name)
VALUES ('Quiz New Artist');

SELECT ArtistId, Name
FROM   Artist
WHERE  Name = 'Quiz New Artist';
```

```
ArtistId  Name
--------  ---------------
276       Quiz New Artist
```

(276 only if you started from a fresh database with its 275 original
artists — `last_insert_rowid()` returns the same number.)

## Q2 — Change customer 5's city to "Montreal"

Before:

```sql
SELECT City FROM Customer WHERE CustomerId = 5;
```

```
City
------
Prague
```

The update:

```sql
UPDATE Customer
SET    City = 'Montreal'
WHERE  CustomerId = 5;
```

After:

```sql
SELECT City FROM Customer WHERE CustomerId = 5;
```

```
City
--------
Montreal
```

Don't accept an `UPDATE` without the `WHERE` (it would rewrite all 59
cities) or with a `WHERE` that matches more than one row.

## Q3 — Delete invoice 10 and its lines, in the safe order

Before:

```sql
SELECT COUNT(*) FROM Invoice     WHERE InvoiceId = 10;  -- 1
SELECT COUNT(*) FROM InvoiceLine WHERE InvoiceId = 10;  -- 6
```

The deletes (children first):

```sql
BEGIN;
DELETE FROM InvoiceLine WHERE InvoiceId = 10;
DELETE FROM Invoice     WHERE InvoiceId = 10;
COMMIT;
```

After:

```sql
SELECT COUNT(*) FROM Invoice     WHERE InvoiceId = 10;  -- 0
SELECT COUNT(*) FROM InvoiceLine WHERE InvoiceId = 10;  -- 0
```

Accept `BEGIN`/`COMMIT` as optional here (a failed parent delete would
leave orphans, but with a single connection the child-first order works
without a transaction — the transaction is still the better habit).
Don't accept parent-first ordering.

## Q4 — Delete track 1 in a transaction, then ROLLBACK

```sql
BEGIN;
DELETE FROM Track WHERE TrackId = 1;
SELECT COUNT(*) FROM Track;     -- during: 3502
ROLLBACK;
SELECT COUNT(*) FROM Track;     -- after: 3503
```

```
COUNT(*)
--------
3502

COUNT(*)
--------
3503
```

The point is the pair: 3502 inside the transaction, 3503 after rollback.
If a student shows only 3503, they probably never deleted; if only 3502,
they forgot the `ROLLBACK`.

## Q5 — One transaction: invoice 2 total + "Txn Artist"

```sql
BEGIN;
UPDATE Invoice SET Total = 99.99 WHERE InvoiceId = 2;
INSERT INTO Artist (Name) VALUES ('Txn Artist');
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

Both writes must be between one `BEGIN` and one `COMMIT` — that's the
whole point of the question. Accept the INSERT before the UPDATE (order
within the transaction doesn't matter here).

## Q6 (stretch) — AuditLog table

```sql
CREATE TABLE IF NOT EXISTS AuditLog (
    LogId        INTEGER PRIMARY KEY,
    What         TEXT,
    WhenHappened TEXT
);

INSERT INTO AuditLog (What, WhenHappened)
VALUES ('quiz entry', '2026-08-27');

SELECT * FROM AuditLog;
```

```
LogId  What        WhenHappened
-----  ----------  ------------
1      quiz entry  2026-08-27
```

`IF NOT EXISTS` makes the question re-runnable if the student already ran
Example 8. Accept any reasonable note text; the structure (auto-id plus
the two text columns) is what's being tested.

---

## Reference for the "Your Turn" prompts

1. New artist with its id:

```sql
INSERT INTO Artist (Name) VALUES ('Your Band Name Here');
SELECT last_insert_rowid();
```

2. Two genres with explicit ids:

```sql
INSERT INTO Genre (GenreId, Name)
VALUES (26, 'Quiz Genre One'),
       (27, 'Quiz Genre Two');
```

(Ids 26 and 27 are free — the largest existing `GenreId` is 25. Supplying
the `GenreId` yourself is the point: it stops being auto-assigned.)

3. Customer 2's phone, with `changes()`:

```sql
UPDATE Customer SET Phone = '555-0100' WHERE CustomerId = 2;
SELECT changes();
```

```
changes()
---------
1
```

(Customer 2 is Leonie Köhler, original phone `+49 0711 2842222`.)

4. Delete playlist 18 ("On-The-Go 1") and its one track link:

```sql
SELECT COUNT(*) FROM PlaylistTrack WHERE PlaylistId = 18;  -- 1

BEGIN;
DELETE FROM PlaylistTrack WHERE PlaylistId = 18;
DELETE FROM Playlist      WHERE PlaylistId = 18;
COMMIT;

SELECT COUNT(*) FROM Playlist WHERE PlaylistId = 18;       -- 0
```

5. Rename "Rock" inside a transaction, then roll back:

```sql
SELECT Name FROM Genre WHERE GenreId = 1;     -- before:  Rock
BEGIN;
UPDATE Genre SET Name = 'Rock (renamed)' WHERE GenreId = 1;
SELECT Name FROM Genre WHERE GenreId = 1;     -- during:  Rock (renamed)
ROLLBACK;
SELECT Name FROM Genre WHERE GenreId = 1;     -- after:   Rock
```

6. Three notes in `ScratchNote`:

```sql
CREATE TABLE ScratchNote (NoteId INTEGER PRIMARY KEY, Note TEXT);
INSERT INTO ScratchNote (Note)
VALUES ('one'), ('two'), ('three');
SELECT * FROM ScratchNote;
```

```
NoteId  Note
------  -----
1       one
2       two
3       three
```
