# Auditor consolidation design

## Goal

Leave one maintained course-audit command and one corresponding test module in
`tools/`.

## Changes

- Move `extract_sql_blocks` and `split_sql` into `tools/audit_course.py`.
- Move the regression coverage from `tools/test_audit_legacy_lessons.py` into
  `tools/test_audit_course.py`.
- Remove `tools/audit_legacy_lessons.py`,
  `tools/test_audit_legacy_lessons.py`, and the untracked unfinished
  `tools/build_lesson09.py`.

Historical planning records that mention the removed files remain unchanged:
they describe prior work and are not active instructions.

## Validation

The single test command is `python3 -m unittest tools.test_audit_course -v`.
The single course command is `python3 tools/audit_course.py`. Both must pass
after consolidation, and no removed script may remain in `tools/`.
