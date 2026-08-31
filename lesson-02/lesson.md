# Lesson 02: Filtering Rows

Up to now, every `SELECT` has returned **all** the rows of its table (or a
page of them). A database of 3,503 tracks is rarely what you actually want —
you want *the* French customers, *the* 2023 invoices, *the* metal tracks.
That's the job of the `WHERE` clause.

`WHERE` sits after `FROM` and before `ORDER BY`, and it takes a **condition**
— an expression that the database evaluates for each row. The row is kept if
the condition is TRUE; it's dropped if FALSE. There's a third state,
*unknown* (NULL), which we'll meet properly at the end of the lesson because
it causes more real bugs than any other topic in SQL.

The clause order you now know is:

```
SELECT → FROM → WHERE → ORDER BY → LIMIT / OFFSET
```

## 1. The concept

### 1.1 WHERE with a single comparison

```sql
SELECT FirstName, LastName, Country
FROM   Customer
WHERE  Country = 'France';
```

The condition `Country = 'France'` is checked row by row. Only the rows
where it's true come out. Comparison operators:

| Operator | Meaning |
|----------|---------|
| `=`      | equal |
| `<>`     | not equal (some dialects also accept `!=`) |
| `<` `>`  | less / greater than |
| `<=` `>=`| less-or-equal / greater-or-equal |

`<>` and `!=` are interchangeable in SQLite. Text comparisons use
single quotes (`'France'`); numbers don't (`1.99`).

### 1.2 Combining conditions — AND, OR, NOT

```sql
SELECT FirstName, LastName
FROM   Customer
WHERE  Country = 'USA'
  AND  Company IS NOT NULL;
```

- `AND` — **both** sides must be true.
- `OR`  — **at least one** side true.
- `NOT` — flips a condition (`NOT Country = 'France'`).

**Precedence:** `NOT` binds tightest, then `AND`, then `OR`. That means

```sql
A OR B AND C      -- parses as  A OR (B AND C)
```

not `(A OR B) AND C`. When in doubt, **write parentheses** — they never hurt
and they make intent explicit:

```sql
WHERE  (Country = 'France' OR Country = 'Germany')
  AND  Company IS NOT NULL
```

We'll see in the examples exactly what goes wrong when you drop those
parentheses.

### 1.3 Membership — IN and NOT IN

```sql
SELECT Country, COUNT(*)
FROM   Customer
WHERE  Country IN ('France', 'Germany', 'Brazil')
GROUP  BY Country;
```

`x IN (a, b, c)` is shorthand for `x = a OR x = b OR x = c`. Its negation is
`NOT IN`. Use it for "one of this list" — much cleaner than a string of
`OR`s. (There's a NULL trap in `NOT IN` we'll flag in Pitfalls.)

### 1.4 Ranges — BETWEEN

```sql
SELECT InvoiceId, Total
FROM   Invoice
WHERE  Total BETWEEN 10 AND 20;
```

`x BETWEEN a AND b` is **inclusive** on both ends — equivalent to
`x >= a AND x <= b`. Its negation is `NOT BETWEEN`. It works on numbers and
on text/dates that compare in a sensible order (Chinook stores dates as
`'YYYY-MM-DD ...'` strings, which sort chronologically, so `BETWEEN` works
on them directly).

### 1.5 Patterns — LIKE

```sql
SELECT Name
FROM   Playlist
WHERE  Name LIKE 'Brazil%';
```

`LIKE` does pattern matching with two wildcards:

- `%` — matches **zero or more** of any character.
- `_` — matches **exactly one** of any character.

Common shapes:

| Pattern | Matches |
|---------|---------|
| `'Brazil%'` | starts with `Brazil` |
| `'%live%'`  | contains `live` |
| `'%.'`      | ends with a dot |
| `'A_c%'`    | `A`, any single char, `c`, anything |

