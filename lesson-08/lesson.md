# Lesson 08: Expressions & functions

Every lesson so far has moved *rows* around — joined them, unioned them,
put queries inside queries. This lesson shapes the *values inside* rows.
An **expression** is anything that evaluates to a single value: a literal
(`42`, `'hi'`), a column reference (`Total`), an arithmetic combination
(`Total * 1.1`), a function call (`UPPER(Name)`), or a `CASE`. The result
of an expression is one of the five storage classes from Lesson 09's
preview: `NULL`, `INTEGER`, `REAL`, `TEXT`, or `BLOB`. One warning before
anything else: **almost every function returns `NULL` when given a
`NULL`** — `LENGTH(NULL)` is `NULL`, not an error and not `0`. The date
functions get special attention because Chinook stores its dates as
**text**, which is exactly the situation those functions exist for.

**No reset needed.** This lesson only reads.

---

## 1. The concept
Here is a taste of the toolbox, one call per column, on a single row:
```sql
SELECT LENGTH('hi') AS length, UPPER('hi') AS upper, LOWER('HI') AS lower, SUBSTR('hello', 2, 3) AS substr, REPLACE('abc', 'b', 'B') AS replace, TRIM('  hi  ') AS trim, ABS(-4) AS absval, ROUND(2.5) AS round_half;
```

```
length  upper  lower  substr  replace  trim  absval  round_half
------  -----  -----  ------  -------  ----  ------  ----------
2       HI     hi     ell     aBc      hi    4       3.0
```

`LENGTH` counts characters, `UPPER`/`LOWER` change case, `SUBSTR(s, start,
len)` takes a slice (and negative starts count from the end), `REPLACE`
substitutes, `TRIM` strips spaces from both ends (`LTRIM`/`RTRIM` do one
end each), `ABS` removes a sign, and `ROUND(2.5)` rounds **half away from
zero** — `0.5 → 1`, `-1.5 → -2` — not the banker's rounding Python does.
None of these are SQL-specific; they all take a value and return a value,
and that's what makes them usable anywhere a value is accepted: the
`SELECT` list, `WHERE`, `GROUP BY`, even `ORDER BY`.
The date half of the toolbox deserves a paragraph of its own, because
Chinook's dates are **text columns** that happen to hold ISO strings like
`2021-01-01 00:00:00`. The functions `DATE()`, `TIME()`, `DATETIME()`,
`STRFTIME()`, and `JULIANDAY()` all accept such strings, parse them, and
do real calendar math. That's Example 5, and it's the reason Lesson 05's
``InvoiceDate >= …`` comparisons have been working all along: ISO-ordered
text compares correctly as text — until you try to do arithmetic with it
(Pitfall 1).

---
## 2. Worked examples
### Example 1 — `CASE`: a value-level if/elif/else
`CASE` is the only conditional *expression* in SQL — it produces a value
you can put anywhere a value goes, instead of deciding whether a row
survives. The classic use is **bucketing**: label each invoice by size.
The brackets from the course are: under $2 is **cheap**, $2–$8 **mid**,
over $8 **big**:
```sql
SELECT InvoiceId, Total, CASE WHEN Total < 2 THEN 'cheap'      WHEN Total <= 8 THEN 'mid'      ELSE 'big' END AS bucket FROM Invoice ORDER BY InvoiceId LIMIT 6;
```

```
InvoiceId  Total  bucket
---------  -----  ------
1          1.98   cheap
2          3.96   mid
3          5.94   mid
4          8.91   big
5          13.86  big
6          0.99   cheap
```

Read it like a Python chain: `WHEN Total < 2 THEN 'cheap'` is the first
branch, `WHEN Total <= 8` the second, `ELSE 'big'` the fallback. The
conditions test **top to bottom** and the first one that is `TRUE` wins.
Two details matter. First, `<=` is what makes the boundary $8.00 itself
land in `mid`, not `big`. Second, every `WHEN` that is *not* `TRUE` —
including one that is `UNKNOWN` because the value is `NULL` — is skipped
in favor of the next, so `CASE` is always `NULL`-safe in the sense that it
never errors: a `NULL` `Total` simply falls through to `ELSE`. Count the
buckets to see the shape of the store's spending:
```sql
SELECT CASE WHEN Total < 2 THEN 'cheap'      WHEN Total <= 8 THEN 'mid'      ELSE 'big' END AS bucket, COUNT(*) AS invoices FROM Invoice GROUP BY 1 ORDER BY 1;
```

```
bucket  invoices
------  --------
big     120
cheap   170
mid     122
```

