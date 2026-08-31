# Lesson 03 — Practical Answer Key

Attempt the practical exercises in `lesson.md` before opening this file.

## Practical Exercises (reference)

1. New artist with its id:

```sql
INSERT INTO Artist (Name) VALUES ('Your Band Name Here');
SELECT last_insert_rowid();
```

2. Two genres with explicit ids:

```sql
INSERT INTO Genre (GenreId, Name)
VALUES (26, 'Quiz Genre One'),
       (27, 'Quiz Genre Two');
```

(Ids 26 and 27 are free — the largest existing `GenreId` is 25. Supplying
the `GenreId` yourself is the point: it stops being auto-assigned.)

3. Customer 2's phone, with `changes()`:

```sql
UPDATE Customer SET Phone = '555-0100' WHERE CustomerId = 2;
SELECT changes();
```

```
changes()
---------
1
```

(Customer 2 is Leonie Köhler, original phone `+49 0711 2842222`.)

4. Delete playlist 18 ("On-The-Go 1") and its one track link:

```sql
SELECT COUNT(*) FROM PlaylistTrack WHERE PlaylistId = 18;  -- 1

BEGIN;
DELETE FROM PlaylistTrack WHERE PlaylistId = 18;
DELETE FROM Playlist      WHERE PlaylistId = 18;
COMMIT;

SELECT COUNT(*) FROM Playlist WHERE PlaylistId = 18;       -- 0
```

5. Rename "Rock" inside a transaction, then roll back:

```sql
SELECT Name FROM Genre WHERE GenreId = 1;     -- before:  Rock
BEGIN;
UPDATE Genre SET Name = 'Rock (renamed)' WHERE GenreId = 1;
SELECT Name FROM Genre WHERE GenreId = 1;     -- during:  Rock (renamed)
ROLLBACK;
SELECT Name FROM Genre WHERE GenreId = 1;     -- after:   Rock
```

6. Three notes in `ScratchNote`:

```sql
CREATE TABLE ScratchNote (NoteId INTEGER PRIMARY KEY, Note TEXT);
INSERT INTO ScratchNote (Note)
VALUES ('one'), ('two'), ('three');
SELECT * FROM ScratchNote;
```

```
NoteId  Note
------  -----
1       one
2       two
3       three
```
