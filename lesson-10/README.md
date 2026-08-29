# Lesson 10: Performance & Integration

**Promise:** by the end of this lesson you can read a SQLite query plan as a
diagnostic, decide whether an index is likely to help, and combine the whole
course into clear, fan-out-safe reports.

**You need from before:** Lessons 01–09. In particular: joins and aggregates
(Lessons 04–06), CTEs (Lesson 07), expressions and `NULL` handling (Lesson
08), and `EXPLAIN QUERY PLAN` plus index basics (Lesson 09).

**Keywords this lesson:** `EXPLAIN QUERY PLAN`, `SCAN`, `SEARCH`, covering
index, `CREATE INDEX`, `DROP INDEX`, sargable predicate, CTE, fan-out,
`NOT EXISTS`

**Files in this folder:** [lesson.md](lesson.md) (read and do this),
[answers.md](answers.md) (quiz and capstone key — open only after attempting
the work).

**Before you start** — this lesson creates temporary indexes. Make a scratch
copy and work in it (from the repo root):

```bash
cp data/chinook.db data/chinook-scratch.db
litecli data/chinook-scratch.db
```

The lesson drops every index it creates. Still, never run its `CREATE INDEX`
commands against `data/chinook.db`.
