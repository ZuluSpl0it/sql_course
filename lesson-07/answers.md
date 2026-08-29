# Lesson 07 — Quiz & Your-Turn Answer Key
Attempt the Quiz and Your turn in `lesson.md` before opening this file.
This lesson only reads, so run everything against `data/chinook.db`.

---
## Your turn
### 1 — scalar in the `SELECT` list
Add the store total as a column next to each of the first 5 invoices:
```sql
SELECT i.InvoiceId, i.Total, (SELECT ROUND(SUM(Total), 2) FROM Invoice) AS store_total FROM Invoice i ORDER BY i.InvoiceId LIMIT 5;
```

```
InvoiceId  Total  store_total
---------  -----  -----------
1          1.98   2328.6
2          3.96   2328.6
3          5.94   2328.6
4          8.91   2328.6
5          13.86  2328.6
```
The `store_total` column is the same $2,328.60 on every row — the subquery
never references the outer row, so it's computed once and copied.
### 2 — correlated average
```sql
SELECT c.CustomerId, c.FirstName, (SELECT ROUND(AVG(i2.Total), 2) FROM Invoice i2 WHERE i2.CustomerId = c.CustomerId) AS avg_spend, (SELECT ROUND(AVG(Total), 2) FROM Invoice) AS store_avg FROM Customer c ORDER BY avg_spend DESC, c.CustomerId LIMIT 5;
```

```
CustomerId  FirstName  avg_spend  store_avg
----------  ---------  ---------  ---------
6           Helena     7.09       5.65
26          Richard    6.8        5.65
57          Luis       6.66       5.65
45          Ladislav   6.52       5.65
46          Hugh       6.52       5.65
```
Each `avg_spend` is that customer's own average invoice; `store_avg` is the
store-wide $5.65. The first customer's average is above the store average,
the others straddle it — exactly the "this row vs the baseline" read you
wanted.
### 3 — per-customer total (join version)
```sql
SELECT c.FirstName || ' ' || c.LastName AS customer, ROUND(SUM(i.Total), 2) AS total FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.CustomerId ORDER BY total DESC LIMIT 5;
```

