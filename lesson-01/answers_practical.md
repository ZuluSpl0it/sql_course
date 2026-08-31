# Lesson 01 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

These were open-ended; if you're checking your work, one good version each:

1. First 10 tracks:

```sql
SELECT Name FROM Track LIMIT 10;
```

2. 5 artists, Z → A:

```sql
SELECT Name FROM Artist ORDER BY Name DESC LIMIT 5;
```

```
Name
-------------------
Zeca Pagodinho
Youssou N'Dour
Yo-Yo Ma
Yehudi Menuhin
Xis
```

Any 5 of the last rows in descending name order are fine, but
`ORDER BY Name DESC` must be present.

3. All media type names:

```sql
SELECT Name FROM MediaType;
-- or, to see everything while exploring:
SELECT * FROM MediaType;
```

5 rows: MPEG audio file, Protected AAC audio file,
Protected MPEG-4 video file, Purchased AAC audio file, AAC audio file.

4. 5 cheapest tracks with the price labeled `price`:

```sql
SELECT Name, UnitPrice AS price
FROM   Track
ORDER  BY UnitPrice, Name
LIMIT  5;
```

(All track prices are 0.99 or 1.99 — the "cheapest" are the 0.99 ones;
the tie-breaker by `Name` makes the answer deterministic.)

5. Artists at position 251–255 alphabetically:

```sql
SELECT Name FROM Artist ORDER BY Name LIMIT 5 OFFSET 250;
```

(275 artists exist, so this returns 5 rows; positions 1–275.)
