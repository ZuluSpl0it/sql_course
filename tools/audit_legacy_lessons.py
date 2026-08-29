#!/usr/bin/env python3
"""Audit legacy SQL-course lessons without changing their source database.

Unlike the newer audit_lesson.py, this tool preserves one SQLite connection for
the whole lesson, accepts inline ``--`` comments, and treats outputless concept
queries as skips rather than failures. It always runs against a temporary copy
of the supplied database.
"""
import argparse
import os
import re
import shutil
import sqlite3
import tempfile


ARROW_RE = re.compile(r"\s*←.*$")
TEMPLATE_RE = re.compile(r"<[^>]+>")
ELLIPSIS_RE = re.compile(r"^\.\.\.$")
SQL_STARTERS = {
    "ALTER", "ANALYZE", "ATTACH", "BEGIN", "COMMIT", "CREATE", "DELETE",
    "DETACH", "DROP", "EXPLAIN", "INSERT", "PRAGMA", "REINDEX", "RELEASE",
    "ROLLBACK", "SAVEPOINT", "SELECT", "UPDATE", "VACUUM", "WITH",
}


def extract_sql_blocks(markdown):
    blocks = []
    lines = markdown.splitlines()
    in_sql = False
    start = 0
    body = []
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_sql and stripped == "```sql":
            in_sql, start, body = True, number, []
        elif in_sql and stripped == "```":
            blocks.append((start, "\n".join(body), number + 1))
            in_sql = False
        elif in_sql:
            body.append(line)
    return blocks


def next_plain_fence(markdown, after_line):
    """Return the next plain fence, stopping at another SQL fence."""
    lines = markdown.splitlines()
    index = after_line - 1
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped == "```sql":
            return None
        if stripped == "```":
            output = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                output.append(lines[index])
                index += 1
            return output
        index += 1
    return None


def split_sql(sql):
    """Split complete SQLite statements while preserving comments and strings."""
    statements = []
    current = []
    for character in sql:
        current.append(character)
        if character == ";" and sqlite3.complete_statement("".join(current)):
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


def is_dash_row(line):
    stripped = line.strip()
    return bool(stripped and "|" not in stripped and re.fullmatch(r"[\s=-]+", stripped) and "-" in stripped)


def spans(dash_row):
    return [(match.start(), match.end()) for match in re.finditer(r"[-=]+", dash_row)]


def cells(line, column_spans):
    return [line[start:end].strip() if start < len(line) else "" for start, end in column_spans]


def parse_tables(lines):
    cleaned = [ARROW_RE.sub("", line) for line in lines]
    tables = []
    index = 0
    while index < len(cleaned):
        if not is_dash_row(cleaned[index]):
            index += 1
            continue
        column_spans = spans(cleaned[index])
        header = cells(cleaned[index - 1], column_spans) if index and cleaned[index - 1].strip() else []
        rows = []
        index += 1
        while index < len(cleaned) and cleaned[index].strip() and not is_dash_row(cleaned[index]):
            rows.append(cells(cleaned[index], column_spans))
            index += 1
        tables.append((header, rows))
    return tables


def tables_match(printed, actual):
    printed_header, printed_rows = printed
    actual_header, actual_rows = actual
    if printed_header != actual_header:
        return False
    if printed_rows and all(ELLIPSIS_RE.fullmatch(cell) for cell in printed_rows[-1]):
        prefix = printed_rows[:-1]
        return actual_rows[:len(prefix)] == prefix
    if len(actual_rows) > len(printed_rows):
        return actual_rows[:len(printed_rows)] == printed_rows
    return printed_rows == actual_rows


def first_keyword(sql):
    for statement in split_sql(sql):
        without_comments = re.sub(r"(?m)^\s*--.*$", "", statement).lstrip()
        match = re.match(r"[A-Za-z]+", without_comments)
        if match:
            return match.group(0).upper()
    return ""


def is_runnable_sql(sql):
    return first_keyword(sql) in SQL_STARTERS


def needs_fresh_database(text):
    normalized = text.casefold()
    return "## 2. worked examples" in normalized or "start fresh from a clean copy" in normalized


