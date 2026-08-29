# Lesson 10 Performance and Capstone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe, verified performance-and-capstone Lesson 10.

**Architecture:** Markdown lesson files hold the teaching content and answer
key. Temporary indexes are named `idx_l10_...`, created only on a scratch
copy, and dropped before the final verification query.

**Tech Stack:** Markdown, SQLite, Python `unittest`, legacy lesson auditor.

---

### Task 1: Add a failing Lesson 10 structure test

- [ ] Add tests in `tools/test_audit_legacy_lessons.py` that require the
  detailed README labels and seven major section headings in Lesson 10.
- [ ] Run `python3 -m unittest tools/test_audit_legacy_lessons.py -v` and
  confirm the new test fails because Lesson 10 does not exist.

### Task 2: Create Lesson 10 content

- [ ] Create `lesson-10/README.md`, `lesson-10/lesson.md`, and
  `lesson-10/answers.md` using verified Chinook results.
- [ ] Use only temporary `idx_l10_invoice_date` and `idx_l10_track_name`
  indexes; drop both in the lesson teardown.
- [ ] Add the linked Lesson 10 row and included-lessons statement to root
  `README.md`.

### Task 3: Verify the lesson

- [ ] Run the unit tests and legacy auditor.
- [ ] Execute the temporary-index SQL on a `/tmp` database copy and verify no
  `idx_l10_%` objects remain.
- [ ] Verify the pristine database MD5.
