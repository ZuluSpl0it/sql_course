# Lesson 06 — Quiz Answer Key

Attempt the Quiz in `lesson.md` before opening this file. This lesson only
reads, so run everything against `data/chinook.db`.

---

## Your turn

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

## Quiz

### 1 — 8 × 25

**200 rows.** Not useful as a *report* — it's every employee paired with
every genre, a cartesian product with no matching condition. (It *is* a
legitimate scaffold if you then `WHERE` down to a meaningful slice, e.g.
"one row per employee per genre they manage" — but that requires extra
tables in Chinook, which is why the pattern is rare.)

### 2 — RIGHT JOIN, and the SQLite substitute

`RIGHT JOIN` is not supported on SQLite 3.31 (the same error). To keep all
rows from the right table, **swap the tables and use `LEFT JOIN`**:

```sql
SELECT …
FROM   R          -- the table you want to keep fully
LEFT   JOIN  L    ON  L.key = R.key
```

A full outer join in SQLite is the two-branch pattern from Example 2:
`LEFT JOIN` in one direction, `UNION`, then the *same relationship viewed
from the other side* with `WHERE <left>.key IS NULL` to keep only the
second side's unmatched rows. (On SQLite ≥ 3.39 and on PostgreSQL you can
write `FULL [OUTER] JOIN` directly.)

### 3 — 30 ∪ 10 with 4 in common

- `UNION` → 30 + 10 − 4 = **36**
- `UNION ALL` → 30 + 10 = **40**

### 4 — what gets compared

**Positions, by value.** Column 1 of the left query is compared with
column 1 of the right, and so on. The column *names* are irrelevant (the
result just adopts the left side's names), and the *tables the rows came
from* are invisible — two rows with identical values are the same row,
no matter where they were read from.

### 5 — `A EXCEPT B` = 0; then `B EXCEPT A` = 0

First, `A − B = 0` means **A ⊆ B** (every row of A is already in B). Add
`B − A = 0` and you also have **B ⊆ A**, so **A = B** — the two result
sets are identical.

### 6 — stretch: NULLs in the org chart

Blank **manager**: 1 row — the CEO (Andrew), produced by the second
branch as `(NULL, NULL, 1, Andrew)`. Blank **report**: 5 rows — Jane,
Margaret, Steve, Robert, Laura, the five employees nobody reports to.

Can a single row be blank on **both** sides? **No.** A `FULL JOIN` row
is always exactly one of three kinds: a *matched* pair (both sides
filled), a *left-side orphan* (right side NULL), or a *right-side
orphan* (left side NULL). For a row to be NULL on both sides, one
physical row would have to be unmatched in **both** directions at once,
which a single join condition can't do — a row either matches on the
condition or it doesn't. (The emulation respects the same property:
branch 1 can't output `(NULL, NULL)` because its left side is always a
real employee row, and branch 2's one row has a real report.) In this
data: 7 matched + 1 left orphan + 5 right orphans = 13, and every row
has at least one real employee.

---

## Answers to the worked examples (for checking yourself)

| example | the number to check |
|---|---|
| 1 — cross join on purpose | 8 × 25 = **200** rows total |
| 1 — accidental comma join | 3503 × 347 = **1,215,541** rows |
| 2 — FULL JOIN emulation | **13** rows (1 blank manager, 5 blank report) |
| 3 — two "Music" playlists | 6580 (`UNION ALL`) vs **3290** (`UNION`) |
| 3 — The Trooper | 1 row (`UNION`) vs **2** rows (`UNION ALL`) |
| 4 — 90's ∩ Classical | **41** tracks |
| 4 — 95 ∩ 102 by name vs by id | **6** vs **0** |
| 5 — 90's − Classical | **1436** tracks |
| 5 — Basics − Classical | **0** (subset) |
| 5 — Music(1)−Music(8) + Music(8)−Music(1) | **0** (equal sets) |
