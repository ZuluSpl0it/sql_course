# Lesson 07: Subqueries & CTEs

Lesson 06 taught you to treat a query's result as a **set of rows** and to
combine sets with `UNION`, `INTERSECT`, and friends. This lesson goes a
level deeper: you can put a query *inside* another query. A **subquery** is
just that — a `SELECT` whose result you use somewhere inside a bigger
`SELECT`. There are three places it can live, and this lesson covers all
three, plus the two forms of `WITH` that let you *name* a subquery.

**No scratch copy needed.** This lesson only reads.

---

## 1. The concept
### A query inside a query
The simplest subquery is a single value sitting in the `SELECT` list. Here
one returns the store's grand total — the same $2,328.60 you've been
computing since Lesson 05 — and prints it once, as a column, next to every
invoice:
```sql
SELECT i.InvoiceId, i.Total, (SELECT ROUND(SUM(Total), 2) FROM Invoice) AS store_total FROM Invoice i ORDER BY i.InvoiceId LIMIT 4;
```

```
InvoiceId  Total  store_total
---------  -----  -----------
1          1.98   2328.6
2          3.96   2328.6
3          5.94   2328.6
4          8.91   2328.6
```

The subquery `(SELECT ROUND(SUM(Total), 2) FROM Invoice)` never mentions the
outer query, so SQLite runs it *once* and copies the result into every row.
That's a **scalar subquery**: it must come back as exactly one row with
exactly one value, or the query is in trouble (Pitfall 1 is what goes wrong
when it quietly comes back as more than one row).
The more useful version **correlates** the inner query with the outer one:
it refers to a column of the current outer row, so SQLite re-runs it *for
each* outer row. Next to each invoice, here is that invoice's customer's
total spend across *all* their invoices:
```sql
SELECT i.InvoiceId, i.CustomerId, i.Total, (SELECT ROUND(SUM(i2.Total), 2) FROM Invoice i2 WHERE i2.CustomerId = i.CustomerId) AS customer_total FROM Invoice i ORDER BY i.InvoiceId LIMIT 4;
```

```
InvoiceId  CustomerId  Total  customer_total
---------  ----------  -----  --------------
1          2           1.98   37.62
2          4           3.96   39.62
3          8           5.94   37.62
4          14          8.91   37.62
```

The inner query mentions `i.CustomerId` — a column of the outer `Invoice`
row — so it is re-evaluated per row. This is how you attach a per-group
number to every detail row without a `JOIN` or a `GROUP BY`.
### The three slots a subquery can occupy
| slot | example | the subquery is |
|---|---|---|
| `SELECT` list | `(SELECT SUM(Total) FROM Invoice)` | one value (a scalar) |
| `WHERE` | `… WHERE GenreId IN (…)` / `EXISTS (…)` | a set test / yes-or-no |
| `FROM` | `… FROM (SELECT …) AS x` | a table — a **derived table** |
This lesson walks each slot in turn, then `WITH`, which is really the
`FROM` slot with a name on it.
### `WITH`, and `WITH RECURSIVE`
A **common table expression** (CTE) gives a subquery a name so you can use
it — or use it twice — by name instead of repeating the whole thing. The
smallest possible CTE just names a number and reads it twice:
```sql
WITH c AS (SELECT COUNT(*) AS n FROM Invoice) SELECT c.n AS from_cte, (SELECT COUNT(*) FROM Invoice) AS inline FROM c;
```

```
from_cte  inline
--------  ------
412       412
```

The `WITH c AS (…)` clause defines `c`; the `SELECT` then references `c.n`
by name. A CTE is a *table*, so — like any table — it has to appear in the
`FROM` clause for the `SELECT` to see it (delete `FROM c` and you get `no
such column: c.n`). The two columns return the same `412`: the left reads the
CTE by name, the right is the identical subquery written inline. The only
difference is that the CTE has a *name* you can point at, and you may point
at it as often as you like.
A **recursive** CTE adds one twist: the second part of the `WITH` is
allowed to read *the CTE itself*. That lets it walk a relationship one step
at a time, re-joining until there's nothing left to reach. The org chart is
exactly such a relationship — Example 5 uses it to climb `Employee`
from the CEO to the deepest employee, no matter how deep that turns out
to be.

