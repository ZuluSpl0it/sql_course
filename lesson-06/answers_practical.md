# Lesson 06 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

### 1 — `SELECT * FROM MediaType, Genre`

**125 rows** (5 media types × 25 genres). Every pairing of a format with a
genre — most of them meaningless, which is exactly what a cross join is.

### 2 — TV Shows: `UNION` vs `UNION ALL`

- `UNION` → **213 rows**
- `UNION ALL` → **426 rows**

Exactly double — so the two "TV Shows" playlists (3 and 10) contain the
*same* 213 tracks. (If they had partially overlapped, `UNION ALL` would
have been more than the `UNION` count but less than twice it.)

### 3 — Classical ∩ Classical 101 – The Basics

**25 tracks.** The Basics playlist (15) is 25 tracks, and all 25 of them
are on the big Classical playlist (12). Check the subset relation in the
other direction: `12 EXCEPT 15` → **50** (Classical has 75 tracks, 25 of
which Basics also has — so the 25 really is a subset, and Classical has
50 more tracks of its own).

### 4 — Heavy Metal Classic − Classical

**26 tracks.** Heavy Metal Classic (17) has 26 tracks, and *none* of them
are on the Classical playlist (12) — so the `EXCEPT` returns the whole
playlist. (Try it in the other direction, `12 EXCEPT 17`: you get 75, the
entire Classical playlist.)

### 5 — full outer join, by hand

The Example 2 query is exactly this:

```sql
SELECT e.EmployeeId AS manager_id, e.FirstName AS manager,
       r.EmployeeId AS report_id,   r.FirstName AS report
FROM   Employee e
LEFT   JOIN  Employee r ON r.ReportsTo = e.EmployeeId
UNION
SELECT e.EmployeeId, e.FirstName, r.EmployeeId, r.FirstName
FROM   Employee r
LEFT   JOIN  Employee e ON e.EmployeeId = r.ReportsTo
WHERE  e.EmployeeId IS NULL
ORDER  BY manager_id, report_id;
```

13 rows:

```
manager_id  manager  report_id  report
----------  -------  ---------  -------
                        1       Andrew
1           Andrew 2          Nancy
1           Andrew 6          Michael
2           Nancy  3          Jane
2           Nancy  4          Margaret
2           Nancy  5          Steve
3           Jane
4           Margaret
5           Steve
6           Michael 7          Robert
6           Michael 8          Laura
7           Robert
8           Laura
```

Check the two "sides": the row with blank *manager* columns (`(NULL, NULL,
1, Andrew)` — the only employee with `ReportsTo` NULL) and the five rows
with blank *report* columns (Jane, Margaret, Steve, Robert, Laura — the
only employees nobody reports to).

---
