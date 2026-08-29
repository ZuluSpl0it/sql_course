# Lesson 06: Joins II & Set Operations

Lesson 05 taught you to *connect* tables. This lesson adds the two joins you
haven't seen yet — `CROSS JOIN` (pair *everything*) and `FULL JOIN` (keep
unmatched rows from **both** sides) — and then switches gears to the **set
operators**: `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`. Set operators
treat query results like sets of rows and combine them the way you'd combine
circles in a Venn diagram.

**No scratch copy needed.** This lesson only reads.

---

## 1. The concept

### `CROSS JOIN` — every row with every row

So far every `JOIN` had an `ON` condition. What happens without one?

```sql
SELECT e.LastName, g.Name
FROM   Employee e
CROSS  JOIN  Genre g
LIMIT  5;
```

A **cross join** (also called a *cartesian product*) pairs **every** row of
the left table with **every** row of the right table. 8 employees × 25
genres = **200 rows**. No matching, no filtering — pure multiplication.

You rarely *want* a bare cross join, but you will *meet* one: it's exactly
what you get when you forget the `ON` clause (Example 1).

### `FULL JOIN` — keep the unmatched on both sides

Recall the family from Lesson 05:

| join | keeps rows from… |
|---|---|
| `INNER JOIN` | both sides — only where they match |
| `LEFT JOIN`  | **all** left-side rows (+ matches from the right) |
| `RIGHT JOIN` | **all** right-side rows (+ matches from the left) |
| `FULL JOIN`  | **all rows from both sides** — unmatched sides get NULLs |

Think of the org chart. A `LEFT JOIN` from employees to their reports keeps
every *employee* — but it looks only *down* the hierarchy, so it can never
show the fact that the CEO answers to no one. A `FULL JOIN` keeps everyone
in both directions: managers who have no reports **and** the employee who
has no manager.

**SQLite's catch:** our pinned SQLite **3.31 does not support `FULL JOIN`
or `RIGHT JOIN` at all** — it answers `Error: RIGHT and FULL OUTER JOINs are
not currently supported`. (SQLite 3.39, released mid-2023, added them;
PostgreSQL has always had them — so you'll write this for real on other
engines, and the emulation below is the portable version.) The trick is two
`LEFT JOIN`s plus a `UNION`:

```sql
-- full outer join: managers ↔ their reports, both sides complete
SELECT e.EmployeeId AS manager_id, e.FirstName AS manager,
       r.EmployeeId AS report_id,   r.FirstName AS report
FROM   Employee e
LEFT   JOIN  Employee r ON r.ReportsTo = e.EmployeeId
UNION
SELECT e.EmployeeId, e.FirstName, r.EmployeeId, r.FirstName
FROM   Employee r
LEFT   JOIN  Employee e ON e.EmployeeId = r.ReportsTo
WHERE  e.EmployeeId IS NULL        -- only what the first branch missed
ORDER  BY manager_id, report_id;
```

The first branch is a plain left join, manager → reports. The second branch
looks at the *same relationship from the other side*, and the
`WHERE e.EmployeeId IS NULL` keeps only the rows where that second-side
join **failed** — employees who report to no one. `UNION` glues the two
together. (The `IS NULL` test is the exact "find the unmatched" recipe from
Lesson 05.)

### Set operators — queries as sets

A query result is just a **set of rows**. Four operators combine sets:

| operator | Venn name | keeps |
|---|---|---|
| `UNION` | union (∪) | rows in **either** query, duplicates removed |
| `UNION ALL` | multiset union | rows in either query, **duplicates kept** |
| `INTERSECT` | intersection (∩) | rows in **both** queries |
| `EXCEPT` | difference (A − B) | rows in the **first**, not the second |

The rules:

- The two queries need the **same number of columns** with compatible
  types. Rows are compared **by position** — column 1 vs column 1 — the
  *names* don't matter (the result simply takes the left query's names).
- `UNION` and `INTERSECT` **deduplicate** (identical rows collapse to one);
  `UNION ALL` keeps every row.
- In SQLite, an `ORDER BY` / `LIMIT` written at the end of a compound
  query applies to the **whole combination**, not to the last branch:

```sql
-- every track that is in playlist 5 (90's Music) OR in playlist 12 (Classical)
SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 5
UNION
SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 12;
```

