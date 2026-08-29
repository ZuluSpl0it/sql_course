# Course Baseline and Navigation Design

## Goal

Make the full course safely trackable in Git and improve navigation consistency
for students without changing lesson SQL or database contents.

## Scope

### Git baseline

Track the root course documentation, setup guide, answer keys, Lessons 4–9,
and the pristine `data/chinook.db` database. Do not add any scratch database.

Add these ignore rules:

```gitignore
# Scratch databases
data/chinook-scratch.db
data/northwind-scratch.db

# Generated local analysis and Python cache
graphify-out/
__pycache__/
*.py[cod]
```

Keep `tools/build_lesson09.py` untracked. It is unfinished source, not a
generated artifact; ignoring it would hide it from future review.

### Lessons 5–6 student-facing format

Adopt the detailed README labels used by Lessons 1–3 and 9:

- `Promise`
- `You need from before`
- `Keywords this lesson`
- `Files in this folder`

Retain a read-only note instead of a scratch-database setup section. Add a
short `## 7. Look ahead` section to each lesson, linking the current topic to
the next lesson’s core idea. Preserve all existing SQL, outputs, exercises,
and answer content.

### Root course map

Replace the unlinked lesson table with a linked map containing Lesson number,
title, prerequisite, scratch-database requirement, and key topics. Keep the
existing course overview and repo layout.

## Non-goals

- No migration to the current auditor format.
- No content rewrite or reordering.
- No change to `data/chinook.db`.
- No decision on whether to retain or delete `tools/build_lesson09.py`.

## Validation

1. Check the ignore rules cover scratch databases, Graphify output, and Python
   caches while leaving `tools/build_lesson09.py` visible as untracked.
2. Add regression tests for Lessons 5–6 README labels and all Lessons 1–6
   major-section headings.
3. Check every root course-map link resolves to an existing file or directory.
4. Run the legacy auditor for Lessons 5–6 and verify zero failures.
5. Verify `data/chinook.db` has MD5
   `99fe99c99d23033719bf9e277291e351` before and after the changes.
6. Make three commits: baseline, Lessons 5–6 format, and root course map.
