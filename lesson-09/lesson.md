# Lesson 09: Schema & Constraints

You've been *reading* Chinook for eight lessons. This lesson opens the hood: what a `CREATE TABLE` actually declares, why SQLite's declared types are a promise rather than a rule, and how the five constraint words (`PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`) are enforced — and when they *aren't*. You'll also learn what `ALTER TABLE` can and can't do in SQLite 3.31, how to read the schema's own data in `sqlite_master`, and what `EXPLAIN QUERY PLAN` shows before and after you add an index — the bridge into Lesson 10's performance work.

**This lesson writes.** Open Jasper SQL Playground and load `data/chinook.db`.
Work in its in-memory
copy; reload the original file whenever you need a clean session. The real
database stays untouched. The last example tears down everything it creates.

---

## 1. The concept

### The five storage classes

SQLite doesn't have a type per column the way PostgreSQL does. It has **five storage classes**, and every value in the database is exactly one of them:

- **`NULL`** — the absence of a value.
- **`INTEGER`** — a signed integer, 1 to 8 bytes.
- **`REAL`** — an 8-byte IEEE floating-point number.
- **`TEXT`** — a character string, stored as UTF-8.
- **`BLOB`** — a string of bytes, stored exactly as given.

The function `typeof(x)` names the storage class of a value:

```sql
SELECT typeof(NULL), typeof(1), typeof(1.5), typeof('hi'), typeof(X'00');
```

```
typeof(NULL)  typeof(1)  typeof(1.5)  typeof('hi')  typeof(X'00')
------------  ---------  -----------  ------------  -------------
null          integer    real         text          blob
```


Five values, five classes — the entire type system of SQLite, in one row.

### Declared types vs. storage: affinity

When you write `CREATE TABLE`, you can put a *type name* on each column — but SQLite only uses it to pick one of four **affinities** (`INTEGER`, `TEXT`, `REAL`, `NUMERIC`, or none). The affinity is a *conversion rule*: on `INSERT`, SQLite tries to coerce your value toward the declared type, **without ever losing information** (it never truncates, rounds, or clips). What actually gets stored is still one of the five classes, and `typeof()` tells you which.