**170 cheap, 122 mid, 120 big** — 412 invoices, as before. `GROUP BY 1`
groups by the first output column, the label; the same `CASE` text is
repeated, which is fine at this size (a `WITH` would be cleaner for a long
expression you need twice).
### Example 2 — `STRFTIME('%Y', …)`: revenue per year
`STRFTIME(format, date)` formats a parsed date like C's `strftime`. The
codes that matter here are numeric: `%Y` year, `%m` month (zero-padded),
`%d` day, `%w` weekday (`0` = Sunday), `%j` day of year, `%s` Unix epoch
seconds. The zero-padding is a feature: `%Y` returns the **text** `'2021'`,
and padded text sorts in the same order as the dates, so grouping and
ordering by it is safe. The store's revenue, per year:
```sql
SELECT STRFTIME('%Y', InvoiceDate) AS year, COUNT(*) AS invoices, ROUND(SUM(Total), 2) AS revenue FROM Invoice GROUP BY 1 ORDER BY 1;
```

```
year  invoices  revenue
----  --------  -------
2021  83        449.46
2022  83        481.45
2023  83        469.58
2024  83        477.53
2025  80        450.58
```

Five years, 2021 through 2025. The first four each carry **83 invoices**;
2025 has **80** because the data ends partway through that year
(its last invoice is 2025-12-22). Revenue hovers between about $450 and
$480 a year, peaking in 2022. This is the standard "group a date column
by year/month/quarter" pattern: `STRFTIME('%Y-%m', col)` for months,
`CASE` over `STRFTIME('%m', col)` for quarters.
### Example 3 — `COALESCE`: give a `NULL` a face
Of Chinook's 3,503 tracks, **977 have `Composer = NULL`** (mostly the
Brazilian jazz set). `COALESCE(a, b, …)` returns the first argument that
is not `NULL` — the standard way to give missing values a placeholder:
```sql
SELECT TrackId, Name, COALESCE(Composer, 'Unknown') AS composer FROM Track WHERE Composer IS NULL ORDER BY TrackId LIMIT 3;
```

```
TrackId  Name                                   composer
-------  -------------------------------------  --------
63       Desafinado                             Unknown
64       Garota De Ipanema                      Unknown
65       Samba De Uma Nota Só (One Note Samba)  Unknown
```

The `COALESCE(Composer, 'Unknown')` column now has 3,503 values instead of
2,526. `COALESCE` only reacts to `NULL`, never to an empty string or a
zero — more on that in Pitfall 6. And it changes *aggregates*: counting
distinct composers before and after:
```sql
SELECT COUNT(*) AS tracks, SUM(Composer IS NULL) AS null_composers, COUNT(DISTINCT Composer) AS distinct_nonnull, COUNT(DISTINCT COALESCE(Composer, 'Unknown')) AS distinct_after_coalesce FROM Track;
```

```
tracks  null_composers  distinct_nonnull  distinct_after_coalesce
------  --------------  ----------------  -----------------------
3503    977             853               854
```

853 distinct non-`NULL` composers, **854** after `COALESCE` — the
placeholder `Unknown` is itself a distinct value. If you count distinct
composers, decide explicitly whether `NULL` is a bucket; `COUNT(Composer)`
already skips `NULL`s on its own (2,526 of 3,503).
### Example 4 — `NULLIF` and the three-valued logic it protects
`NULLIF(a, b)` is the inverse of `COALESCE`'s job: it returns `a` **unless
`a` equals `b`, in which case it returns `NULL`**. The usual trick is
`NULLIF(x, '')` — normalize empty strings to `NULL` so one `NULL` path
handles both kinds of "missing":
```sql
SELECT NULLIF('', '') IS NULL AS nullif_equal, NULLIF('a', '') AS nullif_diff, (SELECT COUNT(*) FROM Track WHERE Composer = NULL) AS eq_null, (SELECT COUNT(*) FROM Track WHERE Composer IS NULL) AS is_null, CASE WHEN NULL THEN 'a' ELSE 'c' END AS case_null;
```

```
nullif_equal  nullif_diff  eq_null  is_null  case_null
------------  -----------  -------  -------  ---------
1             a            0        977      c
```

