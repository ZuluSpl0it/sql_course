# Northwind Final Test Design

## Goal

Create a self-graded, 50-question cumulative assessment on the unfamiliar
Northwind SQLite database, plus concise answer explanations and guided
walkthroughs for the hardest integrated problems.

## Deliverables

- `data/northwind.db`, pinned to SHA-256
  `2f4f5c68dfcd33ba27373eae48c7a4869800c68095ee0f9f0da494f83382a877`.
- `final-test/README.md`, `exam.md`, `answers.md`, and `guided-solutions.md`.
- Root course-map links to the final test.

## Assessment shape

Six sections: schema discovery (6), retrieval/filtering (10), joins and NULL
handling (10), aggregation (9), subqueries/CTEs/sets (7), and performance plus
four integrated case studies (8), totaling 50 questions.

## Self-grading design

Each answer provides a recommended query, why it is preferred, credit
conditions, lesson review references, and meaningful valid alternatives with
trade-offs. Guided solutions walk through eight hardest questions: table/key
choice, row grain, incremental query construction, likely wrong turns, and
review links.

## Safety and validation

Core questions are read-only. Any temporary-index exercise requires a fresh
`data/northwind-scratch.db` and drops the index. Every answer query is checked
against the shipped database; checksums protect both course databases.
