# Course databases

This folder contains the two SQLite database files used by the course.

## `chinook.db`

`chinook.db` is the main course database. Lessons 01–10 use it. It models a
digital music store with artists, albums, tracks, customers, invoices, and
employees.

Treat this file as **pristine**. Jasper SQL Playground reads it into an
in-memory browser copy, so Lessons 03, 09, and 10 can write data or change the
schema without changing this file. Reload the original file whenever you want
to start over.

## `northwind.db`

`northwind.db` is used only by the [final test](../11-final-test/README.md). It
models a different business, so the assessment checks whether you can transfer
the SQL skills from Chinook to unfamiliar tables and relationships.

The final test is read-only. Do not modify `northwind.db`.

## Using the databases

Both files are standard SQLite 3 databases. Open [Jasper SQL
Playground](https://jasperbernaers.com/sql-playground/) and drag either file
into the page:

The playground's schema panel lists tables and columns. All changes happen in
the browser's in-memory copy; the files in this folder are not modified.
