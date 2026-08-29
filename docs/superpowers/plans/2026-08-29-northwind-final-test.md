# Northwind Final Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a verified 50-question Northwind final test with self-grading and guided teaching support.

**Architecture:** The exam has no answers; the answer key provides canonical SQL and lesson references; guided solutions teach only the hardest integrated tasks. Northwind remains pristine and any index experiment runs on a scratch copy.

**Tech Stack:** Markdown, SQLite, SHA-256.

---

### Tasks

- [ ] Verify the downloaded database schema, row counts, and checksum.
- [ ] Create the final-test README, exam, answer key, and guided-solutions files.
- [ ] Validate all answer-key SQL against `data/northwind.db` or a temporary copy for DDL.
- [ ] Verify local Markdown links, checksums, and final-test file structure.
- [ ] Update the root README and commit the assessment separately from Lesson 10.
