# Lessons 01–03 Format Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Lessons 1–3 the same detailed, student-facing navigation and section style used by the later course lessons.

**Architecture:** Markdown-only migration. README files use the detailed course template. Major lesson section labels move to title case. SQL, output fences, exercises, file names, and audit behavior stay unchanged.

**Tech Stack:** Markdown, Python `unittest`, SQLite compatibility auditor.

---

## File map

- Modify: `lesson-01/README.md`, `lesson-02/README.md`, `lesson-03/README.md` — detailed README labels and links.
- Modify: `lesson-01/lesson.md`, `lesson-02/lesson.md`, `lesson-03/lesson.md` — title-case major headings only.
- Modify: `tools/test_audit_legacy_lessons.py` — regression checks for visible format.

### Task 1: Add format regression checks

**Files:**

- Modify: `tools/test_audit_legacy_lessons.py`

- [ ] **Step 1: Write failing tests for README labels and lesson headings**

Assert each README contains `**Promise:**`, `**You need from before:**`, `**Keywords this lesson:**`, and `**Files in this folder:**`. Assert each lesson contains `## 1. The concept`, `## 2. Worked examples`, `## 3. Your turn`, `## 4. Quiz`, `## 5. Pitfalls`, and `## 6. Recap`.

- [ ] **Step 2: Verify RED**

Run `python3 -m unittest tools/test_audit_legacy_lessons.py -v`.

Expected: heading assertions fail because the old labels are uppercase.

### Task 2: Standardize student-facing Markdown

**Files:**

- Modify: `lesson-01/README.md`, `lesson-02/README.md`, `lesson-03/README.md`
- Modify: `lesson-01/lesson.md`, `lesson-02/lesson.md`, `lesson-03/lesson.md`

- [ ] **Step 1: Normalize README wrappers**

Keep the detailed four-field format. Link `lesson.md` and `answers.md`. Preserve Lesson 03’s `Before you start` scratch-copy instructions verbatim.

- [ ] **Step 2: Normalize headings only**

Replace `CONCEPT`, `WORKED EXAMPLES`, `YOUR TURN`, `QUIZ`, `PITFALLS`, `RECAP`, and `LOOK AHEAD` with `The concept`, `Worked examples`, `Your turn`, `Quiz`, `Pitfalls`, `Recap`, and `Look ahead` respectively. Do not alter content below the headings.

- [ ] **Step 3: Verify GREEN**

Run `python3 -m unittest tools/test_audit_legacy_lessons.py -v`.

Expected: all tests pass.

### Task 3: Verify safety and commit

**Files:**

- Verify: `lesson-01/lesson.md`, `lesson-02/lesson.md`, `lesson-03/lesson.md`
- Verify: `data/chinook.db`, `data/chinook-scratch.db`

- [ ] **Step 1: Run the legacy auditor**

Run `for lesson in lesson-01 lesson-02 lesson-03; do python3 tools/audit_legacy_lessons.py "$lesson/lesson.md" data/chinook.db || exit $?; done`.

Expected: each lesson reports `0 FAIL`.

- [ ] **Step 2: Verify database hashes**

Run `md5sum data/chinook.db data/chinook-scratch.db`.

Expected: both hashes are `99fe99c99d23033719bf9e277291e351`.

- [ ] **Step 3: Commit**

Stage only the six lesson files and `tools/test_audit_legacy_lessons.py`, then commit with message `docs: standardize lessons 1-3 format`.
