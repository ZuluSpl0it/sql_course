# Lesson 05 — Quiz Answer Key

Attempt the Quiz in `lesson.md` before opening this file. This lesson only
reads, so run everything against `data/chinook.db`.

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

## Your turn (reference)

**1.**

```sql
SELECT t.Name AS track, a.Title AS album
FROM   Track t JOIN Album a ON a.AlbumId = t.AlbumId
ORDER  BY t.Name
LIMIT  10;
```

First three (alphabetical; note the quotes/symbols sort before letters):
`"40"` → War; `"?"` → Lost, Season 2; `"Eine Kleine Nachtmusik" Serenade In
G, K. 525: I. Allegro` → Sir Neville Marriner: A Celebration.

**2.** Iron Maiden: **21** albums. Lenny Kravitz: **1** album
("Greatest Hits" — the 57-track one).

```sql
SELECT ar.Name, COUNT(a.AlbumId)
FROM   Artist ar JOIN Album a ON a.ArtistId = ar.ArtistId
WHERE  ar.Name IN ('Iron Maiden','Lenny Kravitz')
GROUP  BY ar.ArtistId, ar.Name;
```

**3.**

```sql
SELECT c.FirstName, c.LastName, e.FirstName AS rep_first, e.LastName AS rep_last
FROM   Customer c LEFT JOIN Employee e ON e.EmployeeId = c.SupportRepId
ORDER  BY c.CustomerId
LIMIT  5;
```

Every customer has a support rep (0 NULLs), so `INNER JOIN` would work here
too — but `LEFT JOIN` is the safer habit. Sample: Luís Gonçalves → Jane
Peacock; Leonie Köhler → Steve Johnson; François Tremblay → Jane Peacock;
Bjørn Hansen → Margaret Park; František Wichterlová → Margaret Park.

**4.**

```sql
SELECT ar.Name, COUNT(t.TrackId) AS tracks
FROM   Track t
JOIN   Album  a  ON a.AlbumId  = t.AlbumId
JOIN   Artist ar ON ar.ArtistId = a.ArtistId
GROUP  BY ar.ArtistId, ar.Name
ORDER  BY tracks DESC
LIMIT  5;
```

```
Name          tracks
------------  ------
Iron Maiden   213
U2            135
Led Zeppelin  114
Metallica     112
Deep Purple   92
```

**5.** Artists with at least one album:

```sql
SELECT COUNT(DISTINCT ar.ArtistId)
FROM   Artist ar JOIN Album a ON a.ArtistId = ar.ArtistId;
```

→ **204**. (The other 71 of the 275 artists have no albums.)