def run_block(connection, sql):
    results = []
    for statement in split_sql(sql):
        cursor = connection.execute(statement)
        if cursor.description:
            headers = [column[0] for column in cursor.description]
            rows = [["" if value is None else str(value) for value in row] for row in cursor.fetchall()]
            results.append((headers, rows))
    return results


def audit(lesson_path, database_path):
    markdown = open(lesson_path, encoding="utf-8").read()
    blocks = extract_sql_blocks(markdown)
    markdown_lines = markdown.splitlines()
    passed = failed = skipped = 0
    with tempfile.TemporaryDirectory(prefix="sql-course-audit-") as directory:
        copied_db = os.path.join(directory, "lesson.db")
        shutil.copy2(database_path, copied_db)
        connection = sqlite3.connect(copied_db, isolation_level=None)
        prior_block_end = 0
        try:
            for number, (line, sql, after_line) in enumerate(blocks, 1):
                intervening = "\n".join(markdown_lines[prior_block_end:line - 1])
                prior_block_end = after_line
                if needs_fresh_database(intervening):
                    connection.close()
                    shutil.copy2(database_path, copied_db)
                    connection = sqlite3.connect(copied_db, isolation_level=None)
                    print(f"[RESET] block {number} (line {line}): fresh scratch database")
                if TEMPLATE_RE.search(sql) or re.search(r"(?m)^\s*--\s*\.\.\.", sql):
                    print(f"[SKIP(template)] block {number} (line {line})")
                    skipped += 1
                    continue
                fence = next_plain_fence(markdown, after_line)
                if not is_runnable_sql(sql):
                    print(f"[SKIP(fragment)] block {number} (line {line}): SQL syntax illustration")
                    skipped += 1
                    continue
                if fence is None and first_keyword(sql) == "SELECT":
                    print(f"[SKIP(no-output)] block {number} (line {line}): legacy concept query")
                    skipped += 1
                    continue
                try:
                    actual = run_block(connection, sql)
                except sqlite3.Error as error:
                    message = str(error)
                    shown = "\n".join(fence or [])
                    if message in sql or message in shown:
                        print(f"[PASS(expected-error)] block {number} (line {line}): {message}")
                        passed += 1
                    else:
                        print(f"[FAIL] block {number} (line {line}): unexpected error: {message}")
                        failed += 1
                    continue
                if fence is None:
                    if actual:
                        print(f"[SKIP(no-output)] block {number} (line {line}): {len(actual)} result set(s)")
                        skipped += 1
                    else:
                        print(f"[PASS] block {number} (line {line}): no output")
                        passed += 1
                    continue
                if [entry.strip() for entry in fence if entry.strip()] == ["(no rows)"]:
                    if len(actual) == 1 and actual[0][1] == []:
                        print(f"[PASS] block {number} (line {line}): empty result")
                        passed += 1
                    else:
                        print(f"[FAIL] block {number} (line {line}): expected no rows")
                        failed += 1
                    continue
                printed = parse_tables(fence)
                if not printed and actual:
                    print(f"[SKIP(non-tabular-output)] block {number} (line {line})")
                    skipped += 1
                    continue
                if len(printed) != len(actual):
                    print(f"[FAIL] block {number} (line {line}): {len(printed)} printed table(s) vs {len(actual)} result set(s)")
                    failed += 1
                    continue
                mismatch = next(
                    (f"table {table_number} differs" for table_number, pair in enumerate(zip(printed, actual), 1)
                     if not tables_match(pair[0], pair[1])),
                    None,
                )
                if mismatch:
                    print(f"[FAIL] block {number} (line {line}): {mismatch}; printed={printed!r}; actual={actual!r}")
                    failed += 1
                else:
                    print(f"[PASS] block {number} (line {line}): exact match")
                    passed += 1
        finally:
            connection.close()
    print(f"\n{len(blocks)} sql blocks: {passed} PASS, {failed} FAIL, {skipped} SKIP.")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", help="path to lesson.md")
    parser.add_argument("database", help="pristine SQLite database; never modified")
    arguments = parser.parse_args()
    if not os.path.isfile(arguments.lesson) or not os.path.isfile(arguments.database):
        parser.error("lesson and database must exist")
    raise SystemExit(audit(arguments.lesson, arguments.database))


if __name__ == "__main__":
    main()
