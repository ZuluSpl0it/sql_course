# Lesson 09 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

### T1 — `Invoice`'s declared types vs. `typeof()`

```sql
PRAGMA table_info(Invoice);
```
declares `InvoiceDate DATETIME` and `Total NUMERIC(10,2)`. Against a real row:
```sql
SELECT typeof(InvoiceDate), typeof(Total) FROM Invoice LIMIT 1;
```
```
typeof(InvoiceDate)|typeof(Total)
text|real
```
`DATETIME` → TEXT affinity (the value is the string `'2021-01-01 00:00:00'`); `NUMERIC(10,2)` → NUMERIC affinity, which stored the decimal `1.98` as `REAL`.

### T2 — a table with all five constraint kinds

```sql
CREATE TABLE Feedback (
  FeedbackId  INTEGER PRIMARY KEY,
  Source      TEXT NOT NULL,
  Score       NUMERIC CHECK (Score BETWEEN 1 AND 5),
  Handle      TEXT UNIQUE,
  CustomerRef INTEGER REFERENCES Customer(CustomerId)
);
INSERT INTO Feedback (Source, Score, Handle, CustomerRef) VALUES ('web', 4, 'h1', 1);
```
The five violations, and the five errors they produce:
```
-- duplicate UNIQUE
INSERT INTO Feedback (Source, Score, Handle, CustomerRef) VALUES ('web', 4, 'h1', 2);
--   Error: UNIQUE constraint failed: Feedback.Handle

-- NULL into NOT NULL
INSERT INTO Feedback (Source, Score, Handle, CustomerRef) VALUES (NULL, 4, 'h2', 2);
--   Error: NOT NULL constraint failed: Feedback.Source

-- out of CHECK range
INSERT INTO Feedback (Source, Score, Handle, CustomerRef) VALUES ('web', 9, 'h3', 2);
--   Error: CHECK constraint failed: Feedback

-- bad foreign key, with the pragma ON in this session
PRAGMA foreign_keys = ON;
INSERT INTO Feedback (Source, Score, Handle, CustomerRef) VALUES ('web', 4, 'h4', 999);
--   Error: FOREIGN KEY constraint failed

-- the primary key: two rows can't share a FeedbackId
INSERT INTO Feedback (FeedbackId, Source, Score, Handle, CustomerRef) VALUES (1, 'web', 4, 'h5', 2);
--   Error: UNIQUE constraint failed: Feedback.FeedbackId
```
Note the `PRIMARY KEY` failure is reported as a `UNIQUE` failure on that column — an `INTEGER PRIMARY KEY` is unique *and* the rowid, and the uniqueness check is what fires.

### T3 — rename a column

```sql
ALTER TABLE Feedback RENAME COLUMN Source TO FromWhere;
PRAGMA table_info(Feedback);
```
The `table_info` output now shows the column as `FromWhere` (`TEXT`, notnull 1) — and any index on `Source` would have been rewritten too, as in Example 8.

### T4 — read the FK back, then trip it

```sql
PRAGMA foreign_key_list(Feedback);
```
```
id|seq|table|from|to|on_update|on_delete|match
0|0|Customer|CustomerRef|CustomerId|NO ACTION|NO ACTION|NONE
```
With `PRAGMA foreign_keys = ON;` in the session, inserting `CustomerRef = 999` fails with `FOREIGN KEY constraint failed`. **Without** the pragma, the exact same insert succeeds silently — the FK clause is inert. That one-line pragma is the entire difference.

### T5 — `EXPLAIN QUERY PLAN` on `Employee(Country)`

```sql
EXPLAIN QUERY PLAN SELECT * FROM Employee WHERE Country = 'Brazil';
```
```
QUERY PLAN
`--SCAN TABLE Employee
```
```sql
CREATE INDEX idx_emp_country ON Employee(Country);
EXPLAIN QUERY PLAN SELECT * FROM Employee WHERE Country = 'Brazil';
```
```
QUERY PLAN
`--SEARCH TABLE Employee USING INDEX idx_emp_country (Country=?)
```
Brazil matches **zero** of the eight employees in Chinook; all eight have `Country = 'Canada'`. The query is still useful here because the same query changes from `SCAN` to `SEARCH … USING INDEX`. (It's not `COVERING` because you `SELECT *` — the index finds rows, then the table supplies the other columns. On an 8-row table the index saves nothing measurable; the lesson is the plan shape. `DROP INDEX idx_emp_country;` when you're done.)

### T6 — (stretch) list every index; which can't you drop?

```sql
SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' ORDER BY name;
```
That's the 12 you saw in Example 1: eleven `IFK_` indexes (all droppable — try `DROP INDEX IFK_TrackAlbumId;` and re-create it if you want the scratch clean) plus `sqlite_autoindex_PlaylistTrack_1`, which `DROP INDEX` refuses because it enforces `PlaylistTrack`'s `UNIQUE(PlaylistId, TrackId)` — you'd have to rebuild the table to get rid of it.
