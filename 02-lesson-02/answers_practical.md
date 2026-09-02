# Lesson 02 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.
`ORDER BY` appears below when useful for stable, readable output. It is
required only when the exercise explicitly requests an order or a first/last
subset.

## Practical Exercises (reference)

1. German customers:

```sql
SELECT FirstName, LastName, Country
FROM   Customer
WHERE  Country = 'Germany'
ORDER  BY LastName, FirstName;
```

4 rows: Leonie Köhler, Hannah Schneider, Niklas Schröder, Fynn Zimmermann.

2. Tracks at exactly 1.99, alphabetical, first 5:

```sql
SELECT Name
FROM   Track
WHERE  UnitPrice = 1.99
ORDER  BY Name
LIMIT  5;
```

First rows: `"?"`, `...And Found`, `...In Translation`, `.07%`,
`A Benihana Christmas, Pts. 1 & 2`. (213 rows qualify total.)

3. Canadian customers with a company:

```sql
SELECT FirstName, LastName, Company
FROM   Customer
WHERE  Country = 'Canada'
  AND  Company IS NOT NULL
ORDER  BY LastName, FirstName;
```

Canada has 8 customers, but only 2 have a non-NULL company (the Rogers Canada
and Telus rows). François Tremblay is one of the Canadian customers excluded
because his `Company` value is NULL, so `IS NOT NULL` is doing real work here.

4. Distinct cities of customers in France, Germany, or Brazil:

```sql
SELECT DISTINCT City
FROM   Customer
WHERE  Country IN ('France', 'Germany', 'Brazil')
ORDER  BY City;
```

```
City
------------------
Berlin
Bordeaux
Brasília
Dijon
Frankfurt
Lyon
Paris
Rio de Janeiro
Stuttgart
São José dos Campos
São Paulo
```

The country list filters the customers; `DISTINCT City` returns the different
cities represented by those matching customers.

5. Playlists starting with "Classical":

```sql
SELECT Name
FROM   Playlist
WHERE  Name LIKE 'Classical%'
ORDER  BY Name;
```

4 rows: `Classical`, `Classical 101 - Deep Cuts`, `Classical 101 - Next
Steps`, `Classical 101 - The Basics`.

6. Track titles containing "Live" anywhere (case-insensitive), first 5:

```sql
SELECT Name
FROM   Track
WHERE  Name LIKE '%live%'
ORDER  BY Name
LIMIT  5;
```

5 of the 44 matches, in alphabetical order. (SQLite's `LIKE` is
case-insensitive for ASCII, so one query covers all casings.)
