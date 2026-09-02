# SQL Course — Beginner to Intermediate

A hands-on SQL course built around **SQLite** and the **Chinook** sample database
(a digital music store: 11 tables, ~7,000 rows). You learn by running real
queries against real data.

## What you'll be able to do

After the course you will be able to write SQL from scratch: select, filter,
join, aggregate, use subqueries and CTEs, handle nulls and three-valued logic,
write and modify data with transactions, design schemas, and read `EXPLAIN`
output for basic performance intuition.

## How the course works

- **One tool:** [SQL Explorer](https://sql-explorer.netlify.app/),
  a browser-based SQLite workspace. Setup is in [00-getting-started/](00-getting-started/).
- **One database:** `12-data/chinook.db`, shared by Lessons 01–10. Each lesson's
  queries run against it.
- **Every lesson** follows the same seven-block structure:
  1. **Concept** — the idea, the syntax, the keywords of the lesson
  2. **Worked examples** — real queries with real output
  3. **Practical exercises** — prompts for you to solve (no answers shown)
  4. **Quiz** — self-graded; the answer key is in a separate file so you
     attempt it first
  5. **Pitfalls** — common mistakes and their fixes
  6. **Recap** — what to remember
  7. **Look ahead** — what the next lesson adds

## Lessons

| # | Lesson | You need first | Scratch DB? | Key topics |
|---|--------|----------------|-------------|------------|
| 01 | [Your first query](01-lesson-01/README.md) | [Setup](00-getting-started/README.md) | No | `SELECT`, `FROM`, `AS`, `DISTINCT`, `ORDER BY`, `LIMIT`, `OFFSET` |
| 02 | [Filtering rows](02-lesson-02/README.md) | Lesson 01 | No | `WHERE`, `AND`/`OR`/`NOT`, `IN`, `BETWEEN`, `LIKE`, `IS NULL` |
| 03 | [Writing data](03-lesson-03/README.md) | Lessons 01–02 | Yes | `INSERT`, `UPDATE`, `DELETE`, transactions, `CREATE TABLE` |
| 04 | [Aggregation & groups](04-lesson-04/README.md) | Lessons 01–02 | No | `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`, `GROUP BY`, `HAVING` |
| 05 | [Joins, Part I](05-lesson-05/README.md) | Lesson 04 | No | keys, `INNER JOIN`, `LEFT JOIN`, self joins |
| 06 | [Joins II & set operations](06-lesson-06/README.md) | Lesson 05 | No | `CROSS JOIN`, emulated `FULL JOIN`, `UNION`, `INTERSECT`, `EXCEPT` |
| 07 | [Subqueries & CTEs](07-lesson-07/README.md) | Lesson 06 | No | subqueries, `EXISTS`, `WITH`, `WITH RECURSIVE` |
| 08 | [Expressions & functions](08-lesson-08/README.md) | Lesson 07 | No | `CASE`, string/date/numeric functions, `COALESCE`, `NULLIF` |
| 09 | [Schema & constraints](09-lesson-09/README.md) | Lessons 01–03, 08 | Yes | types, constraints, `ALTER TABLE`, views, indexes |
| 10 | [Performance & integration](10-lesson-10/README.md) | Lessons 01–09 | Yes | query plans, index judgment, fan-out-safe reports, CTEs |

## Final test

After Lesson 10, take the [Northwind final test](11-final-test/README.md). It
uses the unfamiliar `12-data/northwind.db` dataset to assess transfer across the
whole course; its self-grading key and guided solutions are separate from the
exam questions.

## Repo layout

```
README.md                <- this file
00-getting-started/         <- install & first connection
12-data/
  README.md               <- database and reset guidance
  chinook.db             <- the course database (used by Lessons 01-10)
  northwind.db           <- unfamiliar database for the final test
01-lesson-01/
  README.md              <- short overview of the lesson
  lesson.md              <- the lesson itself (7 blocks)
  answers_practical.md   <- practical-exercise answer key
  answers_quiz.md        <- quiz answer key
...
11-final-test/
  README.md              <- rules and self-grading guidance
  exam.md                <- 50-question assessment
  answers.md              <- final-test answer key and review references
  guided-solutions.md    <- step-by-step help for the hardest problems
13-tools/
  README.md              <- maintainers' course-audit instructions
  audit_course.py        <- whole-course SQL and Markdown audit
  test_audit_course.py   <- auditor regression tests
```

## Pinned versions

- **SQLite** ≥ 3.31 (any modern system version is fine; `chinook.db` is a
  standard SQLite file and works across all current versions)

Keep the tool versions and the `.db` file as shipped — the expected outputs in
the answer keys were generated against them.