Four lessons in one row. `NULLIF('', '') IS NULL` is `1` — equal values
produce `NULL`. `NULLIF('a', '')` returns `'a'` — unequal values pass
through. The middle two columns are the most important in the whole
lesson: `WHERE Composer = NULL` matches **0** tracks, while
`WHERE Composer IS NULL` matches all **977**. `=` with a `NULL` on either
side is not `FALSE` — it is `UNKNOWN` — and `WHERE` drops `UNKNOWN` rows
just like `FALSE` ones. There is no way to make `= NULL` work; `IS NULL`
(and its negation `IS NOT NULL`) is the only correct test. The last column
shows the same rule inside `CASE`: `WHEN NULL` is `UNKNOWN`, so the chain
falls through to `ELSE`.
### Example 5 — date math on `Employee`: tenure and friends
`Employee` has eight rows, which makes it the perfect table for
per-row date expressions. Each date function takes the text date and
optional **modifiers** — `'+1 year'`, `'-30 days'`, `'start of month'` —
which do real calendar arithmetic (and, unlike bare `+`, they *do* the
math as dates, not numbers):
```sql
SELECT EmployeeId, FirstName, HireDate, DATE(HireDate, '+1 year') AS one_year_after, ROUND(JULIANDAY((SELECT MAX(InvoiceDate) FROM Invoice)) - JULIANDAY(HireDate)) AS days_service, ROUND((JULIANDAY((SELECT MAX(InvoiceDate) FROM Invoice)) - JULIANDAY(HireDate)) / 365.25, 1) AS years FROM Employee ORDER BY EmployeeId;
```

```
EmployeeId  FirstName  HireDate             one_year_after  days_service  years
----------  ---------  -------------------  --------------  ------------  -----
1           Andrew     2002-08-14 00:00:00  2003-08-14      8531.0        23.4
2           Nancy      2002-05-01 00:00:00  2003-05-01      8636.0        23.6
3           Jane       2002-04-01 00:00:00  2003-04-01      8666.0        23.7
4           Margaret   2003-05-03 00:00:00  2004-05-03      8269.0        22.6
5           Steve      2003-10-17 00:00:00  2004-10-17      8102.0        22.2
6           Michael    2003-10-17 00:00:00  2004-10-17      8102.0        22.2
7           Robert     2004-01-02 00:00:00  2005-01-02      8025.0        22.0
8           Laura      2004-03-04 00:00:00  2005-03-04      7963.0        21.8
```

`DATE(HireDate, '+1 year')` shifts the hire date forward exactly one year
(2002-08-14 → 2003-08-14) — note it does **not** carry the time part,
which is dropped. The other two columns turn *differences between dates*
into *durations*: `JULIANDAY(date)` returns a fractional day count on the
Julian calendar, so the difference of two of them is exactly the days
between them, and dividing by 365.25 converts to years. Andrew was hired
23.4 years before the last invoice, 2025-12-22. `JULIANDAY` differences
are the workhorse for "how long between these two dates?" — they handle
leap years for free (a two-year span that crosses 2016 is 731 days, not
730).

---
## 3. Practical Exercises
Do these in Jasper SQL Playground against `data/chinook.db`. This lesson only
reads, so no reset is needed. Answers in `answers_practical.md`.
1. **Invoices per month in 2023.** Use `STRFTIME('%m', …)` to show the
   invoice count for each of the twelve months of 2023. (One month differs
   from the rest — find it.)
2. **The last 30 days.** How many invoices fall in the 30-day window
   ending on the store's most recent invoice date? (Date modifiers,
   one subquery.)
3. **Human-readable emails.** For the first 4 employees, print their
   full name and their email with `@` replaced by ` at `. (`REPLACE`.)
4. **Normalize missing composers two ways.** Count distinct composers
   with `COALESCE(Composer, 'Unknown')` and again with
   `COALESCE(NULLIF(Composer, ''), 'Unknown')`. Same or different? Why?
5. **Stretch — age at hire.** For each employee, compute their age in
   whole years on their hire date from `BirthDate` and `HireDate`
   (`JULIANDAY` difference divided by 365.25, rounded), and show the
   three oldest-at-hire.
---
## 4. Pitfalls
1. **Dates are text, so `+` does number tricks, not calendar tricks.**
   `+` on a date string first coerces the string to a number by taking
   its *leading numeric prefix* — `'2021-01-01'` becomes `2021` — and the
   rest is silently ignored:
```sql
SELECT '2021-01-01' + 7 AS date_plus_7, 'abc' + 1 AS text_plus_1, DATE('2021-01-01', '+7 day') AS date_fn_plus_7_day;
```

```
date_plus_7  text_plus_1  date_fn_plus_7_day
-----------  -----------  ------------------
2028         1            2021-01-08
```

