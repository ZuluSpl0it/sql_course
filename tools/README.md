# Course audit tools

This folder contains the repository's maintenance checks. Students do not need
to run them to complete the course.

## Audit the whole course

From the repository root, run:

```bash
python3 tools/audit_course.py
```

The audit uses temporary copies of `data/chinook.db` and `data/northwind.db`.
It checks Lessons 01–10, both lesson answer-key files, and the final-test answers and
guided solutions without changing either shipped database.

Normal SQL blocks must run successfully. The report separately counts lesson
templates and examples that intentionally demonstrate a SQLite error.

To also execute normal SQL blocks through the student-facing LiteCLI client:

```bash
python3 tools/audit_course.py --litecli
```

That mode requires a working `litecli` command on your `PATH`.

## Run the auditor's tests

```bash
python3 -m unittest tools.test_audit_course -v
```

The tests cover the document manifest, SQL-fence parsing, expected-error
handling, final-test structure, LiteCLI availability, and Markdown layout
checks such as accidental Setext headings.
