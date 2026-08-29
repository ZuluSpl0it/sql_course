# Course-wide auditor design

## Goal

Provide one command that verifies all ten lessons and the final assessment
without modifying either shipped database.

## Command

`python3 tools/audit_course.py` runs the SQLite audit. Passing `--litecli`
also executes the same runnable SQL through the LiteCLI client.

## Scope

- Lessons 01–10 use `data/chinook.db`.
- Lesson and answer-key fences are checked in document order on a fresh
  temporary copy for each document.
- Final-test answer and guided-solution fences use `data/northwind.db`.
- Template fragments and examples explicitly displaying an error are reported
  as skips or expected errors, not failures.
- The final-test question sheet is structure-checked; it intentionally has no
  answer SQL to execute.

## Result policy

SQLite execution errors in a runnable, non-expected-error fence fail the
audit. Output table formatting is informational only because SQLite CLI and
LiteCLI legitimately render floats and query plans differently.

The program prints a per-document summary and one course total, returning
zero only when every required check passes. LiteCLI is optional; when
`--litecli` is requested but unavailable, the program reports a clear failure.

## Tests

Unit tests cover the document manifest, template/expected-error classification,
final-test selection, total aggregation, and the missing-LiteCLI failure path.
An integration run verifies the real course against temporary copies of the
two databases.