2028 is `2021 + 7`. `'abc'` has no numeric prefix, so it becomes `0`, and
`'abc' + 1` is `1`. No error, no warning. The middle column is the only
correct way to add days: `DATE('2021-01-01', '+7 day')` → `2021-01-08`.
One related fact makes plain-text date *comparison* safe but *arithmetic*
unsafe: ISO dates compare correctly as text because they're ordered
year-first (`'2021-01-01' < '2021-01-02'` is `1`), which is why
`WHERE InvoiceDate >= '2021-01-01'` has been legal in every lesson.
2. **The date functions don't validate the calendar — only the ranges.**
   SQLite checks that each component is in range (month 1–12, day 1–31,
   hour 0–23, …) and that the string *parses*, but not that the date
   exists:
```sql
SELECT DATE('2021-02-29') AS feb29, JULIANDAY('2021-02-29') AS feb29_julianday, DATE('2021-13-01') AS month13, DATE('2021-01-32') AS day32;
```

```
feb29       feb29_julianday  month13  day32
----------  ---------------  -------  -----
2021-02-29  2459274.5
```

`2021-02-29` passes (February has a day 29 *in some year*) and `JULIANDAY`
even happily assigns it a number, `2459274.5` — plausible output for an
impossible date. But month `13` and day `32` are out of *component*
range, so those return `NULL`. The upshot: garbage that *looks* like a
date produces garbage that *looks* like a date. If dates arrive from
outside, validate them with a `CHECK`-style test or `JULIANDAY(x) IS NOT
NULL` plus a real-calendar check — don't assume `DATE()` did it for you.
3. **`= NULL` never matches — there is no workaround inside `=`.**
   Comparing anything to `NULL` yields `UNKNOWN`, not `TRUE`, and `WHERE`
   keeps only `TRUE` rows:
```sql
SELECT (SELECT COUNT(*) FROM Track WHERE Composer = NULL) AS eq_null, (SELECT COUNT(*) FROM Track WHERE Composer IS NULL) AS is_null, (SELECT COUNT(*) FROM Invoice WHERE (Total - Total) IS NULL) AS null_math_kept;
```

```
eq_null  is_null  null_math_kept
-------  -------  --------------
0        977      0
```

`0` versus `977`. The third column shows the same rule biting inside
expressions you might trust: `Total - Total` is `NULL - NULL = NULL` for
every row, so `WHERE (Total - Total) IS NULL` would keep all 412 — but
flip it to `WHERE (Total - Total) = 0` and you get `0` rows, because
`NULL = 0` is `UNKNOWN`. Two habits: test `NULL` with `IS NULL` / `IS NOT
NULL`, and when you suspect a mysterious missing-row bug, check whether
an arithmetic or comparison expression in the `WHERE` silently turned
`NULL` into a dropped row.
4. **Unknown `STRFTIME` codes fail silently — the result is `NULL`.**
   If you ask for a format code SQLite doesn't have, it does not error;
   it returns `NULL` (and on this build the ICU-only codes like `%A`,
   weekday *names*, are unavailable too):
```sql
SELECT typeof(STRFTIME('%A', '2020-01-01')) AS weekday_name, typeof(STRFTIME('%Q', '2020-01-01')) AS typo_code, typeof(STRFTIME('%w', '2020-01-01')) AS weekday_num, STRFTIME('%w', '2020-01-01') AS w_value;
```

```
weekday_name  typo_code  weekday_num  w_value
------------  ---------  -----------  -------
null          null       text         3
```

`%A` and the typo'd `%Q` both come back `NULL`; the numeric `%w` works and
returns the *text* `'3'` (Wednesday). A report column that quietly turns
all-`NULL` because of one mistyped code will look, at a glance, like
"nobody has data" — so when a formatted-date column comes back empty,
check the code before checking the data. Stick to the numeric codes
(`%Y %m %d %w %W %j %s`) and spot-check `typeof(STRFTIME(…))` when in
doubt.
5. **Integer division truncates — including for negative numbers.**
   When both operands are integers, `/` is integer division:
```sql
SELECT 7 / 2 AS int_div, -7 / 2 AS neg_int_div, 7 % 2 AS rem, -7 % 2 AS neg_rem, 2.0 / 3 AS float_div, 7 * 1.0 / 2 AS scaled;
```

```
int_div  neg_int_div  rem  neg_rem  float_div          scaled
-------  -----------  ---  -------  -----------------  ------
3        -3           1    -1       0.666666666666667  3.5
```