---
## 2. Worked examples
### Example 1 — the correlated scalar: one number per row
Worked example 1 in the concept already showed the correlated form; let's
make the contrast between *correlated* and *not* impossible to miss, using
customers. First, the store-wide total, the same for every row:
```sql
SELECT c.CustomerId, c.FirstName, (SELECT ROUND(SUM(Total), 2) FROM Invoice) AS customer_total FROM Customer c ORDER BY c.CustomerId LIMIT 5;
```

```
CustomerId  FirstName  customer_total
----------  ---------  --------------
1           Luís       2328.6
2           Leonie     2328.6
3           François   2328.6
4           Bjørn      2328.6
5           František  2328.6
```

Now the same query **correlated** to each customer — it returns *that*
customer's own total instead:
```sql
SELECT c.CustomerId, c.FirstName, (SELECT ROUND(SUM(i2.Total), 2) FROM Invoice i2 WHERE i2.CustomerId = c.CustomerId) AS customer_total FROM Customer c ORDER BY c.CustomerId LIMIT 5;
```

```
CustomerId  FirstName  customer_total
----------  ---------  --------------
1           Luís       39.62
2           Leonie     37.62
3           François   39.62
4           Bjørn      39.62
5           František  40.62
```

Same shape, one added `WHERE` clause in the subquery, and the fourth column
goes from a constant $2,328.60 to a number that's different on every row.
That one `WHERE i2.CustomerId = c.CustomerId` is the entire difference
between a scalar subquery that *correlates* and one that doesn't — and
forgetting it is the bug in Pitfall 2.
### Example 2 — `IN` vs `EXISTS`: two ways to ask "does it have a match?"
Suppose you want every artist who has at least one Rock track. You can ask
"is this artist in the set of Rock artists?" with `IN`:
```sql
SELECT a.ArtistId, a.Name FROM Artist a WHERE a.ArtistId IN (SELECT al.ArtistId FROM Album al JOIN Track t ON al.AlbumId = t.AlbumId WHERE t.GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Rock')) ORDER BY a.ArtistId LIMIT 5;
```

```
ArtistId  Name
--------  -----------------
1         AC/DC
2         Accept
3         Aerosmith
4         Alanis Morissette
5         Alice In Chains
```

Or you can ask "does there *exist* a Rock track for this artist?" with
`EXISTS`, correlating the inner query to the outer artist:
```sql
SELECT a.ArtistId, a.Name FROM Artist a WHERE EXISTS (SELECT 1 FROM Album al JOIN Track t ON al.AlbumId = t.AlbumId WHERE al.ArtistId = a.ArtistId AND t.GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Rock')) ORDER BY a.ArtistId LIMIT 5;
```

```
ArtistId  Name
--------  -----------------
1         AC/DC
2         Accept
3         Aerosmith
4         Alanis Morissette
5         Alice In Chains
```

Both return **51** artists (showing the first 5 here). `IN` builds the
set of Rock artist-ids once and tests membership; `EXISTS` runs its little
correlated query per artist and stops as soon as it finds one Rock track.
On this data they agree; we'll see in Pitfall 3 that the two *diverge*
when a `NULL` is involved.
### Example 3 — the derived table: a query in the `FROM` clause
Lesson 06, Pitfall 5, told you that in `A UNION B ORDER BY … LIMIT n` the
`ORDER BY`/`LIMIT` bind to the *whole* compound, not to the last branch —
so you can't write "top 3 artists, `UNION`, bottom 3 artists" directly.
The fix is a **derived table**: run each branch's `LIMIT` *inside* its own
subquery, then `UNION` the two already-limited results:
```sql
SELECT name, revenue, tag FROM (SELECT ar.name, ar.revenue, 'top' AS tag FROM (SELECT a.Name AS name, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue FROM Artist a JOIN Album al ON a.ArtistId = al.ArtistId JOIN Track t ON al.AlbumId = t.AlbumId JOIN InvoiceLine il ON t.TrackId = il.TrackId GROUP BY a.Name ORDER BY revenue DESC, name LIMIT 3) ar UNION SELECT ar.name, ar.revenue, 'bottom' FROM (SELECT a.Name AS name, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue FROM Artist a JOIN Album al ON a.ArtistId = al.ArtistId JOIN Track t ON al.AlbumId = t.AlbumId JOIN InvoiceLine il ON t.TrackId = il.TrackId GROUP BY a.Name ORDER BY revenue ASC, name LIMIT 3) ar) ORDER BY tag, revenue DESC;
```

