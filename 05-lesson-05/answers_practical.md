# Lesson 05 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

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
