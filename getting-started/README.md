# Getting Started

Everything in this course runs on **SQLite** with the browser-based [Jasper SQL
Playground](https://jasperbernaers.com/sql-playground/), using the bundled
`chinook.db` sample database. No software, server, or configuration is needed.

## What you need

| Component | Version | Where it comes from |
|-----------|---------|---------------------|
| Browser   | current Chrome, Edge, Firefox, or Safari | Jasper SQL Playground |
| SQLite    | modern SQLite | provided by the playground |

Works on Windows, macOS, and Linux.

## Step 1 — Get the database

The database file is in this repo, at `data/chinook.db` (~1 MB).
After cloning, you're done — nothing else to download.

Chinook is a digital music store: 11 tables covering artists, albums, tracks,
genres, customers, employees, invoices, and playlists — about 7,000 rows in
total. Small enough to read all of it, real enough to practice on.

## Step 2 — Open the database

Open [Jasper SQL Playground](https://jasperbernaers.com/sql-playground/), then
drag `data/chinook.db` from this repository into the page. The file is read
locally by the browser. The playground's schema panel shows the tables and
columns available to query.

Type SQL in the editor and use **Run**. You can keep multiple query tabs open
to compare queries and results.

Format queries across several lines as shown in the lessons:

```sql
SELECT
    Name,
    Composer,
    UnitPrice
FROM Track
WHERE UnitPrice > 0.99;
```

## Step 3 — Warm-up

Try these in your first session:

```sql
SELECT Name FROM Artist;
```

That query lists all 275 artists — you've just run your first SQL query.

## House rules for the course

- **Run everything yourself.** Every query in a lesson is copy-paste-runnable
  against `data/chinook.db`. If your output differs from the book, stop and
  figure out why before moving on.
- **Quizzes are self-graded.** Each lesson has separate practical and quiz
  answer keys. Attempt the exercise or quiz before opening its answer file.
- **Don't modify the original file.** Jasper works on an in-memory copy, so
  your repository database remains unchanged. For a lesson that writes data,
  upload the original file again when you need a clean starting point:

  Jasper lets you download a modified database, but do not overwrite the
  repository copy.

## Troubleshooting
- **The wrong data appears** — reload the original `.db` file and confirm the
  playground's schema panel shows the expected database.
