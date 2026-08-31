# Lesson 04: Aggregation & Groups

So far every `SELECT` has returned one row per matching row. But the
questions that actually get asked in a business are summaries: *"How many
tracks are in the catalog?"* *"What's the average invoice?"* *"Which
genre has the most tracks?"* *"Which customers spent the most?"* None of
those is answered by listing rows — you have to **collapse** many rows
into one. That's what this lesson teaches: the five aggregate functions,
`GROUP BY`, and the filter that works on groups, `HAVING`.

**No reset needed.** This lesson only reads.

---

## 1. The concept

### The five aggregate functions

All five take a set of values and return **one value**:

| Function | Returns | Typical use |
|---|---|---|
| `COUNT(expr)` | how many values (rows) | "how many tracks" |
| `SUM(expr)`  | total | "total revenue" |
| `AVG(expr)`  | average | "average invoice" |
| `MIN(expr)`  | smallest | "cheapest track" |
| `MAX(expr)`  | largest | "longest track" |

Two important flavors of `COUNT`:

- `COUNT(*)` — counts **rows** (every row, NULLs included).
- `COUNT(column)` — counts only the rows where that column is **not NULL**.

That difference is not pedantic; it's the most common "wait, my count is
wrong?" moment in this course. We'll meet it in Example 1.

### `GROUP BY` — aggregate *per group*

Without `GROUP BY`, an aggregate collapses the **whole** filtered table into
one row. With `GROUP BY somecolumn`, the table is split into groups (one per
distinct value of `somecolumn`) and each aggregate is computed **separately
per group**, returning one row per group.

### `WHERE` vs `HAVING` — the key distinction

- `WHERE` filters **rows, before** grouping.
- `HAVING` filters **groups, after** grouping.

You can write a `HAVING` condition with an aggregate (`HAVING COUNT(*) > 5`)
but you **cannot** write one in `WHERE` (`WHERE COUNT(*) > 5` is illegal —
the rows haven't been grouped yet, so there's no count to compare). This is
the single most common mistake people make learning aggregation, so we spend
an example on it.

---

## 2. Worked examples

### Example 1 — the whole table as one group, and `COUNT(*)` vs `COUNT(column)`

The most basic aggregate: how many tracks?

```sql
SELECT COUNT(*) FROM Track;
```

```
COUNT(*)
--------
3503
```

One row, one number: the whole `Track` table collapsed into a count.

Now the subtle one. How many tracks have a composer?

```sql
SELECT COUNT(Composer) FROM Track;
```

```
COUNT(Composer)
---------------
2526
```

Only 2,526, not 3,503 — because 977 tracks have a `NULL` composer, and
`COUNT(Composer)` skips NULLs. If you'd used `COUNT(*)` you'd get all 3,503.
**Rule of thumb:** `COUNT(*)` = "how many rows"; `COUNT(column)` = "how many
rows where that column is present." Keep them straight and most count bugs
disappear.

### Example 2 — `SUM`, `AVG`, `MIN`, `MAX` in one query

You can stack several aggregates in a single `SELECT`:

```sql
SELECT MIN(UnitPrice) AS cheapest,
       MAX(UnitPrice) AS priciest,
       ROUND(AVG(UnitPrice), 2) AS average,
       ROUND(SUM(UnitPrice), 2) AS catalog_value
FROM   Track;
```

```
cheapest  priciest  average  catalog_value
--------  --------  -------  -------------
0.99      1.99      1.05     3680.97
```

Read it: every track is $0.99 or $1.99 (that's how the catalog is priced),
the average sits just over a dollar, and if you bought all 3,503 tracks it
would cost about $3,681. `ROUND(x, 2)` is just a cleanup step so the average
and sum don't spew 15 decimal places — you learned `AS` back in Lesson 01,
and it works fine on expressions too.

### Example 3 — `GROUP BY`: one number per genre

Now split the table. How many tracks in each genre?

```sql
SELECT GenreId,
       COUNT(*) AS tracks
FROM   Track
GROUP  BY GenreId
ORDER  BY tracks DESC
LIMIT  5;
```

```
GenreId  tracks
-------  ------
1        1297
7        579
3        374
4        332
2        130
```

The table was split into 25 groups (one per `GenreId`), and `COUNT(*)` was
computed inside each group, so we get one row per genre. Rock (genre 1)
dominates with 1,297 tracks.

Two rules are doing the work here, and they're easy to violate:

- **Every column in `SELECT` must be either grouped or aggregated.** We
  selected `GenreId` (the grouping key) and `COUNT(*)` (an aggregate) — both
  allowed. If we'd also selected `Name` (a plain track name) we'd be asking
  "which name?" for a group of 1,297 tracks, which is meaningless; SQLite
  would let you but hand back an arbitrary row's value (more on that in
  Pitfalls).
