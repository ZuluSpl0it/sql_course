# Lesson 01 ordering example repair

## Goal

Make the introductory `ORDER BY` example runnable in LiteCLI while retaining
both ascending and descending ordering demonstrations.

## Change

Replace the single invalid fenced SQL block containing two `ORDER BY` clauses
with two independent fenced SQL blocks:

1. An ascending query: `SELECT Name FROM Artist ORDER BY Name;`.
2. A descending query: `SELECT Name FROM Artist ORDER BY Name DESC;`.

Each block is a complete, directly runnable statement. The surrounding prose
will identify ascending as the default and descending as the alternative.

## Validation

Run every SQL fence in `lesson-01/lesson.md` that is intended to execute
against a temporary copy of `data/chinook.db`, through both `sqlite3` and
LiteCLI. The opening grammar skeleton and the documented `OFFSET` error remain
non-executable teaching examples.
