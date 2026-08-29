# Lesson 10: Performance & Capstone

You can write a query. Now ask what work SQLite performs to answer it. A
query plan is a route description, not a stopwatch. This capstone combines
that judgment with correct joins, correct row grain, clear names, and only
evidence-backed indexes.

## 1. The concept

Run `EXPLAIN QUERY PLAN` before the query you are investigating:

```sql
EXPLAIN QUERY PLAN
SELECT COUNT(*)
FROM   Invoice
WHERE  InvoiceDate >= '2023-01-01'
  AND  InvoiceDate <  '2024-01-01';
```

- **SCAN** reads every candidate row in a table or index.
- **SEARCH** uses a condition to narrow candidates.
- **USING INDEX** finds rows through an index; **COVERING INDEX** supplies all
  requested columns from the index itself.
- **USE TEMP B-TREE** means SQLite needs temporary sorting or grouping work.

litecli may compact the plan into one detail line while Python shows four
columns. Read the words, not the display decoration. A `SEARCH` is evidence
about plan shape, not proof of a meaningful timing win on a small table.

## 2. Worked examples

### Example 1 — begin with a correct report

Goal: the five artists whose sold tracks produced the most revenue. Follow
the keys Artist → Album → Track → InvoiceLine.

```sql
SELECT ar.Name AS artist,
       ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue
FROM   Artist ar
JOIN   Album al       ON al.ArtistId = ar.ArtistId
JOIN   Track t        ON t.AlbumId = al.AlbumId
JOIN   InvoiceLine il ON il.TrackId = t.TrackId
GROUP  BY ar.ArtistId, ar.Name
ORDER  BY revenue DESC, artist
LIMIT  5;
```

```
artist        revenue
------------  -------
Iron Maiden   138.6
U2            105.93
Metallica     90.09
Led Zeppelin  86.13
Lost          81.59
```

Correctness comes first. An index cannot repair the wrong join or duplicated
rows.

### Example 2 — one narrow index, one specific question

Goal: count and total the invoices from 2023.

```sql
SELECT COUNT(*) AS invoices,
       ROUND(SUM(Total), 2) AS revenue
FROM   Invoice
WHERE  InvoiceDate >= '2023-01-01'
  AND  InvoiceDate <  '2024-01-01';
```

```
invoices  revenue
--------  -------
83        469.58
```

```sql
CREATE INDEX idx_l10_invoice_date ON Invoice(InvoiceDate);

EXPLAIN QUERY PLAN
SELECT COUNT(*)
FROM   Invoice
WHERE  InvoiceDate >= '2023-01-01'
  AND  InvoiceDate <  '2024-01-01';
```

The new plan says `SEARCH ... USING COVERING INDEX idx_l10_invoice_date`.
The result is unchanged; only the route changed. On 412 invoices, do not
promise a visible timing win. Indexes also consume space and write work.

### Example 3 — an index cannot rescue every predicate

```sql
CREATE INDEX idx_l10_track_name ON Track(Name);

EXPLAIN QUERY PLAN
SELECT COUNT(*)
FROM   Track
WHERE  Name LIKE '%The%';
```

The leading `%` gives SQLite no known starting point in ordered names, so it
still scans candidates. Compare the two counts:

```sql
SELECT COUNT(*) AS contains_the
FROM   Track
WHERE  Name LIKE '%The%';

SELECT COUNT(*) AS starts_the
FROM   Track
WHERE  Name LIKE 'The%';
```

```
contains_the
------------
543

starts_the
----------
219
```

An index helps only when the predicate exposes a searchable range. A leading
wildcard hides that range.

### Example 4 — a report with no fan-out

Goal: revenue by genre. Start from `InvoiceLine`, because each row is one
sale, then join through `Track` to `Genre`. Do not join playlists: one track
can appear in several playlists and would repeat the same sale.

```sql
SELECT g.Name AS genre,
       COUNT(*) AS line_items,
       ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue
FROM   InvoiceLine il
JOIN   Track t ON t.TrackId = il.TrackId
JOIN   Genre g ON g.GenreId = t.GenreId
GROUP  BY g.GenreId, g.Name
ORDER  BY revenue DESC, genre
LIMIT  5;
```

