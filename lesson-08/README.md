# Lesson 08: Expressions & functions

**Prereq:** Lesson 07 (subqueries & CTEs) — the values you shape here are the
same values those queries moved around. You should be comfortable with
`SELECT` lists, `WHERE` clauses, and `NULL`.

**What you'll learn:** how to *transform* values instead of just moving rows.
`CASE` (a value-level if/elif/else), string functions (`LENGTH`, `UPPER`,
`SUBSTR`, `REPLACE`, `TRIM`), the date functions on Chinook's text-stored
dates (`DATE`, `STRFTIME`, `JULIANDAY`, date modifiers like `'+1 year'`),
numeric behavior (`ROUND`, `ABS`, integer division), and the two `NULL`
tools: `COALESCE` and `NULLIF`. Plus what SQLite will and won't check for
you when it parses a date string.

**No reset needed.** This lesson only reads.

**Files:** [`lesson.md`](lesson.md) · [`answers_practical.md`](answers_practical.md)
· [`answers_quiz.md`](answers_quiz.md)