`7/2` is `3`, and the truncation is **toward zero**: `-7/2` is `-3`, not
`-4` (that's floor), while the remainder keeps the sign of the dividend:
`-7 % 2` is `-1`. The moment one operand is a float (`2.0/3`, `7*1.0/2`)
you get a real result. The classic reporting bug is `AVG`-style math on
integers: `COUNT(*) / 2` when you meant a half. Fix it with `* 1.0` (as
in the example) or `CAST(x AS REAL)`.
6. **The empty string is not `NULL` — `COALESCE` won't save you from it.**
   `''` is a perfectly good `TEXT` value: `'' IS NULL` is `0`, and
   `COALESCE('', 'fallback')` returns `''` — the first argument is there,
   it just happens to be empty:
```sql
SELECT '' IS NULL AS empty_is_null, COALESCE('', 'fallback') AS coalesce_empty, COALESCE(NULL, 'fallback') AS coalesce_null, NULLIF('', '') IS NULL AS nullif_empty, (SELECT COUNT(*) FROM Track WHERE Composer = '') AS empty_composers;
```

```
empty_is_null  coalesce_empty  coalesce_null  nullif_empty  empty_composers
-------------  --------------  -------------  ------------  ---------------
0                              fallback       1             0
```

Chinook's data is clean on this point — zero tracks have an empty-string
composer — but in the wild, `''` and `NULL` are how two upstream systems
each spell *missing*. The fix is to normalize with `NULLIF(x, '')`
*before* `COALESCE`: `COALESCE(NULLIF(Composer, ''), 'Unknown')` treats
both as missing. Practical exercise #4 checks that this data needs no such fix, and
knowing that is the whole point.

---
## 5. Recap
- **An expression is a value:** literal, column, arithmetic, function, or
  `CASE`; it evaluates to one of the five storage classes, and most
  functions map `NULL` in → `NULL` out.
- **`CASE`** is the value-level if/elif/else: first `TRUE` branch wins,
  `UNKNOWN`/`FALSE` branches are skipped, `ELSE` catches the rest. Use it
  to bucket (`cheap/mid/big`) or to relabel; it never errors on `NULL`.
- **String functions** — `LENGTH`, `UPPER`/`LOWER`, `SUBSTR` (negative
  start counts from the end), `REPLACE`, `TRIM`/`LTRIM`/`RTRIM` — work on
  `TEXT`; `ROUND` rounds half *away from zero*.
- **Date functions parse text dates and do real calendar math:**
  `DATE/TIME/DATETIME`, `STRFTIME('%Y','%m','%d','%w','%j','%s')`,
  `JULIANDAY` differences for durations, and modifiers like
  `'+1 year'`, `'-30 days'`, `'start of month'`. But: bare `+` on a date
  string is number arithmetic; the calendar is only *range*-validated
  (`2021-02-29` passes, `2021-13-01` is `NULL`); and unknown `STRFTIME`
  codes return `NULL`, not an error.
- **`NULL` tools:** `COALESCE(a, b, …)` = first non-`NULL` (never touches
  `''`); `NULLIF(a, b)` = `a` unless `a = b`, else `NULL` (so
  `NULLIF(x, '')` normalizes empty strings); `= NULL` is always
  `UNKNOWN` — only `IS [NOT] NULL` works.
- **Integer division truncates toward zero** (`7/2 = 3`, `-7/2 = -3`);
  make one operand a float (`* 1.0`) for real division.
Next up, **Lesson 09: Schema & constraints** — where the declared types
you've been reading as text all along (`NVARCHAR(40)`, `DATETIME`,
`NUMERIC(10,2)`) actually come from, and how SQLite maps them onto the
five storage classes this lesson has been living in. It's the first
write-lesson since Lesson 03: you'll reload `data/chinook.db` for a clean
database before touching anything.

## 6. Quiz
1. What does `'2021-01-01' + 7` evaluate to, and *why*? What about
   `'abc' + 1`? (Pitfall 1 is the lesson; this is the mechanism.)
2. `Track` has 977 rows with `Composer IS NULL`. How many rows do
   `WHERE Composer = NULL` and `WHERE Composer IS NULL` each return, and
   what does `=` actually produce when one side is `NULL`?
3. `DATE('2021-02-29')` returns the text `'2021-02-29'` — a date that
   does not exist — while `DATE('2021-13-01')` returns `NULL`. What is
   SQLite actually validating, and what is it not?
4. In SQLite 3.31, what are `7 / 2`, `-7 / 2`, and `7 * 1.0 / 2`? When
   does the difference between them matter for a report?
5. In one sentence each: what is `COALESCE(a, b)`, and what is
   `NULLIF(a, b)`? Which of the two turns an empty string into `NULL`,
   and which turns `NULL` into a default?
6. **Stretch.** `STRFTIME('%w', InvoiceDate)` gives `0` for Sunday and `6`
   for Saturday. How many of the 412 invoices fall on weekends? Why would
   using `%W` (capital) be wrong even though it also starts at something
   small? And what does `STRFTIME('%Q', …)` — a code that doesn't exist —
   return, and what does that make it dangerous?
---