Chinook was exported from SQL Server, so its DDL says things like `NVARCHAR(200)` and `NUMERIC(10,2)`. SQLite reads those names only to pick an **affinity** — a conversion rule applied on `INSERT` — and what actually gets stored is still one of the five classes: `NVARCHAR(200)` → `TEXT`, `NUMERIC(10,2)` → `REAL` (or `INTEGER` for whole numbers), and `DATETIME` → `TEXT` (Chinook's dates are strings like `'2021-01-01 00:00:00'`, parsed by the date functions from Lesson 08). The declared name is a *hint to other tools*; the storage class is the truth. Example 2 proves it on `Track`.

### The five constraint words

| word | what it promises | enforced by |
|---|---|---|
| `PRIMARY KEY` | this column uniquely identifies the row | always (it's the rowid) |
| `NOT NULL` | this column must have a value | always |
| `UNIQUE` | no two rows share this value | always |
| `CHECK (…)` | an expression must be true | always |
| `FOREIGN KEY` | this value must exist in another table | **only if `PRAGMA foreign_keys = ON`** |

That last row is the trap of this lesson: the first four are part of the storage engine and are always on. The fifth is a *feature you have to switch on, per connection, or it doesn't exist.* Example 6 proves it.

### `sqlite_master`: the schema is data

Every table, index, view, and trigger in a SQLite database has a row in a hidden table called `sqlite_master`. Its `name` is the object, its `type` is one of `table`/`index`/`view`/`trigger`, and its `sql` column is the exact `CREATE …` statement. **You can `SELECT` it like any other table** — that's how you discover a schema you didn't write (and it's how this course audits its own lessons).

---

## 2. Worked examples

### Example 1 — the map: what's in the database?

Before touching anything, look at what's here. `sqlite_master` lists every object; filter out the `sqlite_%` internal objects and you get Chinook's real schema:

```sql
SELECT name, type FROM sqlite_master
WHERE  name NOT LIKE 'sqlite_%'
ORDER  BY type, name;
```

```
name                         type
---------------------------  -----
IFK_AlbumArtistId            index
IFK_CustomerSupportRepId     index
IFK_EmployeeReportsTo        index
IFK_InvoiceCustomerId        index
IFK_InvoiceLineInvoiceId     index
IFK_InvoiceLineTrackId       index
IFK_PlaylistTrackPlaylistId  index
IFK_PlaylistTrackTrackId     index
IFK_TrackAlbumId             index
IFK_TrackGenreId             index
IFK_TrackMediaTypeId         index
Album                        table
Artist                       table
Customer                     table
Employee                     table
Genre                        table
Invoice                      table
InvoiceLine                  table
MediaType                    table
Playlist                     table
PlaylistTrack                table
Track                        table
```


Eleven tables and eleven indexes — and **zero views**. Every index name starts with `IFK_` ("index-foreign-key"): Chinook's exporter created an index on each foreign-key column. (A twelfth object exists but the filter hides it: `sqlite_autoindex_PlaylistTrack_1`, SQLite's own index enforcing `PlaylistTrack`'s `UNIQUE(PlaylistId, TrackId)` — you'll meet it in Practical Exercise T6, where it's the one index you can't `DROP`.)

### Example 2 — declared types are a promise, not a rule

The DDL of `Track` (from `sqlite_master.sql`) declares `NVARCHAR(200)` for `Name` and `NUMERIC(10,2)` for `UnitPrice`. Read those declared types straight from the schema, then ask `typeof()` what the same columns actually store — the declared name and the stored class disagree, and that's the whole story of type affinity:

```sql
PRAGMA table_info(Track);
```

```
cid  name          type           notnull  dflt_value  pk
---  ------------  -------------  -------  ----------  --
0    TrackId       INTEGER        1                    1
1    Name          NVARCHAR(200)  1                    0
2    AlbumId       INTEGER        0                    0
3    MediaTypeId   INTEGER        1                    0
4    GenreId       INTEGER        0                    0
5    Composer      NVARCHAR(220)  0                    0
6    Milliseconds  INTEGER        1                    0
7    Bytes         INTEGER        0                    0
8    UnitPrice     NUMERIC(10,2)  1                    0
```


```sql
SELECT typeof(Name)      FROM Track  LIMIT 1;
SELECT typeof(Milliseconds) FROM Track  LIMIT 1;
SELECT typeof(UnitPrice)   FROM Track  LIMIT 1;
SELECT typeof(InvoiceDate) FROM Invoice LIMIT 1;
SELECT typeof(Total)       FROM Invoice LIMIT 1;
```

```
typeof(Name)
------------
text

typeof(Milliseconds)
--------------------
integer

typeof(UnitPrice)
-----------------
real

typeof(InvoiceDate)
-------------------
text

typeof(Total)
-------------
real
```


`NVARCHAR(200)` → `TEXT`. `NUMERIC(10,2)` → `real` (for a value like `1.98`). `DATETIME` → `text`. The declared type tells SQLite *how to try to convert on insert*; the storage class is what survives. When in doubt, `typeof()` settles it.

### Example 3 — affinity in action

Create a small table declaring one column of each affinity, then insert values that *don't match* the declared type. Watch what gets stored:

```sql
CREATE TABLE AffinityDemo (I INTEGER, T TEXT, N NUMERIC(10,2), R REAL);
INSERT INTO AffinityDemo VALUES (1.5, 7, 3, 4);
INSERT INTO AffinityDemo VALUES (2.0, '8', '2', 5.5);
SELECT I, T, N, R, typeof(I), typeof(T), typeof(N), typeof(R) FROM AffinityDemo ORDER BY I;
```

```
I    T  N  R    typeof(I)  typeof(T)  typeof(N)  typeof(R)
---  -  -  ---  ---------  ---------  ---------  ---------
1.5  7  3  4.0  real       text       integer    real
2    8  2  5.5  integer    text       integer    real
```


Row 1: `1.5` into an `INTEGER` column stays `REAL` (converting it would lose the `.5` — affinity never destroys information); `7` into a `TEXT` column stays the string `7` → stored as… wait, it prints `7` but `typeof` says `text`. `3` into `NUMERIC(10,2)` becomes the integer `3`; `4` becomes `4.0` in the `REAL` column. Row 2: `2.0` is an exact integer in value, so `INTEGER` affinity converts it to `2`; `'8'` and `'2'` are text that *looks like* a number, and `NUMERIC` affinity converts them to `8` and `2`. The rule to remember: **INTEGER affinity keeps exact integers and converts exact-looking reals; TEXT affinity converts nothing; NUMERIC and REAL convert whenever it's lossless.

### Example 4 — `rowid`: the row number underneath every table

Every table without an `INTEGER PRIMARY KEY` has a hidden row number, the `rowid` (also `_rowid_` / `oid`). And an `INTEGER PRIMARY KEY` column *is* the rowid — an alias, not a separate thing. Make one and look:

```sql
CREATE TABLE Roster (Id INTEGER PRIMARY KEY, Name TEXT);
INSERT INTO Roster (Name) VALUES ('a');
INSERT INTO Roster (Name) VALUES ('b');
INSERT INTO Roster (Id, Name) VALUES (100, 'c');
INSERT INTO Roster (Name) VALUES ('d');
SELECT Id, Name, rowid FROM Roster ORDER BY Id;
```

```
Id   Name  Id
---  ----  ---
1    a     1
2    b     2
100  c     100
101  d     101
```


`a` and `b` got rowids 1 and 2. The explicit `100` in row three made SQLite set both the `Id` and the `rowid` to 100. And `d` — the next *auto*-numbered row — got **101**, not 3: the rowid allocator always moves to one past the maximum. This is why deleting row 100 and then inserting a new row gives you 101 again, and why an `INTEGER PRIMARY KEY` column is the cheapest possible key: it *is* the rowid.

### Example 5 — `NOT NULL`, `UNIQUE`, `CHECK` — three constraints that always work

A small review table with one of each (plus a primary key), and one valid row:

```sql
CREATE TABLE Review (
  ReviewId INTEGER PRIMARY KEY,
  Title    TEXT NOT NULL,
  Rating   NUMERIC CHECK (Rating BETWEEN 0 AND 10),
  Code     TEXT UNIQUE
);
INSERT INTO Review (Title, Rating, Code) VALUES ('ok', 7, 'A1');
SELECT * FROM Review;
```

```
ReviewId  Title  Rating  Code
--------  -----  ------  ----
1         ok     7       A1
```


```sql
INSERT INTO Review (Title, Rating, Code) VALUES ('dup', 1, 'A1');
```

```
Error: UNIQUE constraint failed: Review.Code
```


```sql
INSERT INTO Review (Title, Rating, Code) VALUES (NULL, 1, 'A2');
```

```
Error: NOT NULL constraint failed: Review.Title
```


```sql
INSERT INTO Review (Title, Rating, Code) VALUES ('bad', 11, 'A3');
```

```
Error: CHECK constraint failed: Review
```


Three different violations, three different errors, all *always* enforced because they're part of the storage engine. The `UNIQUE` and `NOT NULL` messages name the column; the `CHECK` message names the table (the `CHECK` expression itself can't be named, so SQLite reports the table). And note what did **not** happen: the three failed `INSERT`s changed nothing — the table still holds only `('ok', 7, 'A1')`, because each rejected statement rolled back its own partial effect.

### Example 6 — the foreign-key pragma: the one constraint you must switch on

Now the trap. `PRAGMA foreign_keys` reports whether foreign-key enforcement is on for *this connection*. On a fresh connection it's always off:

```sql
PRAGMA foreign_keys;
```

```
foreign_keys
------------
0
```


```sql
PRAGMA foreign_keys = ON;
```



```sql
INSERT INTO Album (Title, ArtistId) VALUES ('Phantom', 9999);
```

```
Error: FOREIGN KEY constraint failed
```



```sql
INSERT INTO Album (Title, ArtistId) VALUES ('Real', 1);
SELECT COUNT(*) FROM Album WHERE Title = 'Real';
```

```
COUNT(*)
--------
1
```


Read that again: **a `FOREIGN KEY` clause in the DDL does nothing until you turn the pragma on, and it resets to off every time you open a new connection.** Chinook's DDL is full of `FOREIGN KEY` lines; in a default browser session, none of them are enforced. The bad `ArtistId = 9999` insert was rejected only because the `PRAGMA foreign_keys = ON` in the *same session* was still in effect. Reload the database in a new playground session and you can insert `9999` again — silently. The good insert (a real `ArtistId = 1`) is accepted in either case. **If you write any lesson, script, or app that inserts into a table with foreign keys, the first statement must be `PRAGMA foreign_keys = ON`** — there is no database-level setting, and no way to make it the default.

### Example 7 — reading the foreign-key map

A foreign-key clause is stored in the schema, and there's a pragma that reads it back. `Track` references three tables; `PRAGMA foreign_key_list(Track)` gives each as a row (`from` → `to` is this column → the referenced column):

```sql
PRAGMA foreign_key_list(Track);
```

```
id  seq  table      from         to           on_update  on_delete  match
--  ---  ---------  -----------  -----------  ---------  ---------  -----
0   0    MediaType  MediaTypeId  MediaTypeId  NO ACTION  NO ACTION  NONE
1   0    Genre      GenreId      GenreId      NO ACTION  NO ACTION  NONE
2   0    Album      AlbumId      AlbumId      NO ACTION  NO ACTION  NONE
```


```sql
SELECT sql FROM sqlite_master WHERE name = 'IFK_TrackAlbumId';
```

```
sql
------------------------------------------------------
CREATE INDEX [IFK_TrackAlbumId] ON [Track] ([AlbumId])
```


This is how you discover a relationship you didn't create — and it's the same `foreign_key_list` you'll reach for when you read the Northwind schema in the final exam. The second query shows *why* Chinook ships an `IFK_` index on each of these columns: without it, every `JOIN` through the foreign key would be a full scan of the referenced table.

### Example 8 — what `ALTER TABLE` can do

SQLite 3.31 is deliberately conservative about changing a table after it's created. What it *can* do: add a column (existing rows get the default), rename a column (indexes and foreign keys that reference it follow), and rename the table. Add a column with a default:

```sql
ALTER TABLE Roster ADD COLUMN Note TEXT DEFAULT 'n/a';
SELECT * FROM Roster ORDER BY Id;
```

```
Id   Name  Note
---  ----  ----
1    a     n/a
2    b     n/a
100  c     n/a
101  d     n/a
```


```sql
CREATE INDEX idx_roster_name ON Roster(Name);
ALTER TABLE Roster RENAME COLUMN Name TO ArtistName;
SELECT sql FROM sqlite_master WHERE name = 'idx_roster_name';
```

```
sql
--------------------------------------------------
CREATE INDEX idx_roster_name ON Roster(ArtistName)
```


The `ADD COLUMN` filled the four existing rows with the default `'n/a'` — you can't `ALTER` the old rows themselves. Then the rename: create an index on `Name`, rename the column, and the index's own `sql` is rewritten to the new name. `RENAME COLUMN` is the safe kind of edit: nothing that *points at* the column is left dangling.

### Example 9 — what `ALTER TABLE` cannot do (3.31)

The other side of the story. These all fail, with exactly these errors:

```sql
ALTER TABLE Roster ADD COLUMN U TEXT UNIQUE;
```

```
Error: Cannot add a UNIQUE column
```


```sql
ALTER TABLE Roster ADD COLUMN P INTEGER PRIMARY KEY;
```

```
Error: Cannot add a PRIMARY KEY column
```


```sql
ALTER TABLE Roster ADD CONSTRAINT u2 UNIQUE (ArtistName);
```

```
Error: near "CONSTRAINT": syntax error
```


No adding `UNIQUE` or `PRIMARY KEY` columns, and no `ADD CONSTRAINT` at all (there's no syntax for it). The escape hatch is the classic one: **create a new table with the constraint you want, `INSERT … SELECT` the rows across, drop the old table, rename the new one.** (And `DROP COLUMN` doesn't exist yet in 3.31 at all — that arrived in 3.35.) When a schema change you need isn't in this list, it's a rebuild, not an alter.

### Example 10 — the one `ALTER` the textbooks get wrong

One thing *is* possible that many references claim isn't: adding a column that carries a foreign key. This works in 3.31:

```sql
ALTER TABLE Roster ADD COLUMN RefArtist INTEGER REFERENCES Artist(ArtistId);
PRAGMA foreign_key_list(Roster);
```

```
id  seq  table   from       to        on_update  on_delete  match
--  ---  ------  ---------  --------  ---------  ---------  -----
0   0    Artist  RefArtist  ArtistId  NO ACTION  NO ACTION  NONE
```


```sql
CREATE TABLE RenDemo (a TEXT);
INSERT INTO RenDemo VALUES ('x');
ALTER TABLE RenDemo RENAME TO RenDemo2;
SELECT * FROM RenDemo2;
```

```
a
-
x
```


`ADD COLUMN … REFERENCES …` adds a real, working foreign key — `PRAGMA foreign_key_list` now reports `Roster.RefArtist → Artist.ArtistId`. (With the pragma on, a bad value in `RefArtist` would fail exactly like Example 6.) So the accurate 3.31 list of `ALTER TABLE` limits is: **no adding `UNIQUE`, no adding `PRIMARY KEY`, no `ADD CONSTRAINT`, no `DROP COLUMN`** — but adding a column with a `REFERENCES` clause is fine. The second block shows the other supported rename: `RENAME TABLE`, after which the data (and any indexes on the table) travel with the new name.

### Example 11 — transactions cover `CREATE` and `DROP` too

Lesson 03 made `BEGIN … ROLLBACK` undo your `INSERT`/`UPDATE`/`DELETE`. DDL is in the same transaction too — a `CREATE TABLE` inside a rolled-back block never happens:

```sql
BEGIN;
INSERT INTO Track (Name, AlbumId, MediaTypeId, Milliseconds, UnitPrice)
VALUES ('Txn Track', 1, 1, 100, 0.99);
SELECT COUNT(*) FROM Track;
CREATE TABLE TxnTable (x INTEGER);
ROLLBACK;
SELECT COUNT(*) FROM Track;
SELECT COUNT(*) FROM sqlite_master WHERE name = 'TxnTable';
```

```
COUNT(*)
--------
3504

COUNT(*)
--------
3503

COUNT(*)
--------
0
```



```sql
BEGIN;
BEGIN;
```

```
Error: cannot start a transaction within a transaction
```



During the block, `Track` had 3,504 rows and `TxnTable` existed; after `ROLLBACK`, the insert is gone (3,503) *and* the table is gone (0). And the second block is the lesson-03 rule restated: SQLite allows exactly one open transaction per connection — a nested `BEGIN` is an error, not a savepoint.

### Example 12 — views: a saved query with a name

A `VIEW` is a `SELECT` that the database runs for you every time you query it — a read-only, always-fresh projection. Chinook ships none; make one that counts tracks per genre:

```sql
CREATE VIEW GenreCounts AS
SELECT g.GenreId, g.Name,
       (SELECT COUNT(*) FROM Track t WHERE t.GenreId = g.GenreId) AS track_count
FROM   Genre g
ORDER  BY track_count DESC;
SELECT * FROM GenreCounts LIMIT 3;
SELECT COUNT(*) FROM sqlite_master WHERE type = 'view';
```

```
GenreId  Name   track_count
-------  -----  -----------
1        Rock   1297
7        Latin  579
3        Metal  374

COUNT(*)
--------
1
```


The view prints like a table (top three genres: Rock 1,297, Latin 579, Metal 374), and `sqlite_master` now holds one row of type `view`. You can't `INSERT` into a view (it's read-only), and it stores no data of its own — it's just the saved query, re-run on demand. Views are how you package a join-heavy query that several reports keep re-deriving.

