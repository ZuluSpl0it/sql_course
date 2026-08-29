# Lesson 05: Joins, Part I

Up to now every query has looked at **one table**. But the interesting
questions live *across* tables: "which albums does AC/DC have, and what
tracks are on them?" "who is each employee's manager?" "how much revenue
does each artist generate?" You can't answer any of those by listing one
table — you have to **connect** the tables. That connection is a **join**,
and this lesson teaches the two workhorses: `INNER JOIN` and `LEFT JOIN`,
plus a join to a table's own history (a **self join**).

**No scratch copy needed.** This lesson only reads.

---

## 1. The concept

### The problem with one table

Look at a row from `Track`:

```sql
SELECT TrackId, Name, AlbumId FROM Track LIMIT 3;
```

```
TrackId  Name                                     AlbumId
-------  ---------------------------------------  -------
1        For Those About To Rock (We Salute You)  1
2        Balls to the Wall                        2
3        Fast As a Shark                          3
```

The track knows it belongs to album `1` — but `1` is just a number. To find
the album's *title* you need the `Album` table, which has
`AlbumId → Title`. The `AlbumId` in `Track` is a **foreign key**: a column
that points at the **primary key** of another table. A **primary key**
uniquely identifies one row (here `AlbumId`); a **foreign key** references
one.

| term | means | example in Chinook |
|---|---|---|
| **primary key** | uniquely identifies a row | `Album.AlbumId` |
| **foreign key** | points at another table's primary key | `Track.AlbumId` → `Album.AlbumId` |

### `INNER JOIN` — match rows from both sides

A join lines up rows from two tables where a condition (the `ON`) is true.
The classic form matches the foreign key to the primary key:

```sql
SELECT t.Name AS track,
       a.Title AS album
FROM   Track t
JOIN   Album a
  ON   a.AlbumId = t.AlbumId
LIMIT  5;
```

Read it: "for each track `t`, find the album `a` whose `AlbumId` equals the
track's, and give me both." The `t` and `a` are **table aliases** — short
names we use so we don't type `Track` and `Album` over and over, and so we
can tell the two tables apart.

An `INNER JOIN` (sometimes just `JOIN`) keeps **only the rows that match on
both sides**. If a track had an `AlbumId` that no album row possesses, that
track would disappear from the result.

You can chain joins to hop across three or more tables:

```sql
SELECT ar.Name AS artist,
       al.Title AS album,
       t.Name  AS track
FROM   Track t
JOIN   Album  al ON al.AlbumId  = t.AlbumId
JOIN   Artist ar ON ar.ArtistId = al.ArtistId
LIMIT  6;
```

Each `JOIN` adds one more table, each `ON` says how that new table connects
to one already in the query. The pattern is always **foreign key = primary
key**.

### `LEFT JOIN` — keep the left side even when there's no match

`INNER JOIN` drops rows that don't match. Sometimes you *want* those rows
back, with NULLs where the right side was missing. That's `LEFT JOIN`:
**every row from the left table appears**, and matching right-side values
are filled in — or `NULL` if there was no match.

### The cardinality rule (and why it matters for totals)

Joins have a shape: **one-to-many** (one album → many tracks),
**many-to-one** (many tracks → one album), or **one-to-one**. The direction
matters. When you join *many* tracks to *one* album, each album row is
**repeated once per track** — that's normal and fine for listing. But if you
then `SUM` or `AVG` a column from the *one* side, you've just counted it
many times. This **fan-out** is the most expensive join mistake in this
whole course, and Example 5 makes it concrete with real money.

---

## 2. Worked examples

### Example 1 — a basic two-table join

List the first few tracks with their album titles (the `Track`→`Album` hop
from the concept):

```sql
SELECT t.Name AS track,
       a.Title AS album
FROM   Track t
JOIN   Album a ON a.AlbumId = t.AlbumId
LIMIT  5;
```

