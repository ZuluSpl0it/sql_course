# Course Baseline and Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Track the course baseline safely, standardize Lessons 5–6 student navigation, and add a linked root course map.

**Architecture:** Git-ignore rules distinguish reproducible course assets from local generated state. Lesson-level changes are Markdown-only and tested with the legacy test suite. The root README remains the single navigation entry point.

**Tech Stack:** Git, Markdown, Python `unittest`, SQLite compatibility auditor.

---

## File map

- Modify: `.gitignore` — generated/local files only.
- Track: `README.md`, `getting-started/`, `data/chinook.db`, course answers, and Lessons 4–9.
- Modify: `lesson-04/lesson.md`, `lesson-05/README.md`, `lesson-05/lesson.md`, `lesson-06/README.md`, `lesson-06/lesson.md`.
- Modify: `tools/test_audit_legacy_lessons.py` — navigation regression checks.
- Modify: `README.md` — linked course map.

### Task 1: Commit a safe course baseline

**Files:**

- Modify: `.gitignore`
- Track: `README.md`, `getting-started/README.md`, `data/chinook.db`, all answer keys, Lessons 4–9 except ignored scratch/generated artifacts.

- [ ] **Step 1: Add ignore rules**

Add `graphify-out/`, `__pycache__/`, and `*.py[cod]` after the existing scratch-database rules. Do not add `tools/build_lesson09.py`.

- [ ] **Step 2: Verify the ignore boundary**

Run `git check-ignore -v data/chinook-scratch.db graphify-out/cache/stat-index.json tools/__pycache__/audit_legacy_lessons.cpython-38.pyc`.

Expected: each generated/local path is ignored. Run `git status --short tools/build_lesson09.py`; expected: still untracked.

- [ ] **Step 3: Stage only baseline assets**

Stage `.gitignore`, `README.md`, `getting-started/`, `data/chinook.db`, all `answers.md` files, and Lessons 4–9. Exclude `data/chinook-scratch.db`, `graphify-out/`, caches, and `tools/build_lesson09.py`.

- [ ] **Step 4: Commit baseline**

Commit with message `chore: track course baseline`.

### Task 2: Add regression checks for visible consistency

**Files:**

- Modify: `tools/test_audit_legacy_lessons.py`

- [ ] **Step 1: Write failing tests**

Add assertions that Lessons 5–6 READMEs include the four detailed labels and
that Lessons 1–6 each include the seven title-case major headings, including
`## 7. Look ahead`.

- [ ] **Step 2: Verify RED**

Run `python3 -m unittest tools/test_audit_legacy_lessons.py -v`.

Expected: test failure because Lessons 5–6 do not yet use all detailed labels
or include `Look ahead`.

### Task 3: Standardize Lessons 5–6

**Files:**

- Modify: `lesson-04/lesson.md`, `lesson-05/README.md`, `lesson-05/lesson.md`
- Modify: `lesson-06/README.md`, `lesson-06/lesson.md`

- [ ] **Step 1: Rewrite README wrappers**

Use the detailed labels `Promise`, `You need from before`, `Keywords this
lesson`, and `Files in this folder`. Link `lesson.md` and `answers.md`. State
that each lesson reads only and needs no scratch copy.

- [ ] **Step 2: Add short Look ahead sections**

Add Lesson 04’s bridge to joins in Lesson 05, Lesson 05’s bridge to set
operations in Lesson 06, and Lesson 06’s bridge to subqueries and CTEs in
Lesson 07. Do not change existing lesson content.

- [ ] **Step 3: Verify GREEN**

Run `python3 -m unittest tools/test_audit_legacy_lessons.py -v`.

Expected: all tests pass.

- [ ] **Step 4: Audit Lessons 5–6**

Run `python3 tools/audit_legacy_lessons.py lesson-05/lesson.md data/chinook.db` and the equivalent Lesson 06 command.

Expected: both report `0 FAIL`.

- [ ] **Step 5: Commit lesson format work**

Commit `lesson-05`, `lesson-06`, and `tools/test_audit_legacy_lessons.py` with message `docs: standardize lessons 5-6 format`.

### Task 4: Create a linked course map

**Files:**

- Modify: `README.md`

- [ ] **Step 1: Update the course-map table**

Make each Lesson 01–09 title link to its lesson README. Include columns for
prerequisite, scratch-database requirement, and topics. Link the setup guide.

- [ ] **Step 2: Check links and database integrity**

Use a Python standard-library script or `rg --files` to confirm every local
Markdown target exists. Run `md5sum data/chinook.db`; expected:
`99fe99c99d23033719bf9e277291e351`.

- [ ] **Step 3: Commit course map**

Commit `README.md` with message `docs: add linked course map`.
