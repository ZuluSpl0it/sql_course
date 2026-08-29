# Lesson 03: Writing Data

**Promise:** by the end of this lesson you can add, change, and remove rows —
and, more importantly, wrap those writes in a transaction so that when you
make a mistake (you will), the database reverts it instead of keeping it.

**You need from before:** Lessons 01–02 (`SELECT`, `WHERE`, and the
scratch-copy habit).

**Keywords this lesson:** `INSERT`, `VALUES`, `UPDATE`, `SET`, `DELETE`,
`BEGIN`, `COMMIT`, `ROLLBACK`, `CREATE TABLE`, `changes()`

**Files in this folder:** [lesson.md](lesson.md), [answers.md](answers.md)
(quiz key — open only after you've attempted the quiz).

**Before you start** — this is the first lesson that *writes*. Make a
scratch copy and work in it (from the repo root):

```bash
cp data/chinook.db data/chinook-scratch.db
litecli data/chinook-scratch.db
```

If you're on Windows: `copy data\chinook.db data\chinook-scratch.db`.
The real `data/chinook.db` stays untouched for the rest of the course.