1477 tracks ∪ 75 tracks, with the 41 that appear in **both** counted once
→ **1511 rows**. (`UNION ALL` would give 1552.)

---

## 2. Worked examples

### Example 1 — the cross join, on purpose and by accident

On purpose — every employee paired with every genre:

```sql
SELECT e.LastName AS employee,
       g.Name     AS genre
FROM   Employee e
CROSS  JOIN  Genre g
ORDER  BY e.EmployeeId, g.GenreId
LIMIT  6;
```

```
employee  genre
--------  -------------------
Adams     Rock
Adams     Jazz
Adams     Metal
Adams     Alternative & Punk
Adams     Rock And Roll
Adams     Blues
```

The full result has 8 × 25 = **200 rows** — every manager × every genre,
most of them meaningless. That's the smell test for a cross join: the
result is *complete* but not *meaningful*.

Now the accidental version — the classic beginner mistake. You meant to
join `Track` to `Album`, but you forget the `ON`:

```sql
SELECT t.Name, a.Title
FROM   Track t,
       Album a
LIMIT  5;
```

```
Name                                     Title
---------------------------------------  -------------------------------------
For Those About To Rock (We Salute You)  For Those About To Rock We Salute You
For Those About To Rock (We Salute You)  Balls to the Wall
For Those About To Rock (We Salute You)  Restless and Wild
For Those About To Rock (We Salute You)  Let There Be Rock
For Those About To Rock (We Salute You)  Big Ones
```

The first row even *looks* right — track 1 and album 1 happen to be the
same AC/DC release. Every row after that is coincidence: track 1 (AC/DC)
is "on" the albums *Balls to the Wall* (Accept) and *Restless and Wild*
(Alice Cooper). Without an `ON`, you get the cartesian product: 3503 × 347
= **1,215,541 rows** of pairs. The query *runs*, the output *looks*
plausible — which is why this bug is sneaky. The tell is the row count: a
real track→album join has 3,503 rows; the cross product has a million and
a quarter.

### Example 2 — `FULL JOIN` by hand: the complete org chart

SQLite 3.31 refuses the keyword, so we use the pattern from the concept:

```sql
SELECT e.EmployeeId AS manager_id, e.FirstName AS manager,
       r.EmployeeId AS report_id,   r.FirstName AS report
FROM   Employee e
LEFT   JOIN  Employee r ON r.ReportsTo = e.EmployeeId
UNION
SELECT e.EmployeeId, e.FirstName, r.EmployeeId, r.FirstName
FROM   Employee r
LEFT   JOIN  Employee e ON e.EmployeeId = r.ReportsTo
WHERE  e.EmployeeId IS NULL
ORDER  BY manager_id, report_id;
```

```
manager_id  manager   report_id  report
----------  --------  ---------  --------
                      1          Andrew      ← CEO: reports to no one
1           Andrew    2          Nancy
1           Andrew    6          Michael
2           Nancy     3          Jane
2           Nancy     4          Margaret
2           Nancy     5          Steve
3           Jane
4           Margaret
5           Steve
6           Michael   7          Robert
6           Michael   8          Laura
7           Robert
8           Laura
```

(Note the first row: `NULL` sorts before every id, so the CEO's blank
manager columns land at the top.)
13 rows. Anatomy:

- **7 matched rows** — a manager who actually has reports (Adams →
  Nancy/Michael, Nancy → Jane/Margaret/Steve, Michael → Robert/Laura).
- **5 rows with a blank report** — Jane, Margaret, Steve, Robert, Laura.
  They come from the first branch's left-join: they're employees with
  zero reports, so the join produced NULL.
- **1 row with a blank manager** — Andrew, the General Manager,
  appearing on the *report* side as `(NULL, NULL, 1, Andrew)`. He's the
  *only* employee with `ReportsTo` NULL, so the second branch (which
  keeps only rows where its own join failed) contains exactly one row:
  him, with the manager columns empty.

If you'd written only the first branch, you'd get 12 rows: the 7 matched
pairs plus the 5 report-less employees — but the CEO's *"reports to no
one"* fact would never appear, because the first branch only looks *down*
the hierarchy. The second branch exists to look *up*, and it finds exactly
the one row the first branch cannot produce. That division of labour —
**first branch: everything the left join keeps; second branch: only what
the left join dropped** — is the whole FULL JOIN emulation, and it
generalizes to any two tables.

