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

- **One tool:** [litecli](https://github.com/dbcli/litecli) (a SQLite command-line
  client with autocomplete). Setup is in [getting-started/](getting-started/).
- **One database:** `data/chinook.db`, shared by Lessons 01–09. Each lesson's
  queries run against it.
- **Every lesson** follows the same seven-block structure:
  1. **Concept** — the idea, the syntax, the keywords of the lesson
  2. **Worked examples** — real queries with real output
  3. **Your turn** — prompts for you to solve (no answers shown)
  4. **Quiz** — self-graded; the answer key is in a separate file so you
     attempt it first
  5. **Pitfalls** — common mistakes and their fixes
  6. **Recap** — what to remember
  7. **Look ahead** — what the next lesson adds

## Lessons

| # | Lesson | You need first | Scratch DB? | Key topics |
|---|--------|----------------|-------------|------------|
| 01 | [Your first query](lesson-01/README.md) | [Setup](getting-started/README.md) | No | `SELECT`, `FROM`, `AS`, `DISTINCT`, `ORDER BY`, `LIMIT`, `OFFSET` |
| 02 | [Filtering rows](lesson-02/README.md) | Lesson 01 | No | `WHERE`, `AND`/`OR`/`NOT`, `IN`, `BETWEEN`, `LIKE`, `IS NULL` |
| 03 | [Writing data](lesson-03/README.md) | Lessons 01–02 | Yes | `INSERT`, `UPDATE`, `DELETE`, transactions, `CREATE TABLE` |
| 04 | [Aggregation & groups](lesson-04/README.md) | Lessons 01–02 | No | `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`, `GROUP BY`, `HAVING` |
| 05 | [Joins, Part I](lesson-05/README.md) | Lesson 04 | No | keys, `INNER JOIN`, `LEFT JOIN`, self joins |
| 06 | [Joins II & set operations](lesson-06/README.md) | Lesson 05 | No | `CROSS JOIN`, emulated `FULL JOIN`, `UNION`, `INTERSECT`, `EXCEPT` |
| 07 | [Subqueries & CTEs](lesson-07/README.md) | Lesson 06 | No | subqueries, `EXISTS`, `WITH`, `WITH RECURSIVE` |
| 08 | [Expressions & functions](lesson-08/README.md) | Lesson 07 | No | `CASE`, string/date/numeric functions, `COALESCE`, `NULLIF` |
| 09 | [Schema & constraints](lesson-09/README.md) | Lessons 01–03, 08 | Yes | types, constraints, `ALTER TABLE`, views, indexes |
| 10 | [Performance & capstone](lesson-10/README.md) | Lessons 01–09 | Yes | query plans, index judgment, fan-out-safe reports, CTEs |

Lessons 01–10 are included in this repository. A separate final test is not
included yet.

## Repo layout

```
README.md                <- this file
getting-started/         <- install & first connection
data/
  chinook.db             <- the course database (used by Lessons 01-09)
lesson-01/
  README.md              <- short overview of the lesson
  lesson.md              <- the lesson itself (7 blocks)
  answers.md             <- quiz answer key
...
```

## Pinned versions

- **litecli** ≥ 1.17 (current as of this course)
- **SQLite** ≥ 3.31 (any modern system version is fine; `chinook.db` is a
  standard SQLite file and works across all current versions)

Keep the tool versions and the `.db` file as shipped — the expected outputs in
the answer keys were generated against them.
