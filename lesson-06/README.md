# Lesson 06: Joins II & Set Operations

**Prereq:** Lesson 05 (joins) — you'll reuse its `LEFT JOIN` and
unmatched-row recipe here.

**What you'll learn:** `CROSS JOIN` (the cartesian product — and the
accident it causes when you forget an `ON`), `FULL JOIN` (kept rows from
*both* sides; SQLite 3.31 can't spell it, so you'll build one from two
`LEFT JOIN`s + `UNION`), and the four set operators `UNION`, `UNION ALL`,
`INTERSECT`, `EXCEPT` — including using them as data-quality checks
(subset and equality tests) and the "same name ≠ same row" trap.

**No scratch copy needed.** This lesson only reads.

**Files:** [`lesson.md`](lesson.md) · [`answers.md`](answers.md)
