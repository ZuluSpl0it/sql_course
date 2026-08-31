# Lesson 10 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file.

## Quiz

### Q1 — `SCAN` versus `SEARCH`

A `SCAN` reads every candidate row in a table or index. A `SEARCH` has a condition that lets SQLite narrow candidates, commonly through an index or an `INTEGER PRIMARY KEY` lookup.

### Q2 — covering index

`USING COVERING INDEX` means every column needed by a query is already in the index, so SQLite can answer without reading table rows afterward.

### Q3 — plan shape is not timing

The plan does not measure elapsed time. On a small table, a scan may be cheap enough that a `SEARCH` makes no observable difference.

### Q4 — leading wildcard

`'%The%'` has no known starting prefix, so an ordered index cannot jump to the first possible match. SQLite must inspect every candidate name.

### Q5 — index cost

An index uses storage and must be updated whenever an indexed value is inserted, changed, or deleted.

### Q6 — doubled revenue

The join changed the row grain: one sales line was repeated for multiple playlist memberships. Check join cardinality and row count before the `SUM`.
