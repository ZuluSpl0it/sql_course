# Lesson 07 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file.

## Quiz

### 1 — what a scalar subquery must return
**Exactly one row with exactly one column.** In SQLite 3.31, if it returns
more than one row it does *not* error — it silently uses the *first* row
(Pitfall 1). If it returns more than one *column*, that is a hard error
(`more than one column returned by a subquery`).
### 2 — `IN` vs `=` with a two-row subquery
The subquery `SELECT EmployeeId FROM Employee ORDER BY EmployeeId LIMIT 2`
returns the set {1, 2}.
- `WHERE EmployeeId IN (…)`: membership in a **set** → matches both 1 and 2 →
  **2 rows**.
- `WHERE EmployeeId = (…)`: `=` expects a **scalar** (one value). SQLite 3.31
  silently uses the *first* row (id 1) → matches only 1 → **1 row**.
So `IN` is set membership (many matches), `=` is a scalar comparison (one
value, and in SQLite the first of a multi-row subquery).
### 3 — `WHERE x = (multi-row subquery)` in SQLite 3.31
It does **not** error. SQLite 3.31 returns the *first* row of the subquery's
result and compares `x` against that — so the test is only against row 1, and
the other rows are silently ignored. MySQL and PostgreSQL, by contrast, stop
with a *"subquery returns more than one row"* error. Because SQLite is silent,
this is a real correctness trap: put an explicit `LIMIT 1` in the subquery if
you truly want "the first one", or use `IN`/`EXISTS` if you want a set test.
### 4 — `NOT IN` vs `NOT EXISTS` with a `NULL`
`ReportsTo` is `NULL` for the CEO, so `(SELECT ReportsTo FROM Employee)`
contains a `NULL`.
- `e.EmployeeId NOT IN (…that set containing a NULL)`: `NULL` makes the
  `IN` test `UNKNOWN` for every row, so **0 rows**.
- `NOT EXISTS (SELECT 1 FROM Employee r WHERE r.ReportsTo = e.EmployeeId)`: no
  `NULL` in the logic — it just asks "does anyone report to this employee?"
  → the 5 employees with no reports (ids 3, 4, 5, 7, 8) → **5 rows**.
`NOT EXISTS` is the correct "nobody reports to this" test; `NOT IN` is the
NULL-trap.
### 5 — when to use a `WITH`
Use a `WITH` when you need the **same subquery more than once** in a query
(you reference it by name instead of repeating it), or when a long
derived-table expression would obscure the main `SELECT` and a name makes it
readable. A CTE is otherwise just a derived table with a name — it can also be
referenced multiple times, which a plain inline `(SELECT …)` in one `FROM`
position cannot.
### 6 — stretch: 0-row anchor, and cycles
If the anchor matches **zero** employees (`WHERE EmployeeId = 999`), the walk
has no seed, so the result is **0 rows** — no error. If the data had a
**cycle**, there would be no "last" row: every pass would keep re-adding
already-seen employees, so the recursion **never terminates** and the query
runs until you stop it. Keep it safe two ways: (a) keep a restrictive anchor
filter, and (b) add a **depth cap** in the recursive part, e.g.
`WHERE org.depth < 10` (or track seen ids with a `SEEN` set) so a cyclic or
pathological graph stops after a bounded number of levels instead of
spinning forever.

---
## Worked example checks (for checking yourself)
| example | the number to check |
|---|---|
| 1 — non-correlated vs correlated | constant **$2,328.60** on every row → varies per customer |
| 2 — `IN` vs `EXISTS` (Rock artists) | both **51** (first 5 shown) |
| 3 — derived table, top-3 + bottom-3 | **6** rows (3 top + 3 bottom) |
| 4 — `WITH` per-artist revenue, top 5 | Iron Maiden **$138.60**, U2 $105.93, Metallica $90.09, Led Zeppelin $86.13, Lost $81.59 |
| 5 — `WITH RECURSIVE` org chart | **8** rows, max depth **2** (1 / 2 / 5 per level) |
| 5 — missing anchor filter | **20** rows (not 8) |
| 5 — hard-coded two-level join | **8** rows (stops at depth 2 by construction) |
