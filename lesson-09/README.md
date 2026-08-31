# Lesson 09: Schema & Constraints

**Promise:** you can read a database's own schema — `sqlite_master`, `PRAGMA table_info`, `PRAGMA foreign_key_list` — and you'll know exactly which of the five constraint words SQLite enforces *always* and which only when you switch a pragma on, plus the precise limits of `ALTER TABLE` in 3.31 and what `EXPLAIN QUERY PLAN` shows before and after you add an index.

**You need from before:** Lessons 01–02 (reading), Lesson 03 (transactions),
and Jasper SQL Playground. Lesson 08's date-as-text story pays off here,
because `DATETIME` is just `TEXT`.

**Keywords this lesson:** storage class, type affinity, `typeof()`, `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`, `PRAGMA foreign_keys`, `rowid`, `ALTER TABLE`, `RENAME COLUMN` / `RENAME TABLE`, `sqlite_master`, `PRAGMA table_info`, `PRAGMA foreign_key_list`, `CREATE VIEW`, `EXPLAIN QUERY PLAN`, autoindex

**Files in this folder:** `lesson.md`, `answers.md` (quiz + your-turn key), `manual-verify.json`, and `expect-errors.json`.

**Before you start** — this lesson *writes*. Open Jasper SQL Playground and
load `data/chinook.db`. Work in its in-memory copy; reload the original file
when you need a clean session. The real database stays untouched.