**SQLite's `LIKE` is case-insensitive** by default for ASCII: `'a' LIKE 'A'`
is true. (Other databases differ — PostgreSQL's `LIKE` is case-sensitive;
use `ILIKE` there for case-insensitive.) If you need case-sensitive matching
in SQLite, use the `GLOB` operator or the `LOWER()` function (Lesson 08).

### 1.6 NULL — the thing you can't compare

A missing value is not an empty string and not zero — it's **unknown**,
written `NULL`. The single most important rule in all of SQL:

> **You can never use `=` to test for NULL. `x = NULL` is never true.**

To ask "is this missing?", use the dedicated operators:

```sql
SELECT FirstName, LastName
FROM   Customer
WHERE  Company IS NULL;
```

and its negation `IS NOT NULL`. Why `=` fails is the subject of the next
section.

### 1.7 Three-valued logic (read this — it's the whole game)

Ordinary logic has two values, TRUE and FALSE. SQL has **three**: TRUE,
FALSE, and **UNKNOWN** (when a NULL is involved). The rules that matter:

| Operation | Rule you need |
|-----------|---------------|
| `NULL = anything` | UNKNOWN |
| `NULL <> anything` | UNKNOWN |
| `TRUE AND FALSE`  | FALSE |
| `TRUE AND UNKNOWN`| UNKNOWN |
| `FALSE AND UNKNOWN`| **FALSE** |
| `TRUE OR UNKNOWN` | TRUE |
| `FALSE OR UNKNOWN`| UNKNOWN |

And the rule that bites: **`WHERE` keeps only rows whose condition is
TRUE. UNKNOWN is not kept.** It's treated like FALSE for filtering.

That's why this returns *nothing* you'd expect:

```sql
SELECT * FROM Customer WHERE Company = NULL;   -- 0 rows, always
```

Every `Company = NULL` compares to UNKNOWN, and WHERE drops UNKNOWN. The
only rows where `Company` is actually missing are found by
`WHERE Company IS NULL`.

The same logic means this classic is **wrong**:

```sql
SELECT * FROM Customer WHERE Company <> 'Apple Inc.';
```

You'd hope it means "everyone who isn't Apple". But for the 49 customers
whose `Company` is NULL, the test `NULL <> 'Apple Inc.'` is UNKNOWN — so
those 49 rows are **silently dropped**, along with no one else. The correct
"everyone except Apple, including the ones with no company" is:

```sql
SELECT * FROM Customer
WHERE  Company IS NULL
   OR  Company <> 'Apple Inc.';
```

Hold that thought — Example 7 makes it concrete, and Pitfall 3 returns to it.

## 2. Worked examples

### Example 1 — the basic filter

Goal: the French customers.

```sql
SELECT FirstName, LastName, Country
FROM   Customer
WHERE  Country = 'France'
ORDER  BY LastName, FirstName;
```

```
FirstName    LastName   Country
-----------  ---------  -------
Camille      Bernard    France
Marc         Dubois     France
Wyatt        Girard     France
Dominique    Lefebvre   France
Isabelle     Mercier    France
```

5 rows out of 59. `ORDER BY` after `WHERE` sorts only the surviving rows.

### Example 2 — an inequality and a number

Goal: the tracks that cost more than a dollar (the premium-priced ones).

```sql
SELECT Name, UnitPrice
FROM   Track
WHERE  UnitPrice > 1.00
ORDER  BY Name
LIMIT  5;
```

```
Name                              UnitPrice
--------------------------------  ---------
"?"                               1.99
...And Found                      1.99
...In Translation                 1.99
.07%                              1.99
A Benihana Christmas, Pts. 1 & 2  1.99
```

There are 213 of them. Notice `> 1.00` — the price is a number, so no quotes.

### Example 3 — AND with a NULL on one side

Goal: US customers who *have* a company on file.

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

3 rows. The `AND` needs **both** to be true. The US has 13 customers, but
only 3 also have a non-null company — the other 10 have `Company` NULL and
are dropped by `IS NOT NULL`. (An `IS NOT NULL` test is never UNKNOWN —
it's a definite TRUE or FALSE — which is exactly why it's the safe way to
combine with AND.)

