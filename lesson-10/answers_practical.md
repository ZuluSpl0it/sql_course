# Lesson 10 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

### T1 — billing-country plan

```sql
EXPLAIN QUERY PLAN
SELECT COUNT(*)
FROM   Invoice
WHERE  BillingCountry = 'Germany';
```

Without an index on `BillingCountry`, SQLite begins with an invoice scan. The important answer is the evidence from your own plan, not a guessed timing conclusion.

### T2 — searchable versus wrapped country

```sql
CREATE INDEX idx_l10_customer_country ON Customer(Country);

EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM Customer WHERE Country = 'Germany';

EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM Customer WHERE UPPER(Country) = 'GERMANY';

DROP INDEX idx_l10_customer_country;
```

The direct equality can search the ordinary index. Wrapping the column in `UPPER()` changes the value SQLite would need to look up, so the ordinary index is not a usable search range.

### T3 — top customer spenders

The grain is **one invoice** before grouping. `Invoice.Total` is already an invoice-level total, so joining `InvoiceLine` would repeat it.

```sql
SELECT c.FirstName || ' ' || c.LastName AS customer,
       ROUND(SUM(i.Total), 2) AS total_spend
FROM   Customer c
JOIN   Invoice i ON i.CustomerId = c.CustomerId
GROUP  BY c.CustomerId, c.FirstName, c.LastName
ORDER  BY total_spend DESC, customer
LIMIT  10;
```

### T4 — artists with no sold tracks

```sql
SELECT ar.Name
FROM   Artist ar
WHERE  NOT EXISTS (
  SELECT 1
  FROM   Album al
  JOIN   Track t        ON t.AlbumId = al.AlbumId
  JOIN   InvoiceLine il ON il.TrackId = t.TrackId
  WHERE  al.ArtistId = ar.ArtistId
)
ORDER  BY ar.Name;
```

`NOT EXISTS` asks the business question directly and avoids carrying nullable rows through a long outer join.

### T5 — countries above the average country revenue

```sql
WITH country_revenue AS (
  SELECT BillingCountry AS country,
         ROUND(SUM(Total), 2) AS revenue
  FROM   Invoice
  GROUP  BY BillingCountry
)
SELECT country, revenue
FROM   country_revenue
WHERE  revenue > (SELECT AVG(revenue) FROM country_revenue)
ORDER  BY revenue DESC, country;
```

### T6 — an `IFK_` index

`IFK_TrackAlbumId` supports lookups from `Track.AlbumId` to an album. It does not enforce the foreign key — enforcement comes from the constraint plus `PRAGMA foreign_keys = ON` — but it helps SQLite find a parent's child tracks.

```sql
EXPLAIN QUERY PLAN
SELECT Name FROM Track WHERE AlbumId = 1;
```