### Example 3 — `UNION` vs `UNION ALL`: duplicates that are and aren't data

Chinook ships **two** playlists both called "Music":

```
PlaylistId  Name   tracks
----------  -----  ------
1           Music  3290
8           Music  3290
```

(`TV Shows` is doubled too — 3 and 10, both with 213 tracks.) You want
"every track in either Music playlist". First try:

```sql
SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 1
UNION ALL
SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 8;
```

→ **6580 rows**. But are there 6,580 *different* tracks? The two playlists
hold identical sets, so no:

```sql
SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 1
UNION
SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 8;
```

→ **3290 rows**. Same two queries, one keyword apart, half the rows.

A smaller pair to watch the mechanism. The song *The Trooper* (Iron
Maiden) exists on two different albums (95 and 102) as **two different
physical tracks** — but if we only look at the *name*, they're the same
string. Select the name only:

```sql
SELECT t.Name
FROM   Track t WHERE t.AlbumId = 95 AND t.Name = 'The Trooper'
UNION
SELECT t.Name
FROM   Track t WHERE t.AlbumId = 102 AND t.Name = 'The Trooper';
```

→ **1 row**: `The Trooper`. The two recordings collapsed into one because
`UNION` only sees a single `Name` value, and the two branches produced
the identical value `The Trooper`. Now run the exact same query with
`UNION ALL` instead:

```sql
SELECT t.Name
FROM   Track t WHERE t.AlbumId = 95 AND t.Name = 'The Trooper'
UNION ALL
SELECT t.Name
FROM   Track t WHERE t.AlbumId = 102 AND t.Name = 'The Trooper';
```

→ **2 rows**: `The Trooper` twice. Same inputs, one keyword apart, double
the rows.

Rule of thumb: **`UNION` when you want a set of distinct rows** (the
default, and the one that "feels right"); **`UNION ALL` when you're
stacking raw rows** (faster, and correct when each branch is a different
slice of data that shouldn't deduplicate — e.g. sales from two stores,
where the same (date, product) pair *is* a real event). When unsure, ask:
*would a duplicated row be wrong, or would it be real data?*

One caveat, because it bites people: `UNION` compares **values**, not row
identities. Two rows with the same values *are* the same row to a
`UNION`, no matter which table they came from. In Example 2 that's a
feature (the two branches really do share rows); in the Trooper query
above it's why the two different recordings collapsed into one.

### Example 4 — `INTERSECT`: what do these two playlists share?

"Which tracks are on **both** the 90's Music playlist and the Classical
playlist?"

```sql
SELECT t.Name
FROM   (
         SELECT pt.TrackId
         FROM   PlaylistTrack pt WHERE pt.PlaylistId = 5
         INTERSECT
         SELECT pt.TrackId
         FROM   PlaylistTrack pt WHERE pt.PlaylistId = 12
       ) shared
JOIN   Track t ON t.TrackId = shared.TrackId
ORDER  BY t.Name
LIMIT  8;
```

```
Name
------------------------------------------------------------------------------
A Midsummer Night's Dream, Op.61 Incidental Music: No.7 Notturno
Aria Mit 30 Veränderungen, BWV 988 "Goldberg Variations": Aria
Ave Maria
Carmen: Overture
Carmina Burana: O Fortuna
Cavalleria Rusticana \ Act \ Intermezzo Sinfonico
Concerto for Piano No. 2 in F Minor, Op. 21: II. Larghetto
Concerto for Violin, Strings and Continuo in G Major, Op. 3, No. 9: I. Allegro
```

41 tracks in total. (Why the subquery? `INTERSECT` needs both sides to
select the *same column* — here `TrackId` — so we find the shared IDs
first, then join to `Track` for the names. You'll meet this shape again in
Lesson 07.)

Now the trap that set operators are famous for. Iron Maiden's albums
*A Real Dead One* (95) and *Live After Death* (102) share **six song
titles** — *The Trooper*, *Hallowed Be Thy Name*, *2 Minutes To Midnight*,
and three more:

