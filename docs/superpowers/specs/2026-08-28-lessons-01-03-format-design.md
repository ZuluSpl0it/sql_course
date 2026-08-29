# Lessons 01–03 Student-Facing Format Migration

## Goal

Make the first three lessons feel consistent with the later course without
changing their SQL, examples, exercises, answer keys, or legacy audit format.

## Scope

- Standardize each lesson README on the detailed Lesson 09 pattern:
  `Promise`, `You need from before`, `Keywords this lesson`, and `Files in
  this folder`.
- Retain/add a `Before you start` scratch-database section for Lesson 03,
  because it writes data.
- Normalize `lesson.md` major section labels to title case: `The concept`,
  `Worked examples`, `Your turn`, `Quiz`, `Pitfalls`, `Recap`, and `Look
  ahead` where present.
- Preserve all SQL blocks, prose meaning, expected outputs, exercises, file
  names, and answer-key links.

## Non-goals

- No conversion to the newer auditor format.
- No SQL-query rewrite, database change, or pedagogical reordering.
- No changes to Lessons 4–9 in this pass.

## Validation

1. Check Markdown links and required README sections for Lessons 1–3.
2. Run `python3 -m unittest tools/test_audit_legacy_lessons.py -v`.
3. Run the legacy auditor against Lessons 1–3 with `data/chinook.db`.
4. Confirm both course database files still have the pristine matching hash.