```
track                                    album
---------------------------------------  -------------------------------------
For Those About To Rock (We Salute You)  For Those About To Rock We Salute You
Balls to the Wall                        Balls to the Wall
Fast As a Shark                          Restless and Wild
Restless and Wild                        Restless and Wild
Princess of the Dawn                     Restless and Wild
```

Notice the **one-to-many** shape showing up: album "Restless and Wild"
appears three times, once per track on it. That repetition is expected — we
joined many tracks to one album.

### Example 2 — three tables deep

Now add the artist. Three tables, two joins, both matching a foreign key to
a primary key:

```sql
SELECT ar.Name AS artist,
       al.Title AS album,
       t.Name  AS track
FROM   Track  t
JOIN   Album  al ON al.AlbumId  = t.AlbumId
JOIN   Artist ar ON ar.ArtistId = al.ArtistId
WHERE  ar.Name = 'AC/DC'
ORDER  BY t.TrackId
LIMIT  6;
```

```
artist  album                                  track
------  -------------------------------------  ---------------------------------------
AC/DC   For Those About To Rock We Salute You  For Those About To Rock (We Salute You)
AC/DC   For Those About To Rock We Salute You  Put The Finger On You
AC/DC   For Those About To Rock We Salute You  Let's Get It Up
AC/DC   For Those About To Rock We Salute You  Inject The Venom
AC/DC   For Those About To Rock We Salute You  Snowballed
AC/DC   For Those About To Rock We Salute You  Evil Walks
```

All of AC/DC's tracks sit on one album, so the album repeats. The `WHERE`
filters the joined result the same way it did in Lesson 02 — joining just
changed *which columns are available*. AC/DC has 18 tracks total; run it
without the `LIMIT` to see all of them.

### Example 3 — a self join: the org chart

A table can join **to itself**. The `Employee` table has a `ReportsTo`
column that points at *another row in the same table* (the employee's
manager). So to show each employee next to their manager, we join `Employee`
to itself, using two different aliases:

```sql
SELECT e.FirstName,
       e.LastName,
       e.Title,
       m.FirstName || ' ' || m.LastName AS manager
FROM   Employee e
LEFT   JOIN Employee m ON m.EmployeeId = e.ReportsTo
ORDER  BY e.EmployeeId;
```

```
FirstName  LastName  Title                manager
---------  --------  -------------------  ----------------
Andrew     Adams     General Manager
Nancy      Edwards   Sales Manager        Andrew Adams
Jane       Peacock   Sales Support Agent  Nancy Edwards
Margaret   Park      Sales Support Agent  Nancy Edwards
Steve      Johnson   Sales Support Agent  Nancy Edwards
Michael    Mitchell  IT Manager           Andrew Adams
Robert     King      IT Staff             Michael Mitchell
Laura      Callahan  IT Staff             Michael Mitchell
```

Two things are worth noticing:

- **Why two aliases?** A table can't join to itself as one thing. We call
  the "employee" side `e` and the "manager" side `m`, so
  `m.EmployeeId = e.ReportsTo` reads "the manager row whose `EmployeeId`
  equals this employee's `ReportsTo`." Without the aliases the database
  couldn't tell which `EmployeeId` you meant.
- **Why `LEFT JOIN` instead of `INNER`?** The top boss (Andrew Adams) has
  `ReportsTo` of `NULL` — nobody above him. An `INNER JOIN` would have
  *dropped* him, because `NULL` never equals anything. `LEFT JOIN` keeps him
  with a `NULL` manager. A self join is the textbook case where you reach for
  `LEFT JOIN`.

