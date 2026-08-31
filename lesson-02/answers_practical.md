# Lesson 02 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

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

Canada has 8 customers; those with a company are the Rogers Canada and
Telus ones (2 rows — François Tremblay has a NULL company, so the IS NOT
NULL filter is doing real work here).

4. Countries with more than 2 customers (peek at Lesson 04):

```sql
SELECT Country, COUNT(*) AS n
FROM   Customer
GROUP  BY Country
HAVING COUNT(*) > 2
ORDER  BY n DESC, Country;
```

```
Country           n
----------------  -
USA               13
Canada            8
France            5
Brazil            5
Germany           4
United Kingdom    3
```

(If you listed rows and counted by eye, that's a perfectly valid answer
for this lesson — the point is the *set* of countries.)

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
