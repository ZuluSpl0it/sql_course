# Getting Started

Everything in this course runs on **SQLite** with the **litecli** command-line
client, using the bundled `chinook.db` sample database. One terminal, one
file, no server to install or run.

## What you need

| Component | Version | Where it comes from |
|-----------|---------|---------------------|
| litecli   | ≥ 1.17  | `pip install litecli` |
| SQLite    | ≥ 3.31  | included with litecli; a system `sqlite3` is optional |
| Python    | ≥ 3.9   | litecli is a Python program |

Works on Windows, macOS, and Linux.

## Step 1 — Install litecli

Pick whichever you already use:

```bash
# plain pip (simplest)
pip install litecli

# or, if you prefer isolated CLI tools:
pipx install litecli
```

Verify:

```bash
litecli --version
```

You should see a version number ≥ 1.17.

## Step 2 — Get the database

The database file is in this repo, at `data/chinook.db` (~1 MB).
After cloning, you're done — nothing else to download.

Chinook is a digital music store: 11 tables covering artists, albums, tracks,
genres, customers, employees, invoices, and playlists — about 7,000 rows in
total. Small enough to read all of it, real enough to practice on.

## Step 3 — Connect

From the repo root, open a terminal and run:

```bash
litecli data/chinook.db
```

You'll see a `litecli` prompt. You're now connected. A few commands you'll use
in every lesson:

| Command | What it does |
|---------|-------------|
| `.tables` | list all tables |
| `.schema <table>` | show a table's column definitions |
| `.quit` | exit (or just type `quit`) |

Everything else you type is SQL — end it with `;` and press Enter to run.
litecli autocompletes table and column names with **Tab** — use it.

### Multiline SQL (recommended)

LiteCLI starts in single-line mode (`multi_line = False`), where pressing
Enter immediately executes the current line. A partial statement such as
`SELECT` therefore reports `incomplete input`. Enable multiline mode once so
you can format queries across several lines:

```bash
nano ~/.config/litecli/config
```

In the `[main]` section, change:

```ini
multi_line = False
```

to:

```ini
multi_line = True
```

Exit LiteCLI and start it again. Verify the setting without opening the editor:

```bash
grep multi_line ~/.config/litecli/config
```

With multiline mode enabled, Enter adds a line and the terminating semicolon
executes the statement:

```sql
SELECT
    Name,
    Composer,
    UnitPrice
FROM Track
WHERE UnitPrice > 0.99;
```

The continuation prompt looks like this:

```text
./data/chinook.db> SELECT
              ->     Name,
              ->     Composer,
              ->     UnitPrice
              -> FROM Track
              -> WHERE UnitPrice > 0.99;
```

## Step 4 — Warm-up

Try these in your first session. In the default single-line mode, type each
complete query, including `;`, before pressing Enter. In multiline mode, press
Enter after each line and use `;` on the final line:

```sql
.tables

SELECT Name FROM Artist;
```

That second one lists all 275 artists — you've just run your first SQL query.

## House rules for the course

- **Run everything yourself.** Every query in a lesson is copy-paste-runnable
  against `data/chinook.db`. If your output differs from the book, stop and
  figure out why before moving on.
- **Quizzes are self-graded.** Each lesson's quiz has an answer key in a
  separate file (`answers.md`). Attempt the quiz before opening it.
- **Don't modify `data/chinook.db`.** Some lessons (from Lesson 03 onward) do
  write to the database. Copy it first:

```bash
cp data/chinook.db data/chinook-scratch.db
litecli data/chinook-scratch.db
```

Work against `chinook-scratch.db` for anything that inserts, updates, or
deletes. (On Windows use `copy data\chinook.db data\chinook-scratch.db`.)

## Troubleshooting

- **`litecli: command not found`** — pip put it somewhere not on your PATH.
  On Windows: `python -m litecli data/chinook.db` works from anywhere.
- **Your terminal shows `???` for some names** — Chinook has some non-ASCII
  artist names (e.g. Antônio Carlos Jobim). Set your terminal's encoding to
  UTF-8 (on Windows: `chcp 65001`).
- **`incomplete input` after pressing Enter** — LiteCLI is in single-line mode.
  Enable `multi_line = True` as described above, or enter the complete
  statement, including its semicolon, before pressing Enter. Press Ctrl+C to
  cancel an unfinished input.