- **You don't have to order the groups.** `GROUP BY` returns groups in an
  unspecified order (often the group key), so the `ORDER BY tracks DESC` is
  what actually puts the biggest genre on top.

### Example 4 — multiple grouping columns

Group by more than one column to get a finer breakdown. Invoices per
country, per year:

```sql
SELECT BillingCountry,
       substr(InvoiceDate, 1, 4) AS year,
       COUNT(*) AS invoices
FROM   Invoice
GROUP  BY BillingCountry, year
ORDER  BY BillingCountry, year
LIMIT  8;
```

```
BillingCountry    year  invoices
--------------    ----  --------
Argentina         2022  3
Argentina         2023  1
Argentina         2025  3
Australia         2021  3
Australia         2022  1
Australia         2023  1
Australia         2024  2
Austria           2021  1
```

The groups are now the *combination* of `(country, year)` — a separate group
for Argentina-2022, Argentina-2023, etc. Order the keys by importance:
putting `year` first would have grouped by year, then split each year into
countries. `substr(InvoiceDate,1,4)` extracts the year from the
`YYYY-MM-DD HH:MM:SS` string (we'll get proper date functions in Lesson 08).

### Example 5 — `HAVING`: filter the groups

Now the filter that works on aggregates. Which customers bought an invoice
bigger than $13.50?

Start with the tempting version that looks almost right:

```sql
SELECT COUNT(*)
FROM   Invoice
WHERE  Total > 13.50;
```

```
COUNT(*)
--------
61
```

Seems to answer it: 61. **It doesn't.** This counts *invoice rows* whose
total clears $13.50. The question was about *customers* — and a customer who
bought two big invoices is one customer, not two. The correct version
groups first, then asks about each group:

```sql
SELECT CustomerId,
       MAX(Total) AS biggest
FROM   Invoice
GROUP  BY CustomerId
HAVING MAX(Total) > 13.50
ORDER  BY biggest DESC
LIMIT  5;
```

```
CustomerId  biggest
----------  -------
6           25.86
26          23.86
45          21.86
46          21.86
7           18.86
```

(…and 54 more customers if you drop the `LIMIT` — everyone's biggest
invoice is over $13.50, though the top ones tower over the rest.) Notice
the flow, which is always the same three steps:

1. `GROUP BY CustomerId` — make one group per customer.
2. `MAX(Total)` — compute the biggest invoice per group.
3. `HAVING MAX(Total) > 13.50` — keep only the groups where that max clears
   the bar.

`HAVING` is where you're allowed to reference aggregates, because it runs
*after* the groups exist. `WHERE` runs *before* — the rows haven't been
grouped yet, so there's no `MAX(Total)` to compare. Try it and SQLite tells
you:

```
SELECT CustomerId, MAX(Total)
FROM   Invoice
WHERE  MAX(Total) > 13.50      -- no such thing
GROUP  BY CustomerId;

-- Error: misuse of aggregate: MAX()
```

And that's the rule to memorize: **row-level conditions in `WHERE`,
group-level conditions in `HAVING`** — anything containing an aggregate
belongs in `HAVING`.

### Example 6 — `COUNT(DISTINCT ...)`: count unique values

How many different customers actually appear in the invoices?

```sql
SELECT COUNT(DISTINCT CustomerId) FROM Invoice;
```

```
COUNT(DISTINCT CustomerId)
--------------------------
59
```

There are 412 invoice rows, but only 59 distinct customers — each customer
bought several times. `DISTINCT` inside `COUNT` counts unique values rather
than rows. (You also saw `DISTINCT` on its own in Lesson 01; this is the
same idea applied inside an aggregate.)

---

## 3. Practical Exercises

Do these in Jasper SQL Playground against `12-data/chinook.db`. This lesson only
reads, so no reset is needed. Check `answers_practical.md` when done.

1. How many **albums** are there? Then: what's the average track length in
   milliseconds across the whole `Track` table?
2. Count the **distinct** billing countries that appear in `Invoice`.
3. For each `MediaTypeId`, how many tracks? Order by the count, biggest
   first.
4. What's the cheapest and most expensive **invoice** (not track)?
5. Group `Invoice` by `CustomerId` and show the 3 customers with the
   highest total spending (`SUM(Total)`).

---

## 4. Pitfalls

1. **`WHERE` can't see aggregates.** `WHERE SUM(Total) > 100` is an error.
   Row-level filtering happens before grouping; the sum doesn't exist yet.
   Use `HAVING` for anything that mentions an aggregate.

2. **`COUNT(*)` vs `COUNT(column)` silently differ.** `COUNT(*)` counts
   rows; `COUNT(column)` counts non-NULL values of that column. On `Track`,
   that's 3,503 vs 2,526 (977 null composers). If a count looks too low or
   too high, this is the usual suspect.

3. **A bare column next to `GROUP BY` is undefined in standard SQL.**
   SQLite *allows* `SELECT Country, FirstName, COUNT(*) FROM Customer
   GROUP BY Country` but the `FirstName` it hands back is an **arbitrary
   member of the group** (we got `Frank` for the USA group). It looks right
   and isn't. Only select grouping columns or aggregates; anything else is
   a landmine that will bite you the moment you move to PostgreSQL, which
   rejects it outright.

4. **`HAVING` without `GROUP BY` is an error in SQLite.** `SELECT COUNT(*)
   FROM Invoice HAVING COUNT(*) > 100` fails with "a GROUP BY clause is
   required before HAVING." SQLite is stricter here than some other engines;
   if you want to guard a whole-table aggregate, wrap it differently (e.g.
   a subquery, Lesson 07).

5. **Ordering the groups is not part of grouping.** `GROUP BY` returns
   groups in no meaningful order. If your summary needs to be sorted
   (biggest first, alphabetical), add the `ORDER BY` — it's a separate
   clause, not a property of `GROUP BY`.

6. **Aggregates over an empty set.** `SUM`, `AVG`, `MIN`, `MAX` on a group
   with zero rows return `NULL` (not 0). `COUNT` is the exception and
   returns 0. So `AVG(Total)` for a country with no invoices is `NULL`, and
   comparing `NULL > 5` in a `HAVING` clause keeps no row (Lesson 02's
   three-valued logic, again).

---

## 5. Recap

- Five aggregates, all return one value: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
- `COUNT(*)` counts rows; `COUNT(col)` counts non-NULL values.
- No `GROUP BY` → the whole filtered table is one group, one result row.
- `GROUP BY a, b, ...` → one group per distinct combination; every `SELECT`
  column must be a grouping key or an aggregate.
- `WHERE` filters rows **before** grouping; `HAVING` filters groups
  **after** and is where aggregates live.
- `COUNT(DISTINCT col)` counts unique values.
- `GROUP BY` doesn't order; add `ORDER BY`.

## 6. Quiz

Answer without scrolling up. The key is in `answers_quiz.md`.

1. Write a query that returns the **total revenue** (`SUM(Total)`) per
   billing country, biggest spenders first. (No `HAVING` needed here — just
   `GROUP BY` + `ORDER BY`.)
2. Using `HAVING`, return the `CustomerId`s of customers who have **more
   than 6 invoices**. (Hint: one customer is the exception — how many does
   everyone else have?)
3. Write a query that returns the **average** invoice total per billing
   country, but **only for countries whose average is above $6**.
4. True or false: `WHERE COUNT(*) > 5` is valid SQL.
5. `COUNT(*)` and `COUNT(Composer)` on the `Track` table give different
   results. Which is larger, and why?
6. (Stretch) In one query: for each `GenreId`, the number of tracks **and**
   the total catalog value (`SUM(UnitPrice)`), sorted by total value
   descending, top 5.

---

## 7. Look ahead

Lesson 05 introduces **joins**: the catalog is really 11 interlocking tables,
and questions such as "which tracks are on the *Rock Classics* album, and who
wrote the *album*?" need related rows pulled into one result.
