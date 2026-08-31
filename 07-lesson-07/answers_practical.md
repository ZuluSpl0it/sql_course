# Lesson 07 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)
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
