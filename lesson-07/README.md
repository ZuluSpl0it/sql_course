# Lesson 07: Subqueries & CTEs

**Prereq:** Lesson 06 (set operators) — you'll reuse its "a query is a set of
rows" idea, and its rule that `ORDER BY`/`LIMIT` bind to the *whole* compound
query becomes the reason for the derived-table pattern here. Lesson 05's
fan-out-safe per-artist revenue reappears, now written as a `WITH`.

**What you'll learn:** how to put a query *inside* another query — a
**scalar subquery** in the `SELECT` list, `IN` and `EXISTS` in the `WHERE`
clause, and a **derived table** (a query in the `FROM` clause) as the
portable workaround for a per-branch `LIMIT`. Then **`WITH`** (a *common
table expression* — a named subquery you can reference by name, even more
than once) and **`WITH RECURSIVE** (a CTE that reads itself, used here to walk
the `Employee.ReportsTo` org chart to *any* depth). And the failures that
*look* like they should error but don't: a multi-row "scalar" that silently
returns one row, and a non-correlated subquery that quietly prints a constant.

**No scratch copy needed.** This lesson only reads.

**Files:** [`lesson.md`](lesson.md) · [`answers.md`](answers.md)
