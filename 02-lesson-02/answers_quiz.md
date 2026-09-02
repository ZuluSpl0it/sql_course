# Lesson 02 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file. Every query runs
against `12-data/chinook.db`; expected outputs verified against the database
as shipped in this repo. `ORDER BY` appears in reference queries for stable,
readable output; it is required only when the prompt requests an order or a
first/last subset. Compare **outputs**, not query text — many correct
phrasings exist.

## Q1 — Customers in Brazil

```sql
SELECT FirstName, LastName, Country
FROM   Customer
WHERE  Country = 'Brazil'
ORDER  BY LastName, FirstName;
```

```
FirstName   LastName    Country
----------  ----------  -------
Roberto     Almeida     Brazil
Luís        Gonçalves   Brazil
Eduardo     Martins     Brazil
Fernanda    Ramos       Brazil
Alexandre   Rocha       Brazil
```

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
SELECT InvoiceId, InvoiceDate, Total
FROM   Invoice
WHERE  InvoiceDate BETWEEN '2023-01-01' AND '2023-12-31'
  AND  Total > 15.00
ORDER  BY InvoiceDate, InvoiceId;
```

```
InvoiceId  InvoiceDate          Total
---------  -------------------  -----
194        2023-04-28 00:00:00  21.86
201        2023-05-29 00:00:00  18.86
208        2023-06-29 00:00:00  15.86
```

The three invoices (for reference): 194 → 21.86, 201 → 18.86, 208 → 15.86.
Acceptable variants: `InvoiceDate >= '2023-01-01' AND InvoiceDate <
'2024-01-01'`, or `substr(InvoiceDate,1,4) = '2023'`. Don't accept a year
filter without an end boundary that would include 2024+ (e.g.
`InvoiceDate LIKE '2023%'` is actually fine here — the strings are
zero-padded — but `LIKE '2023%'` on a non-padded date format would not be).

## Q4 — First 5 track titles containing "live" (case-insensitive)

```sql
SELECT Name
FROM   Track
WHERE  Name LIKE '%live%'
ORDER  BY Name
LIMIT  5;
```

```
Name
---------------------
A Novidade (Live)
Alive
Breaking The Law (Live)
Bring'em Back Alive
Copacabana (Live)
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

## Q6 (stretch) — First 5 customers not with Apple Inc.

```sql
SELECT FirstName, LastName, Company
FROM   Customer
WHERE  Company IS NULL
   OR  Company <> 'Apple Inc.'
ORDER  BY CustomerId
LIMIT  5;
```

```
FirstName   LastName       Company
----------  -------------  ----------------------------------------
Luís        Gonçalves      Embraer - Empresa Brasileira de Aeronáutica S.A.
Leonie      Köhler         NULL
François    Tremblay       NULL
Bjørn       Hansen         NULL
František   Wichterlová    JetBrains s.r.o.
```

The key point is the filter: `<>` alone silently drops NULL-company rows.
Include `Company IS NULL` when NULL should count as "not Apple."

---
