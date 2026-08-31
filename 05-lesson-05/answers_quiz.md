# Lesson 05 — Quiz Answer Key

Attempt the quiz in `lesson.md` before opening this file. This lesson only
reads, so run everything against `12-data/chinook.db`.

---

## Quiz

### Q1 — what does an `INNER JOIN` drop?

Rows from either side that have **no matching row on the other side**. If a
left row has no right row satisfying the `ON` (or vice versa), that left row
doesn't appear. (Contrast `LEFT JOIN`, which keeps every left row.)

### Q2 — why `LEFT JOIN` in the self-join?

The top boss (Andrew Adams) has `ReportsTo = NULL` — there's no manager row
to match. An `INNER JOIN` would **drop him entirely**, because `NULL` never
equals anything. `LEFT JOIN` keeps him, showing a `NULL` manager.

### Q3 — why is the joined `SUM(Invoice.Total)` ~9× too large?

The `Invoice`→`InvoiceLine` join is one-to-many: each invoice row is repeated
once per line item (≈ 5.4× on average here, and the *specific* invoices in
the sum happen to average ≈ 8.95 line items). So `i.Total` gets added once
per line item instead of once — the join **fanned out** the invoice column.
2,328.60 becomes 20,848.62.

### Q4 — list every artist who has no albums

```sql
SELECT ar.Name
FROM   Artist ar
LEFT   JOIN Album a ON a.ArtistId = ar.ArtistId
WHERE  a.AlbumId IS NULL
ORDER  BY ar.ArtistId;
```

Returns **71 artists** (the `LEFT JOIN` keeps all 275; the `IS NULL` filter
keeps only the ones with no matching album). Any of `Album.AlbumId`,
`a.Title`, or `a.AlbumId` works in the `IS NULL` test — they're all NULL
together when there's no match.

### Q5 — `JOIN` and `INNER JOIN` the same?

**True.** `JOIN` is short for `INNER JOIN` in every standard engine,
including SQLite. They're identical.

### Q6 (stretch) — employee, manager, and # reporting to that manager

```sql
SELECT e.FirstName || ' ' || e.LastName            AS employee,
       COALESCE(m.FirstName || ' ' || m.LastName, '(none)') AS manager,
       COUNT(s.EmployeeId)                          AS reports_to_manager
FROM   Employee e
LEFT   JOIN Employee m ON m.EmployeeId = e.ReportsTo
LEFT   JOIN Employee s ON s.ReportsTo  = m.EmployeeId
GROUP  BY e.EmployeeId, e.FirstName, e.LastName,
          m.FirstName, m.LastName
ORDER  BY e.EmployeeId;
```

```
employee        manager         reports_to_manager
--------------  --------------  ------------------
Andrew Adams    (none)          0
Nancy Edwards   Andrew Adams    2
Jane Peacock    Nancy Edwards   3
Margaret Park   Nancy Edwards   3
Steve Johnson   Nancy Edwards   3
Michael Mitchell Andrew Adams   2
Robert King     Michael Mitchell 2
Laura Callahan  Michael Mitchell 2
```

Two self joins on one table: `m` = the employee's manager, `s` = anyone
reporting to that manager. `COUNT(s.EmployeeId)` counts only non-NULL
matches, so Andrew (no manager) shows 0. The `GROUP BY` must list *all*
non-aggregated selected columns (SQLite lets you get away with less, but
this is the portable form).

---
