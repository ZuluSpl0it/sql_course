# Final Test: Northwind Transfer Assessment

This is a self-graded cumulative assessment. It uses **Northwind**, not
Chinook, so you must inspect an unfamiliar schema and apply the ideas from the
course rather than copying a remembered query.

## What you need

- Complete Lessons 01–10.
- Open [Jasper SQL Playground](https://jasperbernaers.com/sql-playground/) and
  drag in the assessment database:

`data/northwind.db`

- Use Jasper's schema panel, `PRAGMA table_info(...)`, and
  `PRAGMA foreign_key_list(...)` to discover the schema. The exam deliberately
  does not provide a relationship diagram.

## Rules

- Attempt [exam.md](exam.md) before opening any other file here.
- The core exam is read-only. Do not modify `data/northwind.db`.
- Questions 43–46 may create an index in the in-memory database:

Reload `data/northwind.db` in Jasper before attempting those questions so the
database starts clean.

- After self-grading with [answers.md](answers.md), use
  [guided-solutions.md](guided-solutions.md) for the hardest problems. It is a
  teaching guide, not a second attempt at the exam.

## Scoring guide

There are 50 questions. Use the answer key's credit conditions rather than
matching query text exactly. A different query earns full credit when it
returns the required result, has the required row grain, handles `NULL` and
join cardinality correctly, and follows any stated safety condition.

Questions 47–50 are integrated case studies. Give them double weight if you
want a 54-point score; otherwise score all questions equally.

## Database pin

This assessment was written for `data/northwind.db` with SHA-256:

```text
2f4f5c68dfcd33ba27373eae48c7a4869800c68095ee0f9f0da494f83382a877
```