### Example 13 — `EXPLAIN QUERY PLAN`: before and after an index

`EXPLAIN QUERY PLAN` prints the *shape* of the plan without running the query — the bridge into Lesson 10. The same `WHERE` clause, with and without an index on the column:

```sql
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM Customer WHERE Country = 'Germany';
```

```
QUERY PLAN
----------------------
`--SCAN TABLE Customer
```


```sql
CREATE INDEX idx_cust_country ON Customer(Country);
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM Customer WHERE Country = 'Germany';
SELECT COUNT(*) FROM Customer WHERE Country = 'Germany';
DROP INDEX idx_cust_country;
```

```
QUERY PLAN
--------------------------------------------------------------------------
`--SEARCH TABLE Customer USING COVERING INDEX idx_cust_country (Country=?)

COUNT(*)
--------
4
```


```sql
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM Track WHERE Milliseconds > 500000;
```

```
QUERY PLAN
-------------------
`--SCAN TABLE Track
```


```sql
CREATE INDEX idx_track_ms ON Track(Milliseconds);
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM Track WHERE Milliseconds > 500000;
SELECT COUNT(*) FROM Track WHERE Milliseconds > 500000;
DROP INDEX idx_track_ms;
```

```
QUERY PLAN
------------------------------------------------------------------------
`--SEARCH TABLE Track USING COVERING INDEX idx_track_ms (Milliseconds>?)

COUNT(*)
--------
335
```


