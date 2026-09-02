# Getting Started

Everything in this course runs on **SQLite** with the browser-based [SQL
Explorer](https://sql-explorer.netlify.app/), using the course's `chinook.db`
sample database. No software, server, or configuration is needed.

## What you need

| Component | Version | Where it comes from |
|-----------|---------|---------------------|
| Browser   | current Chrome, Edge, Firefox, or Safari | SQL Explorer |
| SQLite    | modern SQLite | provided by SQL Explorer |

Works on Windows, macOS, and Linux.

## Step 1 — Select the database

Open [SQL Explorer](https://sql-explorer.netlify.app/) and select `chinook.db`
from the database dropdown. SQL Explorer loads a copy directly from this
course repository through GitHub; cloning the repository or downloading the
database is not necessary.

**Alternative:** You can also use the [SQLite3 Playground](https://sqlite3-playground.netlify.app/)
as an alternative browser-based SQLite workspace.

Chinook is a digital music store: 11 tables covering artists, albums, tracks,
genres, customers, employees, invoices, and playlists — about 7,000 rows in
total. Small enough to read all of it, real enough to practice on.

## Step 2 — Explore the database

The database's schema panel shows the tables and columns available to query.

To view a table's complete contents, expand that table in the schema panel and
select **`> SELECT *`**. SQL Explorer loads the query into the editor; click
**Run** to execute it. You can change the query's `LIMIT` value to show more
or fewer rows.

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

Try this in your first session:

```sql
SELECT Name FROM Artist;
```

That query lists all 275 artists — you've just run your first SQL query.

## House rules for the course

- **Run everything yourself.** Every query in a lesson is copy-paste-runnable
  against `12-data/chinook.db`. If your output differs from the book, stop and
  figure out why before moving on.
- **Quizzes are self-graded.** Each lesson has separate practical and quiz
  answer keys. Attempt the exercise or quiz before opening its answer file.
- **Don't modify the original database.** SQL Explorer works on an in-memory
  copy, so the GitHub database remains unchanged. For a lesson that writes
  data, click **Load** again and select the database to start with a fresh
  copy. There is no need to download or upload a database file.

## Troubleshooting
- **The wrong data appears** — click **Load** again, select the expected
  database, and confirm the schema panel shows the right tables.
