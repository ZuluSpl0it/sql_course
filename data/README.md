# Course databases

This folder contains the two SQLite database files used by the course.

## `chinook.db`

`chinook.db` is the main course database. Lessons 01–10 use it. It models a
digital music store with artists, albums, tracks, customers, invoices, and
employees.

Treat this file as **pristine**. Lessons that only read data can connect to it
directly. Before Lessons 03, 09, or 10—where you write data or change schema—
create a scratch copy from the repository root:

```bash
cp data/chinook.db data/chinook-scratch.db
litecli data/chinook-scratch.db
```

When you want to start over, delete the scratch copy and create it again from
`chinook.db`. `chinook-scratch.db` is intentionally ignored by Git.

## `northwind.db`

`northwind.db` is used only by the [final test](../final-test/README.md). It
models a different business, so the assessment checks whether you can transfer
the SQL skills from Chinook to unfamiliar tables and relationships.

The final test is read-only. Do not modify `northwind.db`.

## SQLite tools

Both files are standard SQLite 3 databases. You can inspect either one with
LiteCLI:

```bash
litecli data/chinook.db
litecli data/northwind.db
```

Use `.tables` to list tables and `.schema TableName` to inspect a table's
columns.