```
genre               line_items  revenue
------------------  ----------  -------
Rock                835         826.65
Latin               386         382.14
Metal               264         261.36
Alternative & Punk  244         241.56
TV Shows            47          93.53
```

The grain is the safety check: before grouping, every row represents one sold
invoice line. Re-check every aggregate whenever a join changes that grain.

### Example 5 — name repeated logic with a CTE

The artist-revenue join is useful more than once. A CTE gives its business
definition one name and keeps the ranking query readable.

```sql
WITH artist_revenue AS (
  SELECT ar.Name AS artist,
         ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue
  FROM   Artist ar
  JOIN   Album al       ON al.ArtistId = ar.ArtistId
  JOIN   Track t        ON t.AlbumId = al.AlbumId
  JOIN   InvoiceLine il ON il.TrackId = t.TrackId
  GROUP  BY ar.ArtistId, ar.Name
)
SELECT artist, revenue
FROM   artist_revenue
ORDER  BY revenue DESC, artist
LIMIT  5;
```

```
artist        revenue
------------  -------
Iron Maiden   138.6
U2            105.93
Metallica     90.09
Led Zeppelin  86.13
Lost          81.59
```

`WITH` is not a magic speed switch. It makes a repeated definition easier to
read and maintain; verify its result and plan like any other query.

### Example 6 — teardown is part of performance work

Temporary indexes are still schema changes. Drop them, then prove they are
gone before calling the scratch copy clean.

```sql
DROP INDEX idx_l10_invoice_date;
DROP INDEX idx_l10_track_name;

SELECT type, name
FROM   sqlite_master
WHERE  name LIKE 'idx_l10_%'
ORDER  BY type, name;
```

```
(no rows)
```

## 3. Your turn

Work in your scratch copy. Check [answers.md](answers.md) after attempting
the work.

1. Run `EXPLAIN QUERY PLAN` for invoices filtered to one billing country.
   Which table or index does SQLite begin with?
2. Create `idx_l10_customer_country` on `Customer(Country)`. Compare
   `Country = 'Germany'` with `UPPER(Country) = 'GERMANY'`, then drop it.
3. Write each customer's total spend, highest first, limited to 10. State the
   row grain before writing SQL.
4. Find artists with no sold tracks using `NOT EXISTS`.
5. Build a CTE for revenue by country, then keep countries above the average
   country revenue.
6. Stretch: find one `IFK_` index used by a course query and explain why it
   helps lookup work without enforcing the foreign key itself.

## 4. Quiz

1. What is the difference between `SCAN` and `SEARCH`?
2. What does `USING COVERING INDEX` mean?
3. Why does a `SCAN` → `SEARCH` change not prove a timing win?
4. Why can an index on `Track(Name)` not narrow `LIKE '%The%'`?
5. Name one cost of an index.
6. A report joins `InvoiceLine` to `PlaylistTrack` and doubles revenue. What
   happened, and what should you check first?

## 5. Pitfalls

1. **Indexing before checking correctness.** An index can speed up the wrong
   answer; check keys and row grain first.
2. **Treating a plan as a stopwatch.** Plans describe a route, not elapsed
   milliseconds.
3. **Hiding a search range.** Leading wildcards and wrapped columns often stop
   an ordinary index from narrowing a lookup.
4. **Fan-out after a many-to-many join.** Playlist membership is not sales;
   joining it to sales repeats invoice lines.
5. **Treating a CTE as a performance guarantee.** It is a naming boundary,
   not an automatic optimization.
6. **Leaving experimental indexes behind.** Name, drop, and verify every
   temporary object.

## 6. Recap

- Read plans for shape: `SCAN`, `SEARCH`, index lookup, covering index, and
  temporary work.
- Make an index answer one demonstrated access pattern; it costs storage and
  write maintenance.
- Start an aggregate from the table matching the report's grain.
- Use CTEs to name repeated business definitions.
- Drop temporary indexes and prove they are gone.

## 7. Look ahead

You have the core SQL toolkit. The next step is practice on databases you did
not design: state the row grain, verify the result, inspect the plan only
afterward, and leave the data cleaner than you found it.