### Example 4 — the OR-with-parentheses trap

Goal: customers in France **or** Germany who have a company.

```sql
SELECT FirstName, LastName, Company, Country
FROM   Customer
WHERE  (Country = 'France' OR Country = 'Germany')
  AND  Company IS NOT NULL;
```

```
(no rows)
```

Empty — and that's the correct answer, because in this database **every**
French and German customer has `Company` NULL. Now watch the same intent
written without parentheses:

```sql
SELECT FirstName, LastName, Company, Country
FROM   Customer
WHERE  Country = 'France' OR Country = 'Germany' AND Company IS NOT NULL;
```

Because `AND` binds tighter than `OR`, this is read as

```
Country = 'France'  OR  (Country = 'Germany' AND Company IS NOT NULL)
```

So it returns all 5 French customers **plus** zero Germans (no German has a
company) — 5 rows, a *different* set than the parenthesized version's 0.
Same words, different result. Parentheses are how you keep them the same.

### Example 5 — IN for a short list

Goal: customers from three countries at once.

```sql
SELECT Country, COUNT(*) AS how_many
FROM   Customer
WHERE  Country IN ('France', 'Germany', 'Brazil')
GROUP  BY Country
ORDER  BY how_many DESC, Country;
```

```
Country       how_many
------------  --------
Brazil        5
France        5
Germany       4
```

14 customers total, grouped by country. (`GROUP BY`/`COUNT` are Lesson 04 —
here they just make the answer readable; you could also just list the rows.)
The `IN` list is doing the work of `= 'France' OR = 'Germany' OR = 'Brazil'`.

### Example 6 — BETWEEN on a date stored as text

Goal: all invoices from 2023.

```sql
SELECT COUNT(*)
FROM   Invoice
WHERE  InvoiceDate BETWEEN '2023-01-01' AND '2023-12-31';
```

```
COUNT(*)
--------
83
```

Chinook stores `InvoiceDate` as a text string in `YYYY-MM-DD HH:MM:SS`
form, which happens to sort chronologically — so a string `BETWEEN` works as
a date range. Both endpoints are inclusive, and because the month/day parts
are zero-padded, lexicographic order == calendar order. (You'll see cleaner
date handling with `strftime`/`date()` in Lesson 08.)

### Example 7 — the NOT-equal NULL trap, quantified

Goal: everyone who is *not* Apple Inc. — including people with no company.

Wrong way (drops the 49 NULLs):

```sql
SELECT COUNT(*) FROM Customer WHERE Company <> 'Apple Inc.';   -- 9
```

Right way (keeps them):

```sql
SELECT COUNT(*)
FROM   Customer
WHERE  Company IS NULL
   OR  Company <> 'Apple Inc.';                                 -- 58
```

The difference — 58 vs 9 — is exactly the 49 customers with `Company` NULL
(58 − 9 = 49). If a number in a report is mysteriously too small, this is
the first thing to check.

## 3. Your turn

Open-ended; run them in Jasper SQL Playground and judge your own output against what you
now understand. No answers in this file.

1. List the German customers (names and country).
2. List tracks that cost exactly 1.99, in alphabetical order, first 5.
3. List customers who are in Canada **and** have a company on file.
4. List the distinct countries that have more than 2 customers.
   (You may peek at Lesson 04's `GROUP BY`/`HAVING` if you want — or list
   the rows and count by eye.)
5. List playlist names that start with "Classical".
6. (stretch) List track titles that contain the word "Live" *anywhere*,
   case-insensitive, first 5.

## 4. Quiz

Write a query for each, run it, compare your **output** to `answers.md`.
Many correct phrasings exist; the key shows one good one and notes what
would *not* count.