```
name                                                                                   revenue  tag
-------------------------------------------------------------------------------------  -------  ------
Academy of St. Martin in the Fields & Sir Neville Marriner                             0.99     bottom
Academy of St. Martin in the Fields, John Birch, Sir Neville Marriner & Sylvia McNair  0.99     bottom
Adrian Leaper & Doreen de Feis                                                         0.99     bottom
Iron Maiden                                                                            138.6    top
U2                                                                                     105.93   top
Metallica                                                                              90.09    top
```

Each parenthesized subquery in the `FROM` clause does its own `ORDER BY …
LIMIT 3` (top and bottom), and the outer `UNION` just glues the two
three-row results together. The `tag` column tells you which branch a row
came from. This is the standard workaround for "I want `LIMIT` to apply
per-branch" in SQLite.
Why not just wrap each branch in parentheses, like
`… LIMIT 3) UNION (… LIMIT 3`? Because SQLite 3.31 won't parse a *bare*
(parenthesized `SELECT`) as a branch of a compound query at all:
```sql
SELECT 1 AS a UNION (SELECT 2);
```

```
Error: near "(": syntax error
```

You need the subquery to live in a `FROM` clause (a derived table) or
`WITH` (a CTE) — a *table* you can select from — not a naked parenthesized
statement. That's the rule Lesson 06 stated and this example makes concrete.
### Example 4 — `WITH`: the per-artist revenue, named
Lesson 05's fan-out-safe per-artist revenue query is a long chain of joins.
When you need that result more than once in a report, repeating the whole
chain is ugly. A `WITH` names it:
```sql
WITH artist_revenue AS (SELECT a.ArtistId, a.Name, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS revenue FROM Artist a JOIN Album al ON a.ArtistId = al.ArtistId JOIN Track t ON al.AlbumId = t.AlbumId JOIN InvoiceLine il ON t.TrackId = il.TrackId GROUP BY a.ArtistId, a.Name) SELECT Name, revenue FROM artist_revenue ORDER BY revenue DESC LIMIT 5;
```

```
Name          revenue
------------  -------
Iron Maiden   138.6
U2            105.93
Metallica     90.09
Led Zeppelin  86.13
Lost          81.59
```

`WITH artist_revenue AS (…)` defines the same many-to-one chain from Lesson
05 (so no `SUM` gets fanned out), and the outer `SELECT` reads it by name
and orders it. Top five: **Iron Maiden $138.60, U2 $105.93, Metallica
$90.09, Led Zeppelin $86.13, Lost $81.59** — the exact figures Lesson 05
printed, now computed through a named CTE instead of one big inline query.
### Example 5 — `WITH RECURSIVE`: walk the org chart to any depth
The `Employee` table is self-referential (`ReportsTo` points at another
employee). Lesson 05/06 showed a *hard-coded* two-level join to reach
grand-managers. A recursive CTE walks the chain to *whatever* the depth
turns out to be:
```sql
WITH RECURSIVE org(id, name, depth) AS (SELECT EmployeeId, FirstName || ' ' || LastName, 0 FROM Employee WHERE ReportsTo IS NULL UNION ALL SELECT e.EmployeeId, e.FirstName || ' ' || e.LastName, org.depth + 1 FROM Employee e JOIN org ON e.ReportsTo = org.id) SELECT depth, id, name FROM org ORDER BY depth, id;
```