The `||` is string concatenation (we'll meet it properly in Lesson 08); it's
just a convenience to show "First Last" in one column.

### Example 4 — `LEFT JOIN` in general: the 71 artists with no albums

The self join was a special case. `LEFT JOIN` shines more broadly whenever
the left side has rows the right side can't match. In Chinook, **71 of the
275 artists have no albums** at all.

First, the `INNER JOIN` — the wrong tool:

```sql
SELECT COUNT(DISTINCT ar.Name)
FROM   Artist ar
JOIN   Album a ON a.ArtistId = ar.ArtistId;
```

```
COUNT(DISTINCT ar.Name)
-----------------------
204
```

Only 204 artists. The other 71 vanished, because an `INNER JOIN` needs a
matching album row to keep the artist — and they have none.

Now the `LEFT JOIN`:

```sql
SELECT COUNT(DISTINCT ar.ArtistId)
FROM   Artist ar
LEFT   JOIN Album a ON a.ArtistId = ar.ArtistId;
```

```
COUNT(DISTINCT ar.ArtistId)
----------------------------
275
```

All 275 back. To actually *see* the unpaired ones, filter for the NULLs on
the right side:

```sql
SELECT ar.ArtistId, ar.Name
FROM   Artist ar
LEFT   JOIN Album a ON a.ArtistId = ar.ArtistId
WHERE  a.AlbumId IS NULL
ORDER  BY ar.ArtistId
LIMIT  5;
```

```
ArtistId  Name
--------  --------------------------
25        Milton Nascimento & Bebeto
26        Azymuth
28        João Gilberto
29        Bebel Gilberto
30        Jorge Vercilo
```

**The recipe for "find the things with no match" is `LEFT JOIN … WHERE
<right-side-key> IS NULL`.** You *could* write it with `NOT EXISTS` (Lesson
07), but the `LEFT JOIN + IS NULL` form is the most common and the one to
know first.

### Example 5 — the fan-out trap: a join that ruins a `SUM`

Here's the one that will save you real money someday. What's the total
revenue in the store? The invoices alone know it:

```sql
SELECT ROUND(SUM(Total), 2) FROM Invoice;
```

```
ROUND(SUM(Total), 2)
--------------------
2328.6
```

Now suppose a coworker asks "total revenue *with the line items attached*"
and writes:

```sql
SELECT ROUND(SUM(i.Total), 2)
FROM   Invoice i
JOIN   InvoiceLine l ON l.InvoiceId = i.InvoiceId;
```

```
ROUND(SUM(i.Total), 2)
----------------------
20848.62
```

**About 9 times too large** (8.95×, to be exact). What happened? `InvoiceLine` has
2,240 rows across 412 invoices, so on average each invoice has about 5–6
line items. The `JOIN` repeats each `Invoice` row once per line item — so
`i.Total` (a value that belongs to the *invoice*) got summed once per line
item instead of once. The join **fanned out** the one-side column.

The count check that would have caught it:

```sql
SELECT COUNT(*) FROM Invoice i
JOIN   InvoiceLine l ON l.InvoiceId = i.InvoiceId;
```

```
COUNT(*)
--------
2240
```

That's not 412 invoices — it's 2,240 rows. The invoice side got multiplied.

**How to join and aggregate without corrupting your total:** do the
aggregation on the *right* side of the one-to-many, or aggregate each table
separately before joining. The safe version of "revenue per artist" — a
many-to-one chain that never fans a `SUM`-worthy column out — is:

```sql
SELECT ar.Name,
       ROUND(SUM(l.UnitPrice * l.Quantity), 2) AS revenue
FROM   InvoiceLine l
JOIN   Track  t  ON t.TrackId   = l.TrackId
JOIN   Album  a  ON a.AlbumId   = t.AlbumId
JOIN   Artist ar ON ar.ArtistId = a.ArtistId
GROUP  BY ar.Name
ORDER  BY revenue DESC
LIMIT  5;
```

```
Name          revenue
------------  -------
Iron Maiden   138.6
U2            105.93
Metallica     90.09
Led Zeppelin  86.13
Lost          81.59
```

Why is *this* join safe but the previous one corrupt? Because `SUM` is over
`l.UnitPrice * l.Quantity` — a column from the **many** side (the line
items), and the join is many-to-one all the way up (many lines → one track →
one album → one artist). No one-side value gets repeated. The rule: **don't
`SUM`/`AVG`/`COUNT` a column from the "one" side of a one-to-many join.**

---

## 3. Your turn

Work in litecli against `data/chinook.db` (this lesson only reads). Check
`answers.md` when done.

1. List the 10 tracks in alphabetical order, each with its album title.
2. How many albums does **Iron Maiden** have? How many does **Lenny
   Kravitz** have?
3. Show each customer with the name of their support rep (one `Customer` →
   `Employee` join).
4. Count the tracks per **artist**, biggest first, top 5. (You'll need all
   three of `Track`, `Album`, and `Artist`.)
5. How many **artists** in total have at least one album? (Hint: use
   `COUNT(DISTINCT …)` on the join.)

---

## 4. Quiz

Answer without scrolling up. The key is in `answers.md`.

1. In one sentence, what does an `INNER JOIN` drop from the result?
2. Why did the self-join in Example 3 use `LEFT JOIN` instead of
   `INNER JOIN`? What would `INNER JOIN` have done to the top boss?
3. You join `Invoice` to `InvoiceLine` and `SUM(Invoice.Total)`, and the
   number is about 9× too large. In one sentence, why?
4. Write the query that lists every **artist who has no albums** (just the
   artist names).
5. True or false: `JOIN` and `INNER JOIN` mean the same thing.
6. (Stretch) In one query, show each employee, their manager, and how many
   employees report *directly* to that manager. (A self join plus
   `COUNT`.)

---

## 5. Pitfalls

1. **Joining without an `ON` gives you a cross join** — every row paired
   with every other row. `SELECT * FROM Track t, Album a` (no `ON`) is
   3,503 × 347 = **1,215,541 rows**. Almost always a bug, and almost always
   a performance catastrophe. Every `JOIN` needs an `ON`.

2. **Fan-out corrupts aggregates** (Example 5). After a one-to-many join,
   don't `SUM`/`AVG`/`COUNT` a column from the *one* side. Count the result
   rows and compare to the source — if the join row count isn't what you
   expect, an aggregate on the one side is suspect.

3. **`INNER JOIN` silently drops the unpaired rows.** If you expect "all
   artists" but get fewer, the missing ones had no matching row. Reach for
   `LEFT JOIN` whenever "everything on this side, even if unmatched" is what
   you want.

4. **Unqualified column names.** If both tables have a column named `Name`
   (e.g. `Track.Name` and `Artist.Name`) and you `SELECT Name`, SQLite will
   pick one arbitrarily — and PostgreSQL will refuse the query outright.
   Always qualify: `t.Name`, `a.Name`, `ar.Name`.

5. **Matching the wrong keys.** `ON a.ArtistId = ar.ArtistId` is correct;
   `ON a.ArtistId = ar.AlbumId` is nonsense but *runs* (it just pairs rows by
   a coincidental number match and gives you garbage). Read the `ON` as a
   sentence: "album's artist **equals** artist's id." If it doesn't read as a
   true relationship, it's wrong.

6. **Forgetting `DISTINCT` where the join duplicates.** A one-to-many join
   repeats the one-side row; if you then `COUNT` without `DISTINCT` you
   count repeats, not things. `COUNT(DISTINCT ar.ArtistId)` counts artists;
   plain `COUNT(ar.ArtistId)` would count artist-rows (with repeats).

---

## 6. Recap

- A **primary key** identifies a row; a **foreign key** points at another
  table's primary key. Joins connect them: `ON <left>.<fk> = <right>.<pk>`.
- `INNER JOIN` keeps only rows that match on both sides.
- `LEFT JOIN` keeps every left row, filling `NULL` where there's no match —
  and `LEFT JOIN … WHERE <right-key> IS NULL` is how you find "the things
  with no match."
- A **self join** uses two aliases of the same table (the org chart).
- **Fan-out:** a one-to-many join repeats the one-side row; never aggregate
  a one-side column across such a join without care.

**Next up — Lesson 06 (Joins II & set operations):** what about `FULL`
joins and `CROSS` joins, and how do you *combine* the results of two queries
with `UNION`, `INTERSECT`, and `EXCEPT`? Lesson 06 finishes the join family
and adds the set tools.