Before the index: `SCAN TABLE Customer` — read all 59 rows. After: `SEARCH TABLE Customer USING COVERING INDEX idx_cust_country (Country=?)` — jump straight to the matching entries. *Covering* means the index alone answered the question, so SQLite never even touched the table. The same before/after on `Track.Milliseconds` (a 3,503-row table) is where an index starts to earn its keep: 335 tracks run longer than 500,000 ms. You `DROP` each index at the end of its block so the scratch stays clean — and so that when Lesson 10 gets to performance, you'll see `SCAN TABLE` one more time on purpose.

### Example 14 — tear it all down

Every object this lesson created is yours to remove. `DROP VIEW` / `DROP TABLE` each of them, then confirm the in-memory database is back to exactly what you started with:

```sql
DROP VIEW   GenreCounts;
DROP TABLE Roster;
DROP TABLE Review;
DROP TABLE AffinityDemo;
DROP TABLE RenDemo2;
DELETE FROM Album WHERE Title = 'Real' AND ArtistId = 1;
SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'  AND name NOT LIKE 'sqlite_%';
SELECT COUNT(*) FROM sqlite_master WHERE type = 'index'  AND name NOT LIKE 'sqlite_%';
SELECT COUNT(*) FROM sqlite_master WHERE type = 'view';
```

