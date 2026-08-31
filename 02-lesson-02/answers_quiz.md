# Lesson 02 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file. Every query runs
against `12-data/chinook.db`; expected outputs verified against the database
as shipped in this repo. Compare **outputs**, not query text — many correct
phrasings exist.

## Q1 — How many customers are in Brazil?

```sql
SELECT COUNT(*)
FROM   Customer
WHERE  Country = 'Brazil';
```

```
COUNT(*)
--------
5
```

Also fine: `SELECT Country, COUNT(*) FROM Customer WHERE Country = 'Brazil'
GROUP BY Country;`. Don't accept a query without a `WHERE` that counts all
59 customers.

## Q2 — US customers with a company on file (names + company)

```sql
SELECT FirstName, LastName, Company
FROM   Customer
WHERE  Country = 'USA'
  AND  Company IS NOT NULL
ORDER  BY FirstName;
```

```
FirstName  LastName  Company
---------  --------  ---------------------
Frank      Harris    Google Inc.
Jack       Smith     Microsoft Corporation
Tim        Goyer     Apple Inc.
```

3 rows. **Don't accept** a version that omits `Company IS NOT NULL` — the
US has 13 customers, and only 3 have a company; the missing filter would
return 10 extra NULL-company rows.

## Q3 — Invoices in 2023 with a total greater than 15.00

```sql
SELECT COUNT(*)
FROM   Invoice
WHERE  InvoiceDate BETWEEN '2023-01-01' AND '2023-12-31'
  AND  Total > 15.00;
```

```
COUNT(*)
--------
3
```

The three invoices (for reference): 194 → 21.86, 201 → 18.86, 208 → 15.86.
Acceptable variants: `InvoiceDate >= '2023-01-01' AND InvoiceDate <
'2024-01-01'`, or `substr(InvoiceDate,1,4) = '2023'`. Don't accept a year
filter without an end boundary that would include 2024+ (e.g.
`InvoiceDate LIKE '2023%'` is actually fine here — the strings are
zero-padded — but `LIKE '2023%'` on a non-padded date format would not be).

## Q4 — How many track titles contain "live" (case-insensitive)?

```sql
SELECT COUNT(*)
FROM   Track
WHERE  Name LIKE '%live%';
```

```
COUNT(*)
--------
44
```

This is case-insensitive *in SQLite* — so it catches `Live`, `LIVE`,
`live`, and mixed case with one query. (In PostgreSQL you'd write
`ILIKE '%live%'`.) The matches include things like `Who Wants To Live
Forever` and `Bring'em Back Alive` — the substring is what's matched, not
the whole word.

## Q5 — Customers in France or Germany with no company on file

```sql
SELECT FirstName, LastName, Country
FROM   Customer
WHERE  (Country = 'France' OR Country = 'Germany')
  AND  Company IS NULL
ORDER  BY Country, LastName, FirstName;
```

```
FirstName    LastName   Country
-----------  ---------  -------
Camille      Bernard    France
Marc         Dubois     France
Wyatt        Girard     France
Dominique    Lefebvre   France
Isabelle     Mercier    France
Leonie       Köhler     Germany
Hannah       Schneider  Germany
Niklas       Schröder   Germany
Fynn         Zimmermann Germany
```

9 rows — and the punchline: **all** French and German customers have
`Company` NULL, so this list is identical to every customer in those two
countries. Note the parentheses: without them, `A OR B AND C` would parse
as `A OR (B AND C)` and return a different set (Pitfall 4).

## Q6 (stretch) — Not with Apple Inc., counting NULL companies as "not Apple"

```sql
SELECT COUNT(*)
FROM   Customer
WHERE  Company IS NULL
   OR  Company <> 'Apple Inc.';
```

```
COUNT(*)
--------
58
```

Check the arithmetic: 59 customers − 1 Apple customer = 58. The naive
`WHERE Company <> 'Apple Inc.'` returns **9** — because it silently drops
the 49 NULL-company rows (58 − 9 = 49). That gap *is* the lesson: `<>`
against NULL is UNKNOWN, and WHERE drops UNKNOWN. If a student's answer is
9, that's the bug to point at.

---
