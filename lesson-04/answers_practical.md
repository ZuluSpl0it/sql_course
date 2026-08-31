# Lesson 04 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

**1.** Albums: `SELECT COUNT(*) FROM Album;` → **347**.
Average track length: `SELECT ROUND(AVG(Milliseconds), 0) FROM Track;` →
**393,599 ms** (about 6 min 34 s per track).

**2.** `SELECT COUNT(DISTINCT BillingCountry) FROM Invoice;` → **24**
customers bought from 24 different countries (the `Customer` table has 52
countries — not everyone has bought).

**3.**

```sql
SELECT MediaTypeId,
       COUNT(*) AS tracks
FROM   Track
GROUP  BY MediaTypeId
ORDER  BY tracks DESC;
```

```
MediaTypeId  tracks
-----------  ------
1            3034
2            237
3            214
5            11
4            7
```

(5 types total: 3,034 + 237 + 214 + 11 + 7 = 3,503 ✓ — a handy way to sanity-
check that your groups covered every row exactly once.)

**4.** `SELECT MIN(Total), MAX(Total) FROM Invoice;` → **0.99** and
**25.86**.

**5.**

```sql
SELECT CustomerId,
       ROUND(SUM(Total), 2) AS total
FROM   Invoice
GROUP  BY CustomerId
ORDER  BY total DESC
LIMIT  3;
```

```
CustomerId  total
----------  ------
6           49.62
26          47.62
57          46.62
```

(Customers 6, 26, and 57 are the heaviest spenders — the same three whose
biggest invoices topped the HAVING list in Example 5.)
