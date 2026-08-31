# Lesson 01: Your First Query

SQL (Structured Query Language) is how you talk to a relational database.
A relational database stores data in **tables** — grids of rows and columns.
In Chinook, for example, `Artist` is a table of rows, each row one artist,
with a `Name` column.

A SQL query is a sentence with a fixed grammar. The most basic sentence is:

```sql
SELECT <what you want>
FROM   <where to get it>;
```

Read it out loud and it almost works: *"Select the name, from the artist
table."* Every SQL query you'll ever write is built from this skeleton.
The rest of this lesson fills in the parts you control: which columns,
whether rows may repeat, what the output columns are called, the order of
rows, and how many you get back.

## 1. The concept

### 1.1 SELECT and FROM

```sql
SELECT Name
FROM   Artist;
```

- `SELECT` names the **columns** you want, one per comma.
- `FROM` names the **table** the rows come from.
- The `;` ends the statement. Use the playground's **Run** control to execute
  it.

The query returns one row per artist (275 rows) with a single column, `Name`.
Column names are case-insensitive in SQLite: `name` and `Name` are the same.

### 1.2 Selecting many columns — and all columns

```sql
SELECT Name, GenreId, UnitPrice
FROM   Track;
```

Each selected column becomes a column in the result. Order matters: the
result's columns come out in the order you listed them.

```sql
SELECT *
FROM   Genre;
```

`*` means "every column of the table". It's great for exploring a table you
 don't know yet — the playground's schema panel tells you what each column is.
In queries you keep and share, prefer naming the columns you actually need
(`SELECT *` can break silently if the table changes, and it reads worse).

### 1.3 DISTINCT — removing duplicate rows

If you `SELECT GenreId FROM Track`, the same genre appears on every one of
its 3,503 tracks. You wanted the *list of genres*, not 3,503 copies of each:

```sql
SELECT DISTINCT GenreId
FROM   Track;
```

`DISTINCT` keeps only one copy of each **identical row**. If you selected
two columns, both would have to match for rows to be considered duplicates.

### 1.4 Naming output columns — AS

`SELECT UnitPrice FROM Track` gives you a result column literally called
`UnitPrice`. Sometimes you want a friendlier label:

```sql
SELECT UnitPrice AS price_usd
FROM   Track;
```

`AS <label>` renames a column in the result. You'll also use `AS` to name
tables (Lesson 05) — it's the same mechanism.

### 1.5 Ordering — ORDER BY

By default the database returns rows in whatever order it likes —
don't rely on it. To control the order:

```sql
SELECT Name
FROM   Artist
ORDER  BY Name;            -- default: A → Z (ASC = ascending)
```

For the reverse order, add `DESC`:

```sql
SELECT Name
FROM   Artist
ORDER  BY Name DESC;       -- Z → A (descending)
```

You can sort by several columns at once — left to right, first key first:

```sql
SELECT Name, UnitPrice
FROM   Track
ORDER  BY UnitPrice DESC, Name;   -- highest price first, ties broken by name
```

### 1.6 Taking fewer rows — LIMIT and OFFSET

```sql
SELECT Name
FROM   Artist
LIMIT  5;                -- first 5 rows (in whatever order is in effect)
```

`LIMIT n` says "give me at most n rows". To skip rows — the third page of
5, say — combine it with `OFFSET`:

```sql
SELECT Name
FROM   Artist
ORDER  BY Name
LIMIT  5 OFFSET 10;      -- skip 10 rows, then take 5
```

`ORDER BY` before `LIMIT`/`OFFSET` matters: without a sort, "the next 5"
means nothing stable.

**The order of clauses is fixed**, and this order is one you'll never break:

```
SELECT  →  FROM  →  (WHERE, later)  →  ORDER BY  →  LIMIT / OFFSET
```

## 2. Worked examples

### Example 1 — the first query

Goal: look at the first few artists.

```sql
SELECT Name
FROM   Artist;
```

First rows (275 total):

```
Name
-------------------------
AC/DC
Accept
Aerosmith
Alanis Morissette
Alice In Chains
...
```

Notice: no `ORDER BY`, so this order is the table's storage order — it
happens to look alphabetical here, but don't trust it.

### Example 2 — several columns at once

Goal: see a track's name, genre, and price together.

```sql
SELECT Name, GenreId, UnitPrice
FROM   Track;
```

First rows (3,503 total):

```
Name                                     GenreId  UnitPrice
---------------------------------------  -------  ---------
For Those About To Rock (We Salute You)  1        0.99
Balls to the Wall                        1        0.99
Fast As a Shark                          1        0.99
Restless and Wild                        1        0.99
Princess of the Dawn                     1        0.99
```

(Names may wrap in the result table — the data is complete.)

### Example 3 — DISTINCT in action

Goal: the list of genre numbers, without 3,503 copies.

```sql
SELECT DISTINCT GenreId
FROM   Track;
```

```
GenreId
----------
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
```

25 rows instead of 3,503. If you had selected `DISTINCT GenreId, Name`,
the deduplication would have required **both** columns to match — most
tracks' names differ, so you'd still get almost all 3,503 rows back.

### Example 4 — naming output columns

Goal: the same data, friendlier headers for a report.

```sql
SELECT Name AS song, UnitPrice AS price_usd
FROM   Track
LIMIT  5;
```

```
song                                     price_usd
---------------------------------------  ---------
For Those About To Rock (We Salute You)  0.99
Balls to the Wall                        0.99
Fast As a Shark                          0.99
Restless and Wild                        0.99
Princess of the Dawn                     0.99
```

Nothing changed in the data — only the labels the reader sees. `AS` is a
label, not a new column; you cannot refer to `price_usd` anywhere else in
this query (you can in later lessons' subqueries, but that's another day).