```
customer            total
------------------  -----
Helena Holý         49.62
Richard Cunningham  47.62
Luis Rojas          46.62
Ladislav Kovács     45.62
Hugh O'Reilly       45.62
```
Same goal as #1 but via `JOIN` + `GROUP BY` instead of a correlated subquery.
The top customer's total differs from #2's top *average* because #2 ranks by
average (and divides by that customer's invoice count) while #3 ranks by raw
total.
### 4 — artists with no sales
```sql
SELECT COUNT(*) FROM Artist a WHERE NOT EXISTS (SELECT 1 FROM Album al JOIN Track t ON al.AlbumId = t.AlbumId JOIN InvoiceLine il ON t.TrackId = il.TrackId WHERE al.ArtistId = a.ArtistId);
```

```
COUNT(*)
--------
110
```
**110** artists have no line item anywhere. (`NOT EXISTS` is the safe form;
`NOT IN` would also work here because `Artist.ArtistId` is never `NULL`, but
`NOT EXISTS` is the habit to keep.)
### 5 — stretch: rank artists by revenue
```sql
WITH artist_revenue AS (SELECT a.ArtistId, a.Name, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue FROM Artist a JOIN Album al ON a.ArtistId = al.ArtistId JOIN Track t ON al.AlbumId = t.AlbumId JOIN InvoiceLine il ON t.TrackId = il.TrackId GROUP BY a.ArtistId, a.Name) SELECT ar.Name, ar.revenue, (SELECT COUNT(*) FROM artist_revenue ar2 WHERE ar2.revenue > ar.revenue) + 1 AS revenue_rank FROM artist_revenue ar ORDER BY revenue_rank LIMIT 5;
```

```
Name          revenue  revenue_rank
------------  -------  ------------
Iron Maiden   138.6    1
U2            105.93   2
Metallica     90.09    3
Led Zeppelin  86.13    4
Lost          81.59    5
```
Each rank is `1 + (number of artists earning strictly more)`. Ties share a
rank (two artists at the same revenue get the same number), so you can get
ranks like 1, 2, 3, 3, 5 — a "competition" ranking, not a dense one. That's
what the correlated count naturally gives you.

---
## Quiz
### 1 — what a scalar subquery must return
**Exactly one row with exactly one column.** In SQLite 3.31, if it returns
more than one row it does *not* error — it silently uses the *first* row
(Pitfall 1). If it returns more than one *column*, that is a hard error
(`more than one column returned by a subquery`).
### 2 — `IN` vs `=` with a two-row subquery
The subquery `SELECT EmployeeId FROM Employee ORDER BY EmployeeId LIMIT 2`
returns the set {1, 2}.
- `WHERE EmployeeId IN (…)`: membership in a **set** → matches both 1 and 2 →
  **2 rows**.
- `WHERE EmployeeId = (…)`: `=` expects a **scalar** (one value). SQLite 3.31
  silently uses the *first* row (id 1) → matches only 1 → **1 row**.
So `IN` is set membership (many matches), `=` is a scalar comparison (one
value, and in SQLite the first of a multi-row subquery).
### 3 — `WHERE x = (multi-row subquery)` in SQLite 3.31
It does **not** error. SQLite 3.31 returns the *first* row of the subquery's
result and compares `x` against that — so the test is only against row 1, and
the other rows are silently ignored. MySQL and PostgreSQL, by contrast, stop
with a *"subquery returns more than one row"* error. Because SQLite is silent,
this is a real correctness trap: put an explicit `LIMIT 1` in the subquery if
you truly want "the first one", or use `IN`/`EXISTS` if you want a set test.
### 4 — `NOT IN` vs `NOT EXISTS` with a `NULL`
`ReportsTo` is `NULL` for the CEO, so `(SELECT ReportsTo FROM Employee)`
contains a `NULL`.
- `e.EmployeeId NOT IN (…that set containing a NULL)`: `NULL` makes the
  `IN` test `UNKNOWN` for every row, so **0 rows**.
- `NOT EXISTS (SELECT 1 FROM Employee r WHERE r.ReportsTo = e.EmployeeId)`: no
  `NULL` in the logic — it just asks "does anyone report to this employee?"
  → the 5 employees with no reports (ids 3, 4, 5, 7, 8) → **5 rows**.
`NOT EXISTS` is the correct "nobody reports to this" test; `NOT IN` is the
NULL-trap.
### 5 — when to use a `WITH`
Use a `WITH` when you need the **same subquery more than once** in a query
(you reference it by name instead of repeating it), or when a long
derived-table expression would obscure the main `SELECT` and a name makes it
readable. A CTE is otherwise just a derived table with a name — it can also be
referenced multiple times, which a plain inline `(SELECT …)` in one `FROM`
position cannot.
### 6 — stretch: 0-row anchor, and cycles
If the anchor matches **zero** employees (`WHERE EmployeeId = 999`), the walk
has no seed, so the result is **0 rows** — no error. If the data had a
**cycle**, there would be no "last" row: every pass would keep re-adding
already-seen employees, so the recursion **never terminates** and the query
runs until you stop it. Keep it safe two ways: (a) keep a restrictive anchor
filter, and (b) add a **depth cap** in the recursive part, e.g.
`WHERE org.depth < 10` (or track seen ids with a `SEEN` set) so a cyclic or
pathological graph stops after a bounded number of levels instead of
spinning forever.

---
## Answers to the worked examples (for checking yourself)
| example | the number to check |
|---|---|
| 1 — non-correlated vs correlated | constant **$2,328.60** on every row → varies per customer |
| 2 — `IN` vs `EXISTS` (Rock artists) | both **51** (first 5 shown) |
| 3 — derived table, top-3 + bottom-3 | **6** rows (3 top + 3 bottom) |
| 4 — `WITH` per-artist revenue, top 5 | Iron Maiden **$138.60**, U2 $105.93, Metallica $90.09, Led Zeppelin $86.13, Lost $81.59 |
| 5 — `WITH RECURSIVE` org chart | **8** rows, max depth **2** (1 / 2 / 5 per level) |
| 5 — missing anchor filter | **20** rows (not 8) |
| 5 — hard-coded two-level join | **8** rows (stops at depth 2 by construction) |
