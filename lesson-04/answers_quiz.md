# Lesson 04 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file. This lesson only
reads, so you can run everything directly against `data/chinook.db`.

---

## Quiz

### Q1 — total revenue per billing country, biggest first

```sql
SELECT BillingCountry,
       ROUND(SUM(Total), 2) AS revenue
FROM   Invoice
GROUP  BY BillingCountry
ORDER  BY revenue DESC;
```

Top 5 of the 24 rows:

```
BillingCountry    revenue
--------------    -------
USA               523.06
Canada            303.96
France            195.10
Brazil            190.10
Germany           156.48
```

(No `HAVING` needed — every group is kept; `ORDER BY` just sorts them.)

### Q2 — customers with more than 6 invoices

```sql
SELECT CustomerId,
       COUNT(*) AS invoices
FROM   Invoice
GROUP  BY CustomerId
HAVING COUNT(*) > 6
ORDER  BY CustomerId;
```

Returns **58 rows** — customers 1 through 58. The dataset has 59 customers;
all of them bought **7** invoices *except* customer 59, who bought only 6.
So "more than 6" excludes exactly one customer.

### Q3 — countries whose average invoice exceeds $6

```sql
SELECT BillingCountry,
       ROUND(AVG(Total), 2) AS avg_invoice
FROM   Invoice
GROUP  BY BillingCountry
HAVING AVG(Total) > 6
ORDER  BY avg_invoice DESC;
```

```
BillingCountry    avg_invoice
--------------    -----------
Chile             6.66
Ireland           6.52
Hungary           6.52
Czech Republic    6.45
Austria           6.09
```

Exactly **5 countries**. Note the threshold: at $5 *all* 24 countries
qualify, so the question would filter nothing — a `HAVING` clause that
keeps everything isn't filtering. (Ireland and Hungary tie to two decimal
places; if you sort on the unrounded `AVG(Total)` their relative order may
flip — either row order is fine.)

### Q4 — True or false: `WHERE COUNT(*) > 5` is valid SQL

**False.** `WHERE` runs *before* grouping, when no group — and hence no
`COUNT(*)` — exists yet. SQLite rejects it:

```
SELECT Country, COUNT(*)
FROM   Customer
WHERE  COUNT(*) > 5
GROUP  BY Country;

-- Error: misuse of aggregate: COUNT()
```

Aggregate conditions go in `HAVING`.

### Q5 — `COUNT(*)` vs `COUNT(Composer)` on `Track`

`COUNT(*)` is larger: **3,503** vs **2,526**. `COUNT(*)` counts all rows;
`COUNT(Composer)` counts only rows where `Composer` is not NULL, and 977
tracks have a NULL composer (3,503 − 2,526 = 977).

### Q6 (stretch) — tracks and catalog value per genre, top 5

```sql
SELECT GenreId,
       COUNT(*)  AS tracks,
       ROUND(SUM(UnitPrice), 2) AS value
FROM   Track
GROUP  BY GenreId
ORDER  BY value DESC
LIMIT  5;
```

```
GenreId  tracks  value
-------  ------  ------
1        1297    1284.03
7        579     573.21
3        374     370.26
4        332     328.68
19       93      185.07
```

(Genre names: 1 = Rock, 3 = Metal, 4 = Alternative & Punk, 7 = Latin.)

---
