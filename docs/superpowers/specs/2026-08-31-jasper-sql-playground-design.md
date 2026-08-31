# Jasper SQL Playground Student Workflow

## Goal

Make Jasper SQL Playground the sole student-facing database tool for the
course, with no LiteCLI installation or configuration required.

## Design

Student documentation will direct learners to open Jasper SQL Playground and
drag `chinook.db` or `northwind.db` into it. Jasper's schema panel replaces
LiteCLI dot commands. Lessons retain their SQLite SQL, expected results, quiz
structure, and answer keys.

Write lessons will explain that Jasper edits an in-memory browser copy. The
shipped database remains unchanged, and students should reload the original
file when a lesson needs a clean starting state. Scratch-copy shell commands
will be removed from student instructions.

LiteCLI-specific concepts—installation, autocomplete, multiline configuration,
terminal prompts, and dot commands—will be removed or rewritten. SQLite
behavior that is independent of LiteCLI, including transactions and
connection-scoped pragmas, will remain and be described in browser-session
terms where necessary.

The maintainer audit will continue using Python's built-in `sqlite3` module for
deterministic SQL validation. Its optional LiteCLI execution path is outside
the student workflow and will remain unchanged in this pass.

## Files in scope

- Root, setup, data, lesson, answer-key, and final-test Markdown files with
  student-facing LiteCLI instructions.
- No SQL answer content or database files.
- No changes to `tools/audit_course.py` or its tests.

## Verification

- Search student-facing Markdown for LiteCLI, `.tables`, `.schema`, and
  LiteCLI-only setup terms.
- Run `python3 tools/audit_course.py`.
- Run `python3 -m unittest tools.test_audit_course -v`.
