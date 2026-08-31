# Lesson 08 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)
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
