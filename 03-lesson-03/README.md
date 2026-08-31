# Lesson 03: Writing Data

**Promise:** by the end of this lesson you can add, change, and remove rows —
and, more importantly, wrap those writes in a transaction so that when you
make a mistake (you will), the database reverts it instead of keeping it.

**You need from before:** Lessons 01–02 (`SELECT`, `WHERE`, and loading the
database in Jasper SQL Playground).

**Keywords this lesson:** `INSERT`, `VALUES`, `UPDATE`, `SET`, `DELETE`,
`BEGIN`, `COMMIT`, `ROLLBACK`, `CREATE TABLE`, `changes()`

**Files in this folder:** [lesson.md](lesson.md),
[answers_practical.md](answers_practical.md), and
[answers_quiz.md](answers_quiz.md) (open only after attempting the work).

**Before you start** — this is the first lesson that *writes*. Open Jasper SQL
Playground and load `12-data/chinook.db`:

Jasper works on an in-memory copy. Reload `12-data/chinook.db` whenever you need
to reset the lesson; the real file stays untouched.