### Example 5 — sorting, descending, with a tie-breaker

Goal: the most expensive tracks.

```sql
SELECT Name, UnitPrice
FROM   Track
ORDER  BY UnitPrice DESC, Name
LIMIT  5;
```

```
Name                              UnitPrice
--------------------------------  ---------
"?"                               1.99
...And Found                      1.99
...In Translation                 1.99
.07%                              1.99
A Benihana Christmas, Pts. 1 & 2  1.99
```

Two lessons in one: `DESC` puts the highest values first, and the second
sort key (`Name`) decides the order *within* equal prices — without it,
which of the many 1.99 tracks you'd see would be random.

### Example 6 — paging with LIMIT and OFFSET

Goal: artists #11–15 in alphabetical order.

```sql
SELECT Name
FROM   Artist
ORDER  BY Name
LIMIT  5 OFFSET 10;
```

```
Name
-------------------------------------------
Adrian Leaper & Doreen de Feis
Aerosmith
Aerosmith & Sierra Leone's Refugee Allstars
Aisha Duo
Alanis Morissette
```

(The third name is long and may wrap in the result table; that's display, not
data.)

This is how every "page 2 of a results list" in any web app is built.

## 3. Your turn

Attempt these in Jasper SQL Playground before looking at anything else. No answers in
this file's query form — that's the point. The result targets below let you
check your work without giving away the SQL. (The quiz has its answer key in
`answers.md`.)

1. List the first 10 tracks in the database.
2. List the 5 artists with the last names in alphabetical order,
   reversed (Z → A).
3. Show the media type names, one per row. (Hint: it's a small table —
   `SELECT *` is fine here.)
4. List the 5 tracks with the *lowest* price, cheapest first, with
   the price column labeled `price`.
5. (stretch) List the 5 artists at position 251–255 alphabetically.

Compare your results with these targets. The targets show output only — write
the queries yourself:

1. Ten rows: `For Those About To Rock (We Salute You)`, `Balls to the Wall`,
   `Fast As a Shark`, `Restless and Wild`, `Princess of the Dawn`,
   `Put The Finger On You`, `Let's Get It Up`, `Inject The Venom`,
   `Snowballed`, `Evil Walks`.
2. Five rows in this order: `Zeca Pagodinho`, `Youssou N'Dour`, `Yo-Yo Ma`,
   `Yehudi Menuhin`, `Xis`.
3. Five media type names: `MPEG audio file`, `Protected AAC audio file`,
   `Protected MPEG-4 video file`, `Purchased AAC audio file`,
   `AAC audio file`.
4. Five rows, each with a `Name` and `price` column; every price is `0.99`.
   Names, in order: `"40"`, `"Eine Kleine Nachtmusik" Serenade In G, K. 525: I. Allegro`,
   `#1 Zero`, `#9 Dream`, `'Round Midnight`.
5. Five rows in this order: `The Postal Service`, `The Rolling Stones`,
   `The Tea Party`, `The Who`, `Tim Maia`.

## 4. Pitfalls

**Pitfall 1 — "The rows are in the right order!"**
They are only in the order you *asked* for. A `SELECT` without `ORDER BY`
may look sorted (small tables often come out in storage order) and then
reorder itself later. If the order matters, say so.

**Pitfall 2 — OFFSET without LIMIT**

```sql
SELECT Name FROM Artist ORDER BY Name OFFSET 270;
-- Error: near "OFFSET": syntax error
```

SQLite's grammar requires `LIMIT` first: `LIMIT 5 OFFSET 10`. (Other
databases differ; in SQLite, the limit comes before the offset.)

**Pitfall 3 — DISTINCT where you need it, and where it hides problems**
`DISTINCT` is not a filter on one column — it dedupes **whole rows**.
If you want unique values of one column, select *only that column* and
then `DISTINCT` it. If `DISTINCT` makes a number "smaller than expected",
check whether the other columns in your select are different.

**Pitfall 4 — complete statements**
In Jasper SQL Playground, click **Run** after entering a complete statement.
Use a separate query tab when comparing two versions of a query.

**Pitfall 5 — `SELECT *` in a query you ship**
Fine for exploring, fragile for work. If a column is added to `Track`
later, a `SELECT *` query silently changes shape and can break whatever
reads its output. Name the columns you mean.

## 5. Recap

- `SELECT columns FROM table;` — the skeleton of every SQL query.
- `*` = all columns; naming columns is better for real work.
- `DISTINCT` removes duplicate **rows**.
- `AS` renames output columns (and, later, tables).
- `ORDER BY col [ASC|DESC] [, col2 ...]` — sort; ASC is the default.
- `LIMIT n` — at most n rows; `LIMIT n OFFSET m` — skip m, take n.
  In SQLite, `LIMIT` must come before `OFFSET`.
- Clause order is fixed: `SELECT → FROM → ORDER BY → LIMIT/OFFSET`.
- No `ORDER BY`, no guaranteed order — ever.

## 6. Quiz

Five questions. For each, write a query, run it, and compare your output
with `answers.md`. A correct answer is a query that **returns** the right
result — many different queries can be correct; the key shows one good one.

1. List the 10 tracks at the start of the database.
2. List the distinct `GenreId` values in `Track`, one per row.
3. List the names of all media types, ordered by their id.
4. What are the names and prices of the 3 most expensive tracks?
   (Any 3 of the 1.99-priced tracks counts — list them with the price.)
5. List the 5 artists alphabetically just after the first 50.

## 7. Look ahead

Lesson 02 adds `WHERE` — the clause that decides *which rows* come back at
all. Until now every query has returned all (or a page of all) the rows of
its table; next, you'll learn to keep only the ones you actually want,
using `AND`/`OR`/`NOT`, `IN`, `BETWEEN`, `LIKE`, and the tricky `IS NULL`.