```
depth  id  name
-----  --  ----------------
0      1   Andrew Adams
1      2   Nancy Edwards
1      6   Michael Mitchell
2      3   Jane Peacock
2      4   Margaret Park
2      5   Steve Johnson
2      7   Robert King
2      8   Laura Callahan
```

The **anchor** (the non-recursive part) seeds the CEO — the one employee
with `ReportsTo IS NULL`. The **recursive part** keeps joining each known
manager to their reports, adding one depth level each pass, until there are
no more reports to add. Chinook's chart is only **two** levels deep, so the
walk stops at depth 2: 8 employees total (1 at depth 0, 2 at depth 1, 5 at
depth 2).
Contrast that with the hard-coded version, which can *only* reach exactly
two levels because it's written that way:
```sql
SELECT e.EmployeeId, e.FirstName, m.FirstName AS manager, gm.FirstName AS grand_manager FROM Employee e LEFT JOIN Employee m ON e.ReportsTo = m.EmployeeId LEFT JOIN Employee gm ON m.ReportsTo = gm.EmployeeId ORDER BY e.EmployeeId;
```

```
EmployeeId  FirstName  manager  grand_manager
----------  ---------  -------  -------------
1           Andrew
2           Nancy      Andrew
3           Jane       Nancy    Andrew
4           Margaret   Nancy    Andrew
5           Steve      Nancy    Andrew
6           Michael    Andrew
7           Robert     Michael  Andrew
8           Laura      Michael  Andrew
```

Same eight employees, but if Chinook had a third level of staff this
version would never see them — it has exactly two joins, so it stops at
two. The recursive version would have kept going. That's the whole point:
**use recursion when the depth is unknown or varies; use a fixed chain of
joins when you know the exact depth.**
**Check for yourself — drop the anchor's filter.** The anchor above has
`WHERE ReportsTo IS NULL` so that *only* the CEO seeds the walk. Remove that
filter and *every* employee becomes a root:
```sql
WITH RECURSIVE org(id, name, depth) AS (SELECT EmployeeId, FirstName, 0 FROM Employee UNION ALL SELECT e.EmployeeId, e.FirstName, org.depth + 1 FROM Employee e JOIN org ON e.ReportsTo = org.id) SELECT COUNT(*) AS rows, MAX(depth) AS max_depth FROM org;
```

```
rows  max_depth
----  ---------
20    2
```

20 rows instead of 8, and the `MAX(depth)` is still 2. The anchor seeded all
8 employees at depth 0, and the recursion then re-added the ones that have
a manager on top of that. A missing anchor filter is a quiet row-inflation
bug — you get *plausible-looking* output, just with the wrong root set.

---
## 3. Your turn
Do these in Jasper SQL Playground against `data/chinook.db`. This lesson only
reads, so no reset is needed. Answers in `answers.md`.
1. **Scalar in the `SELECT` list.** Add a column showing the store's grand
   total next to each of the first 5 invoices. (One subquery, no `JOIN`.)
2. **Correlated average.** For each of the 5 customers with the highest
   average invoice, show their `avg_spend` *and* the store-wide `store_avg`
   beside it, so you can see each customer against the baseline.
3. **Per-customer total (join version).** Same goal as #1 but for the whole
   store: each customer's total spend, biggest 5. (A `JOIN` + `GROUP BY`
   instead of a correlated subquery — compare it with #2.)
4. **Artists with no sales.** How many artists have *no* line item anywhere
   in `InvoiceLine`? (`NOT EXISTS`.)
5. **Stretch — rank artists by revenue.** Using a `WITH`, assign each
   artist a `revenue_rank` (1 = highest revenue) by counting how many
   artists earn more, and show the top 5.
---
## 4. Quiz
1. A scalar subquery in the `SELECT` list — what exactly must it return for
   the query to be well-formed?