1. How many customers are in Brazil?
2. List the US customers who have a company on file — names and company.
3. How many invoices in 2023 had a total greater than 15.00?
4. How many track titles contain the word "live" (case-insensitive)?
5. List the customers in France or Germany who have **no** company on file.
   (Names and country.)
6. (stretch) How many customers are *not* with Apple Inc., counting people
   with no company as "not Apple"?

## 5. Pitfalls

**Pitfall 1 — `= NULL` / `= NULL` returns nothing, every time.**
`x = NULL` is UNKNOWN, and `WHERE` drops UNKNOWN. Use `x IS NULL` (or
`IS NOT NULL`). This is the single most common beginner bug in SQL, and it
produces the eerily confident "0 rows" result.

**Pitfall 2 — `<>` / `NOT IN` silently drop NULLs.**
`Company <> 'Apple Inc.'` drops every NULL-company row, because
`NULL <> 'Apple'` is UNKNOWN, not TRUE. If you're filtering "not X" and
your numbers look low, you're probably eating NULLs. The fix is
`col IS NULL OR col <> 'X'`. For `NOT IN`, a NULL *inside the list* makes
the whole thing return nothing — see Pitfall 3.

**Pitfall 3 — `NOT IN` with a NULL in the list breaks completely.**
If the list value could be NULL (a column reference, a subquery), and any
list row is NULL, then `x NOT IN (…)` is UNKNOWN for *every* x and returns
zero rows. Safer patterns: use `NOT EXISTS` (Lesson 07) or rewrite with
`LEFT JOIN … IS NULL`. Keep `NOT IN` for literal constant lists where you
know there are no NULLs.

**Pitfall 4 — `AND` beats `OR` — and people get it wrong.**
`a OR b AND c` is `a OR (b AND c)`. If you mean `(a OR b) AND c`, write the
parentheses. There is no scenario where the missing parens "just work"
reliably; the data changes and so does your answer.

**Pitfall 5 — `LIKE` wildcards are not regex, and `%` is greedy.**
`LIKE 'a%b'` matches any string starting with `a` and ending with `b`,
including `ab`. It is not a regular expression (no `.*`, no `+`, no
`[...]`). And a lone `%` matches everything — `WHERE Name LIKE '%'` is the
same as no filter at all, which is a handy "count the table" trick but a
shocking one if you meant a literal percent sign.

**Pitfall 6 — Quotes around numbers (and vice versa) — the silent cast.**
`WHERE UnitPrice > '1'` works in SQLite (it casts the text to a number) but
it's a warning sign, and in other databases it can do the *opposite* cast
and give you wrong answers. Numbers unquoted, text quoted — always.

## 6. Recap

- `WHERE` keeps only rows whose condition is TRUE; it sits after `FROM`,
  before `ORDER BY`.
- Compare with `=`, `<>`, `<`, `>`, `<=`, `>=`. Numbers unquoted, text in
  single quotes.
- Combine with `NOT` > `AND` > `OR` (precedence). **Use parentheses.**
- `IN (…)` for "one of these"; `NOT IN` with care (NULL in the list = no
  rows).
- `BETWEEN a AND b` is inclusive on both ends; works on numbers and on
  well-formatted date strings.
- `LIKE` with `%` (many/zero) and `_` (one). Case-insensitive in SQLite.
- **`NULL` is unknown, not a value.** Test it with `IS NULL` / `IS NOT
  NULL`, never `= NULL`.
- Three-valued logic: any comparison with NULL is UNKNOWN, and WHERE drops
  UNKNOWN — which is why `<>` and `NOT IN` quietly eat your NULL rows.

## 7. Look ahead

Lesson 03 stops reading and starts **writing**: `INSERT`, `UPDATE`, `DELETE`,
and how to wrap them in a transaction (`BEGIN` / `COMMIT` / `ROLLBACK`) so a
mistake never corrupts your data. You'll also create your first table, so
you'll understand exactly what a schema is — which sets up Lesson 09's deep
dive into constraints and design.