```sql
SELECT t.Name
FROM   Track t WHERE t.AlbumId = 95
INTERSECT
SELECT t.Name
FROM   Track t WHERE t.AlbumId = 102
ORDER  BY t.Name;
```

→ 6 rows. But compare that to the same query matching on the **key**:

```sql
SELECT COUNT(*)
FROM   (
         SELECT t.TrackId FROM Track t WHERE t.AlbumId = 95
         INTERSECT
         SELECT t.TrackId FROM Track t WHERE t.AlbumId = 102
       );
```

→ **0**. The albums share no actual tracks — only song titles. A
`TrackId`-based intersection says "same recording"; a `Name`-based one
says "same string". **Match on the primary key whenever the comparison
should be about identity**, and only match on descriptive columns when you
genuinely mean "same value". (And note that the two branches above compare
by *position* — both select a single `Name` column; the names in the two
`SELECT`s never have to match anything else.)

### Example 5 — `EXCEPT`: in here, but not over there

The inverse question: "which tracks are on the 90's Music playlist but
**not** on the Classical playlist?"

```sql
SELECT COUNT(*) AS only90s
FROM   (
         SELECT pt.TrackId
         FROM   PlaylistTrack pt WHERE pt.PlaylistId = 5
         EXCEPT
         SELECT pt.TrackId
         FROM   PlaylistTrack pt WHERE pt.PlaylistId = 12
       ) only90s;
```

```
only90s
-------
1436
```

1477 − 41 = 1436 ✓. Now the *idempotence check* that makes `EXCEPT` a
genuine data-quality tool. Is "Classical 101 – The Basics" (15) entirely
contained in the big Classical playlist (12)?

```sql
SELECT COUNT(*) AS not_in_classical
FROM   (
         SELECT pt.TrackId
         FROM   PlaylistTrack pt WHERE pt.PlaylistId = 15
         EXCEPT
         SELECT pt.TrackId
         FROM   PlaylistTrack pt WHERE pt.PlaylistId = 12
       ) not_in_classical;
```

```
not_in_classical
----------------
0
```

**Zero** means "everything in the first set is already in the second" —
the Basics playlist is a subset of Classical. The same trick is a
set-equality test: run both directions, and if *both* return 0, the sets
are equal. Try it on the two "Music" playlists:

```sql
SELECT (
         SELECT COUNT(*)
         FROM   (
                  SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 1
                  EXCEPT
                  SELECT pt2.TrackId FROM PlaylistTrack pt2 WHERE pt2.PlaylistId = 8
                )
       ) + (
         SELECT COUNT(*)
         FROM   (
                  SELECT pt2.TrackId FROM PlaylistTrack pt2 WHERE pt2.PlaylistId = 8
                  EXCEPT
                  SELECT pt.TrackId FROM PlaylistTrack pt WHERE pt.PlaylistId = 1
                )
       ) AS symmetric_difference_count;
```

```
symmetric_difference_count
--------------------------
0
```

The two differences sum to **0**.

`Music(1) − Music(8)` = 0 **and** `Music(8) − Music(1)` = 0 → the two
playlists are the same set, twice. (You could also just `COUNT(*)` the
`INTERSECT` and check it equals both counts — same idea, different
operator.)

---

## 3. Your turn

Do these in litecli against `data/chinook.db` — this lesson only reads, so
the scratch copy is not needed. Answers in `answers.md`.

1. **Cross join, on purpose.** How many rows does
   `SELECT * FROM MediaType, Genre` produce? (No `JOIN` at all — that's a
   cross join in the old comma syntax.)
2. **Set size.** How many *distinct* tracks are in playlist 3 (TV Shows)
   **or** playlist 10 (TV Shows)? Use `UNION`. Then run the same query
   with `UNION ALL` — how many rows does that give, and what does the
   difference between the two numbers tell you about these two playlists?
3. **Intersection.** How many tracks appear on **both** playlist 12
   (Classical) and playlist 15 (Classical 101 – The Basics)? (`INTERSECT`)
4. **Difference.** How many tracks on the Heavy Metal Classic playlist (17)
   are **not** on the Classical playlist (12)? (`EXCEPT`)
