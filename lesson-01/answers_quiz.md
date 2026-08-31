# Lesson 01 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file. Every query below runs
against `data/chinook.db`. Expected outputs were verified against the
database as shipped in this repo.

Many different queries can be correct; the key shows one good version.
Compare **outputs**, not query text.

## Q1 — First 10 tracks

```sql
SELECT Name
FROM   Track
LIMIT  10;
```

```
Name
---------------------------------------
For Those About To Rock (We Salute You)
Balls to the Wall
Fast As a Shark
Restless and Wild
Princess of the Dawn
Put The Finger On You
Let's Get It Up
Inject The Venom
Snowballed
Evil Walks
```

## Q2 — Distinct genre IDs

```sql
SELECT DISTINCT GenreId
FROM   Track;
```

Returns one row for each of the 25 genre IDs, from `1` through `25`.

## Q3 — Names of all media types, ordered by their id

```sql
SELECT Name
FROM   MediaType
ORDER  BY MediaTypeId;
```

```
Name
---------------------------
MPEG audio file
Protected AAC audio file
Protected MPEG-4 video file
Purchased AAC audio file
AAC audio file
```

Note: 5 rows. The last one (`AAC audio file`, id 5) sorts *after* the
`P...` rows alphabetically — but we ordered by id, not by name, which is
why it's last. A common slip is to write `ORDER BY Name`.

## Q4 — Names of the 3 most expensive tracks (with price)

Any 3 of the tracks priced 1.99 are correct (there are several). One good
answer, tie-broken by name:

```sql
SELECT Name, UnitPrice
FROM   Track
ORDER  BY UnitPrice DESC, Name
LIMIT  3;
```

```
Name                UnitPrice
------------------ ----------
"?                  1.99
...And Found        1.99
...In Translation   1.99
```

Accept: any query returning 3 rows where `UnitPrice` is 1.99.
Don't accept: a query that returns 3 rows without verifying the price is
the maximum (e.g. `ORDER BY Name LIMIT 3`).

## Q5 — The 5 artists alphabetically just after the first 50

```sql
SELECT Name
FROM   Artist
ORDER  BY Name
LIMIT  5 OFFSET 50;
```

```
Name
----------------------------------------
Cake
Calexico
Charles Dutoit & L'Orchestre Symphonique de Montréal
Charlie Brown Jr.
Chicago Symphony Chorus, Chicago Symphony Orchestra & Sir Georg Solti
```

Long names may wrap in the result table — that's display, not data.
Don't accept an `OFFSET 50` without an `ORDER BY` (unstable result) or an
`OFFSET` written before a `LIMIT` (SQLite syntax error — pitfall 2).

---
