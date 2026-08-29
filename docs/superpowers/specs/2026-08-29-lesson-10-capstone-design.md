# Lesson 10 Performance and Capstone Design

## Goal

Finish the SQL course with an offline, Chinook-based lesson that teaches plan
reading, index judgment, safe report construction, query refactoring, and
integrated capstone practice.

## Files

- Create `lesson-10/README.md`, `lesson-10/lesson.md`, and
  `lesson-10/answers.md`.
- Modify the root `README.md` course map to link Lesson 10.

## Constraints

- Use a scratch copy only; never change `data/chinook.db`.
- Create and drop only temporary `idx_l10_...` indexes. No DML, table changes,
  views, generated scripts, metadata JSON, or shared-auditor changes.
- Use seven major lesson sections and the detailed README template.
- Keep to at most 12 SQL fences.
- Treat `EXPLAIN QUERY PLAN` as plan shape, not a timing benchmark. Its display
  varies by client, so prose—not an audited fixed table—describes plan output.

## Content

Worked examples cover baseline planning, one useful narrow index, one
non-sargable wildcard case, fan-out-safe revenue reporting, a CTE refactor,
and teardown verification. Your Turn, Quiz, and answers combine lessons 1–9.

## Validation

- Add a regression test for the Lesson 10 README and seven-section structure.
- Run the legacy auditor against Lesson 10; document plan-only skips.
- Verify temporary-index cleanup on a unique `/tmp` database copy.
- Verify the pristine database MD5 is `99fe99c99d23033719bf9e277291e351`.