2. `Employee` has 8 rows. Compare
   `WHERE EmployeeId IN (SELECT EmployeeId FROM Employee ORDER BY EmployeeId LIMIT 2)`
   with `WHERE EmployeeId = (SELECT EmployeeId FROM Employee ORDER BY EmployeeId LIMIT 2)`.
   How many rows does each return, and why do they differ?
3. In SQLite 3.31, what does `WHERE x = (a subquery that returns 2 rows)`
   do? (Contrast with what MySQL/PostgreSQL do.)
4. `Employee.ReportsTo` is `NULL` for exactly one row (the CEO). Compare
   `NOT IN (SELECT ReportsTo FROM Employee)` with
   `NOT EXISTS (SELECT 1 FROM Employee r WHERE r.ReportsTo = e.EmployeeId)`
   for "employees nobody reports to". How many rows does each return, and
   why do they differ?
5. When would you reach for a `WITH` instead of a derived table (or a plain
   inline subquery)?
6. **Stretch.** The recursive org chart in Example 5 returns 8 rows with a
   max depth of 2. How many rows would it return if the anchor matched
   *zero* employees (say `WHERE EmployeeId = 999`)? And if the data had a
   *cycle* (an employee who reports, directly or indirectly, back to
   themselves), what would the query do — and how do you keep it safe?
---
## 5. Pitfalls
1. **A multi-row "scalar" silently returns the first row.** In SQLite 3.31
   a subquery used where a *single value* is expected — in the `SELECT`
   list or a `WHERE x = (…)` — does **not** error even when it returns
   several rows. It quietly returns the *first* one:
```sql
SELECT (SELECT EmployeeId FROM Employee ORDER BY EmployeeId LIMIT 2) AS got;
```

```
got

---
1
```

The subquery returns two ids (`1` and `2`), but the outer query got `1` —
the first row — with no error and no warning. The same thing happens in
the `WHERE` slot:
```sql
SELECT EmployeeId, FirstName FROM Employee WHERE EmployeeId = (SELECT EmployeeId FROM Employee ORDER BY EmployeeId LIMIT 2);
```

```
EmployeeId  FirstName
----------  ---------
1           Andrew
```