5. **FULL join, by hand.** Using the two-branch pattern from Example 2,
   list every employee together with the employee they report to — keeping
   *both* sides complete: employees with no manager **and** employees whom
   nobody reports to. (It's the Lesson 05 org chart, upgraded to a full
   outer join.)

---

## 4. Quiz

1. `Employee` has 8 rows and `Genre` has 25. How many rows does
   `SELECT * FROM Employee, Genre` return — and would the result be
   useful?
2. SQLite answers `Error: RIGHT and FULL OUTER JOINs are not currently
   supported`. Name the supported join that keeps **all rows from the
   right table** (hint: swap the tables), and say what you'd write in
   SQLite to get a full outer join instead.
3. `UNION` and `UNION ALL` over two queries returning 30 and 10 rows each,
   with 4 identical rows in common. How many rows does each operator
   return?
4. `INTERSECT` compares the two queries' rows. Are the column **names**,
   the column **positions**, or the **tables the rows came from** what get
   compared?
5. `A EXCEPT B` returns 0 rows. What can you conclude about A and B? Now
   `B EXCEPT A` also returns 0 — what can you conclude now?
6. **Stretch.** In Example 2's output, how many rows have a blank manager
   and how many have a blank report? Can any row be blank on **both**
   sides? Why or why not?

---

## 5. Pitfalls

1. **Forgetting `ON` doesn't error — it multiplies.** `FROM Track t,
   Album a` runs happily and produces 1,215,541 garbage rows (Example 1).
   If a join's row count looks like the *product* of the two tables'
   sizes, your condition is missing.
2. **`FULL JOIN` (and `RIGHT JOIN`) don't exist in SQLite 3.31.** The
   keywords are a hard error on this engine; the two-`LEFT JOIN` +
   `UNION` pattern is the portable substitute. (SQLite ≥ 3.39 and
   PostgreSQL accept `FULL [OUTER] JOIN` directly.)
3. **The emulation's second branch must be filtered.** Without
   `WHERE e.EmployeeId IS NULL` the second branch would also list every
   employee *as* a report — and the query gets worse if you try to write
   a *symmetric* version that adds both directions (employee→manager and
   manager→employee) in separate branches: you get **20 rows instead of
   13**, because each matched relationship appears once per direction and
   the columns sit in different positions, so `UNION`'s deduplication
   can't merge them. The filter is what makes the second branch cover
   only the piece of the result the first branch cannot produce.
4. **`UNION` dedupes by value, not by identity.** Two physically
   different rows with identical values become one. Fine for "distinct
   tracks in either playlist"; wrong when the duplication is *meaningful*
   (two stores selling the same item the same day) — use `UNION ALL`
   there.
5. **`ORDER BY` / `LIMIT` at the end of a compound query govern the whole
   combination**, not the last branch. To limit each branch separately,
   wrap each in its own derived table:
   `SELECT * FROM (… LIMIT 3) x UNION SELECT * FROM (… LIMIT 3) y`
   (a bare `(SELECT … LIMIT 3)` inside a `UNION` is a syntax error in
   SQLite 3.31).
6. **Set operators compare by position, and by value.** The two sides
   need matching column counts and compatible types; column names are
   irrelevant. If you find yourself `INTERSECT`-ing `t.Name` when you mean
   "same track", you've actually asked "same title" — compare the key
   (`TrackId`) instead (Example 4).

---

## 6. Recap

- **`CROSS JOIN`** pairs every row with every row — 8 × 25 = 200. Legit
  for small option grids; the accidental result of a missing `ON`.
- **`FULL JOIN`** keeps unmatched rows from both sides; SQLite 3.31 can't
  spell it, so emulate: two `LEFT JOIN`s (one per direction), `UNION`,
  with the second branch filtered to its unmatched rows only.
- **`UNION`** = distinct rows from either query · **`UNION ALL`** = all
  rows from both · **`INTERSECT`** = rows in both · **`EXCEPT`** = rows in
  the first, not the second.
- Set operators compare rows **by position and by value**; names and
  origins are invisible to them. Match on keys for identity, on values for
  "same string".
- `A EXCEPT B → 0` proves `A ⊆ B`; both directions → 0 proves `A = B`.
  A small, sharp toolkit for data-quality checks.

Next up, **Lesson 07: Subqueries & CTEs** — the moment you start putting a
query *inside* another query.