```
COUNT(*)
--------
11

COUNT(*)
--------
11

COUNT(*)
--------
0
```


11 user tables, 11 user indexes (the 12th was `sqlite_autoindex_PlaylistTrack_1`, which stays — it belongs to `PlaylistTrack`'s `UNIQUE` constraint, not to any `CREATE INDEX`), and 0 views: pristine again. **Leave your scratch like this** and the next time you start from it, the outputs in this lesson will reproduce exactly.

---

## 3. Practical Exercises

Work in Jasper SQL Playground against a fresh load of `data/chinook.db` so the
outputs match. Check `answers_practical.md` when you're done.

1. Print the declared schema of `Invoice` with `PRAGMA table_info(Invoice);`. For `Total` and `InvoiceDate`, what does `typeof()` report for a real row — and which affinity does each declared type map to?
2. In the in-memory database, create a table `Feedback` with these columns and **all five constraint kinds present**: `FeedbackId INTEGER PRIMARY KEY`, `Source TEXT NOT NULL`, `Score NUMERIC CHECK (Score BETWEEN 1 AND 5)`, `Handle TEXT UNIQUE`, and `CustomerRef INTEGER REFERENCES Customer(CustomerId)`. Insert one valid row, then try to break each constraint once and note the five different errors.
3. `ALTER TABLE Feedback RENAME COLUMN Source TO FromWhere;` — then confirm with `PRAGMA table_info(Feedback);` that the rename landed.
4. What does `PRAGMA foreign_key_list(Feedback);` return? Now `PRAGMA foreign_keys = ON;` and insert a row with `CustomerRef = 999`. What happens — and what would have happened if you hadn't set the pragma?
5. `EXPLAIN QUERY PLAN` a query that filters `Employee` by `Country = 'Brazil'`, before and after you `CREATE INDEX` on `Employee(Country)`. What changes? (Clean up the index when you're done.)
6. (Stretch) List every object in `sqlite_master` whose `type` is `index`, showing `name` and `tbl_name`. Which of them could you *not* `DROP`, and why?

---

## 4. Quiz

Answer without scrolling up. The key is in `answers_quiz.md`.

1. In one sentence: what is the difference between a column's *declared type* and its *storage class* in SQLite?
2. You open a fresh Jasper database session and `INSERT` a row into
   `InvoiceLine` with a `TrackId` that doesn't exist. It succeeds. Why?
3. `ALTER TABLE t ADD COLUMN c TEXT UNIQUE;` — what's the error, and what's the workaround in 3.31?
4. True or false: a `CREATE TABLE` inside a `BEGIN … ROLLBACK` block leaves an empty table behind.
5. What does `PRAGMA foreign_key_list(Track);` report as `Track`'s three referenced tables, in order?
6. (Stretch) Why can you `DROP INDEX idx_cust_country` but not `DROP INDEX sqlite_autoindex_PlaylistTrack_1`?

---

## 5. Pitfalls

1. **Foreign keys are off unless you say otherwise — every session.** `PRAGMA foreign_keys` is a per-connection setting that defaults to `OFF` and has no database-level default. A schema full of `FOREIGN KEY` clauses enforces nothing in a fresh connection. Make `PRAGMA foreign_keys = ON;` the first line of any script or session that writes to a schema with foreign keys.
2. **Declared type ≠ stored type.** `NVARCHAR(40)`, `DATETIME`, and `NUMERIC(10,2)` are affinities, not types: they store `TEXT`, `TEXT`, and `REAL`/`INTEGER` respectively. Never assume a column's declared name tells you what `typeof()` will return — ask it. (This is also why Chinook's dates sort correctly as text: they're ISO-format strings.)
3. **`ALTER TABLE` is a small vocabulary.** In 3.31 you can `ADD COLUMN` (with a default, and with `REFERENCES`), `RENAME COLUMN`, and `RENAME TABLE`. You cannot add `UNIQUE` or `PRIMARY KEY` columns, there is no `ADD CONSTRAINT`, and `DROP COLUMN` doesn't exist until 3.35. Anything else is a rebuild: new table, `INSERT … SELECT`, drop, rename.
4. **`INTEGER PRIMARY KEY` is the rowid — gaps are normal.** It's an auto-number that always moves to one past the max (Example 4). Deletes create gaps; that's expected, not a bug, and it's why you never *reuse* a deleted id.
5. **One transaction at a time.** A nested `BEGIN` is an error, not a savepoint (Example 11, block 2). If you need nested all-or-nothing units, that's `SAVEPOINT`, which this course deliberately doesn't use — keep to one `BEGIN` and it's a non-issue.
6. **`EXPLAIN QUERY PLAN` says *shape*, not speed.** `SCAN TABLE` vs `SEARCH … USING INDEX` tells you whether an index is available, not how fast the query is. A plan that looks worse can still be faster on a small table (reading 59 rows is cheap). You'll weigh these properly in Lesson 10.

---

## 6. Recap

- SQLite has **five storage classes** — `NULL`, `INTEGER`, `REAL`, `TEXT`, `BLOB` — and `typeof(x)` names whichever one a value is.
- A column's **declared type** only picks an **affinity** (a lossless conversion rule on insert); the stored class is the truth, and Chinook's `NVARCHAR`/`DATETIME`/`NUMERIC(10,2)` store `text`/`text`/`real` or `integer`.
- `NOT NULL`, `UNIQUE`, and `CHECK` are **always enforced**. `FOREIGN KEY` is enforced **only in a connection where `PRAGMA foreign_keys = ON`** — and that resets to off on every new connection.
- The schema is readable data: `sqlite_master` holds every object and its `CREATE` text, and `PRAGMA table_info` / `foreign_key_list` give you structured views of it.
- **`ALTER TABLE` in 3.31**: add a column (with default / `REFERENCES`), rename a column (indexes & FKs follow), rename a table. Nothing else — everything bigger is a rebuild.
- **DDL is transactional**: `BEGIN … ROLLBACK` undoes `CREATE`/`DROP` just like `INSERT`.
- **`EXPLAIN QUERY PLAN`** shows `SCAN TABLE` (read everything) vs `SEARCH … USING (COVERING) INDEX` (jump straight to the match) — the before/after that motivates every index you'll evaluate next.

**Next up — Lesson 10 (Performance & the Capstone):** the schema is under your feet, so now the questions get expensive. You'll read `EXPLAIN QUERY PLAN` like a diagnostic, decide which indexes actually earn their keep (and which just slow the writes), and then put the whole course together in a multi-part report and a graded end-of-course project.