One row (employee 1), not two. (MySQL and PostgreSQL would stop with a
*"subquery returns more than one row"* error; SQLite 3.31 won't.) If a
subquery is *supposed* to be a single value, guard it: wrap it in `LIMIT 1`
deliberately, or check `COUNT(*) = 1` first.
2. **Forgetting to correlate gives a constant, not an error.** The
non-correlated subquery in Example 1's first table printed $2,328.60 on
*every* row — exactly the store total — because it never referenced the
outer row. It ran fine, looked plausible, and was simply the wrong number
for "this customer's total." Add the correlation
(`WHERE i2.CustomerId = c.CustomerId`) and it starts varying (Pitfall: see
Example 1's second table). The bug is invisible unless you know the value
*should* differ row to row.
3. **`NOT IN (subquery)` with a `NULL` returns 0 rows.** `ReportsTo` is
`NULL` for the CEO, so the subquery `(SELECT ReportsTo FROM Employee)`
contains a `NULL`. `NOT IN` then returns *nothing* — the `NULL` makes the
whole membership test unknowable:
```sql
SELECT e.EmployeeId, e.FirstName || ' ' || e.LastName AS name FROM Employee e WHERE e.EmployeeId NOT IN (SELECT ReportsTo FROM Employee);
```

```


```

Zero rows. The correct "nobody reports to this employee" test is
`NOT EXISTS`, which ignores the `NULL` problem entirely:
```sql
SELECT e.EmployeeId, e.FirstName || ' ' || e.LastName AS name FROM Employee e WHERE NOT EXISTS (SELECT 1 FROM Employee r WHERE r.ReportsTo = e.EmployeeId);
```

```
EmployeeId  name
----------  --------------
3           Jane Peacock
4           Margaret Park
5           Steve Johnson
7           Robert King
8           Laura Callahan
```

Five rows (Jane, Margaret, Steve, Robert, Laura — the employees with no
reports). Rule of thumb: **use `NOT EXISTS` for "not in this set"**, never
`NOT IN (a subquery that might contain a `NULL`)`.
4. **`ORDER BY`/`LIMIT` can't sit inside a `UNION` branch (3.31).** You
can't write `… LIMIT 3) UNION (… LIMIT 3` (bare parenthesized branches are
a syntax error — Example 3), and you can't put an `ORDER BY`/`LIMIT` on an
individual branch at all:
```sql
SELECT a FROM (SELECT 1 AS a) ORDER BY a LIMIT 1 UNION SELECT a FROM (SELECT 2 AS a) ORDER BY a LIMIT 1;
```

```
Error: ORDER BY clause should come after UNION not before
```

In SQLite 3.31 an `ORDER BY`/`LIMIT` belongs to the *whole* compound query,
never to one branch. To limit each branch separately, run the limit
*inside* a derived table (Example 3): `(SELECT … LIMIT 3) UNION
(SELECT … LIMIT 3)` each wrapped as a `FROM` table. This is the same rule
Lesson 06, Pitfall 5 stated — here it's what forces you into the derived
table.
5. **A missing anchor filter (or a cycle) wrecks a recursive CTE.** Drop the
anchor's `WHERE` and every row seeds the walk (Example 5's check-for-
yourself: 20 rows instead of 8). Worse, on a graph with a **cycle** an
employee who reports — directly or indirectly — back to themselves never
runs out of new rows, so the recursion **never terminates** and the query
runs until you kill it. The two defenses: keep the anchor's filter, and
add a depth cap such as `WHERE org.depth < 10` in the recursive part so a
bad graph stops instead of spinning.
6. **A non-matching anchor silently returns 0 rows.** If the anchor
matches nothing, there's nothing to seed, so the recursion produces an
empty result with no error:
```sql
WITH RECURSIVE org(id, name, depth) AS (SELECT EmployeeId, FirstName, 0 FROM Employee WHERE EmployeeId = 999 UNION ALL SELECT e.EmployeeId, e.FirstName, org.depth + 1 FROM Employee e JOIN org ON e.ReportsTo = org.id) SELECT COUNT(*) FROM org;
```

```
COUNT(*)
--------
0
```

`0` — the `WHERE EmployeeId = 999` anchor matched no employee, so the walk
never started. A recursive query that "works" but returns nothing almost
always means the anchor is wrong. Verify the anchor by itself first:
`SELECT … FROM Employee WHERE <your anchor>`.---
## 6. Recap
- **A subquery is a `SELECT` used inside another `SELECT`**, in one of three
  slots: the `SELECT` list (a scalar value), the `WHERE` clause (`IN` / `EXISTS`),
  or the `FROM` clause (a **derived table**).
- **Correlated** vs **non-correlated**: the inner query refers to a column of
  the current outer row (re-run per row) or not (run once). Forgetting the
  correlation is a silent *wrong-number* bug, not an error.
- **`IN`** = "is this value in that set?" · **`EXISTS`** = "does a matching row
  exist?" — usually the same result, but `NOT IN` returns 0 rows when the set
  contains a `NULL`; use `NOT EXISTS` for "not in this set."
- **`WITH`** names a subquery (a *common table expression*) so you can reuse it
  by name; **`WITH RECURSIVE** lets it read itself to walk a relationship to any
  depth. Guard it: a filter on the anchor, and a depth cap against cycles.
- **SQLite 3.31 specifics:** a multi-row "scalar" silently returns the first
  row (no error); `ORDER BY`/`LIMIT` bind to the *whole* compound, never a branch
  — so per-branch limits go inside derived tables.
Next up, **Lesson 08: Expressions & functions** — leaving row-level SQL and
starting to *shape* each value: `CASE`, string and date functions, and
`CAST`/`COALESCE`.
