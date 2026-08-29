# Lesson 08 — Quiz & Your-Turn Answer Key
Attempt the Quiz and Your turn in `lesson.md` before opening this file.
This lesson only reads, so run everything against `data/chinook.db`.
---
## Your turn
### 1 — invoices per month in 2023
```sql
SELECT STRFTIME('%m', InvoiceDate) AS month, COUNT(*) AS invoices FROM Invoice WHERE STRFTIME('%Y', InvoiceDate) = '2023' GROUP BY 1 ORDER BY 1;
```

```
month  invoices
-----  --------
01     7
02     7
03     7
04     7
05     7
06     7
07     7
08     7
09     7
10     7
11     6
12     7
```
Eleven months have **7** invoices each; **November has 6**. `%m` is
zero-padded (`'01'` … `'12'`), so the plain `ORDER BY 1` on the text is
calendar order — no `CAST` needed.
### 2 — the last 30 days
```sql
SELECT COUNT(*) AS last_30_days FROM Invoice WHERE InvoiceDate >= DATE((SELECT MAX(InvoiceDate) FROM Invoice), '-30 days');
```

```
last_30_days
------------
7
```
**7** invoices. The window is `2025-11-22` through `2025-12-22` (the last
invoice date minus 30 days). `InvoiceDate` is text, so the comparison
`InvoiceDate >= DATE(…)` works because both sides are ISO-ordered strings —
same reason every date filter in the course has been legal so far.
### 3 — human-readable emails
```sql
SELECT FirstName || ' ' || LastName AS name, REPLACE(Email, '@', ' at ') AS pretty_email FROM Employee ORDER BY EmployeeId LIMIT 4;
```

```
name           pretty_email
-------------  ---------------------------
Andrew Adams   andrew at chinookcorp.com
Nancy Edwards  nancy at chinookcorp.com
Jane Peacock   jane at chinookcorp.com
Margaret Park  margaret at chinookcorp.com
```
`REPLACE(Email, '@', ' at ')` swaps the single character; the full name is
just `FirstName || ' ' || LastName`, the same concatenation Lesson 05 used.
(`||` concatenates text; with numbers it adds — another reason to know
which storage class a column holds.)
### 4 — normalize missing composers two ways
```sql
SELECT COUNT(DISTINCT COALESCE(Composer, 'Unknown')) AS coalesce_only, COUNT(DISTINCT COALESCE(NULLIF(Composer, ''), 'Unknown')) AS nullif_then_coalesce FROM Track;
```

```
coalesce_only  nullif_then_coalesce
-------------  --------------------
854            854
```
Both are **854** — the same. `NULLIF(Composer, '')` only changes the result
when `Composer` *is* `''`, and Chinook has no empty-string composers
(zero of them; the 977 missing ones are real `NULL`s, which `NULLIF` passes
through untouched). The two expressions differ only on data that spells
missing as `''`; this dataset spells missing as `NULL`, so they agree. On a
messier table the `NULLIF`-first version is the safer habit.
### 5 — stretch: age at hire
```sql
SELECT EmployeeId, FirstName || ' ' || LastName AS name, ROUND((JULIANDAY(HireDate) - JULIANDAY(BirthDate)) / 365.25) AS age_at_hire FROM Employee ORDER BY age_at_hire DESC LIMIT 3;
```

```
EmployeeId  name           age_at_hire
----------  -------------  -----------
4           Margaret Park  56.0
2           Nancy Edwards  43.0
1           Andrew Adams   40.0
```
Margaret Park is the oldest at hire, **56** (born 1947, hired 2003), then
Nancy Edwards at **43** and Andrew Adams at **40**. `JULIANDAY` differences
give exact days; dividing by 365.25 and rounding gives whole years without
any month-boundary edge cases.
---
## Quiz
### 1 — `'2021-01-01' + 7` and `'abc' + 1`
`'2021-01-01' + 7` is **2028**. `+` is numeric: SQLite applies *numeric
affinity* to both operands, and converting a text value to a number means
taking its *leading numeric prefix* — `2021` — and discarding the rest, so
the expression is `2021 + 7`. `'abc'` has no numeric prefix, so it converts
to `0`, making `'abc' + 1` equal **1**. No error, no warning — which is
exactly why you use `DATE(x, '+7 day')` for dates (Pitfall 1).
### 2 — `WHERE Composer = NULL` vs `WHERE Composer IS NULL`
`=` with a `NULL` on either side evaluates to **`UNKNOWN`**, never `TRUE`.
`WHERE` keeps only `TRUE` rows, so `Composer = NULL` returns **0** rows
while `Composer IS NULL` returns all **977**. There is no way to make `=`
match `NULL`; `IS NULL` / `IS NOT NULL` is the only correct test.
### 3 — what `DATE()` validates
Only **component ranges**: month 1–12, day 1–31, hour 0–23, and that the
string parses at all. It does **not** check whether the date exists —
February *has* a 29th in leap years, so `2021-02-29` sails through (and
`JULIANDAY` will even number it), while `2021-13-01` fails because month 13
is out of *range*. So an impossible-but-in-range date is accepted silently;
validate real-world dates yourself.
### 4 — `7/2`, `-7/2`, `7*1.0/2`
**3**, **−3**, and **3.5**. Integer `÷` integer truncates the fraction,
toward zero (`-7/2 = -3`, not `-4`); the moment one operand is a float
(`2.0/3`, `7*1.0/2`) you get a real number. It matters whenever a
report needs a real average, share, or ratio from integer counts —
`COUNT(*)/2` is the classic way to accidentally halve-then-lose the half.
### 5 — `COALESCE` vs `NULLIF`
`COALESCE(a, b, …)` returns the **first argument that is not `NULL`** —
it turns `NULL` into a default. `NULLIF(a, b)` returns **`a` unless `a = b`,
else `NULL`** — so `NULLIF(x, '')` turns an empty string into `NULL` (and
any other equal pair too). `COALESCE` never touches `''`; only `NULLIF`
can. (Example 3: 853 distinct non-`NULL` composers → 854 after
`COALESCE(…, 'Unknown')`.)
### 6 — stretch: weekends, `%W`, and unknown codes
`STRFTIME('%w', …)` is the weekday number, `0` = Sunday … `6` = Saturday,
so `IN ('0','6')` counts weekends: **117** of the 412 invoices. `%W` is
wrong here for two reasons: it's the *week-number-within-the-year* (00–53,
Monday-based), not a weekday, and it's zero-padded text, so it wouldn't
even test the way you'd write it. And `STRFTIME('%Q', …)` — a code that
doesn't exist — returns **`NULL` without any error**, so a typo'd format
code silently empties a whole column (Pitfall 4).
---
## Answers to the worked examples (for checking yourself)
| example | the numbers to check |
|---|---|
| 1 — `CASE` buckets (6 rows) | `cheap, mid, big, big, big, cheap` for invoices 1–6; counts **120 / 170 / 122** |
| 2 — revenue per year | 5 rows: **83/83/83/83/80** invoices; revenue 449.46 / 481.45 / 469.58 / 477.53 / 450.58 |
| 3 — `COALESCE` composers | 977 of 3,503 are `NULL`; distinct **853 → 854** |
| 4 — `NULLIF` + 3-valued logic | `1, a, 0, 977, c` |
| 5 — `Employee` date math | 8 rows; Andrew: 2003-08-14, 8531 days, 23.4 years; Jane the longest (8666 days, 23.7) |
