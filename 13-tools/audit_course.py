#!/usr/bin/env python3
"""Audit every SQL lesson and final-assessment answer document."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

@dataclass(frozen=True)
class Document:
    relative_path: str
    database: str


def extract_sql_blocks(markdown):
    """Return ``(start_line, sql, next_line)`` for each fenced SQL block."""
    blocks = []
    in_sql = False
    start = 0
    body = []
    for number, line in enumerate(markdown.splitlines(), 1):
        stripped = line.strip()
        if not in_sql and stripped == "```sql":
            in_sql, start, body = True, number, []
        elif in_sql and stripped == "```":
            blocks.append((start, "\n".join(body), number + 1))
            in_sql = False
        elif in_sql:
            body.append(line)
    return blocks


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


def accidental_setext_heading_lines(markdown):
    """Return rule-line numbers that would promote preceding prose to a heading."""
    lines = markdown.splitlines()
    return [
        number + 1
        for number in range(1, len(lines))
        if lines[number] in {"---", "==="}
        and lines[number - 1].strip()
        and not lines[number - 1].startswith((" ", "\t"))
    ]


@dataclass
class DocumentResult:
    relative_path: str
    executed: int = 0
    skipped: int = 0
    expected_errors: int = 0
    failures: list = None

    def __post_init__(self):
        if self.failures is None:
            self.failures = []


TEMPLATE_BLOCKS = {
    ("01-lesson-01/lesson.md", 1),
    ("02-lesson-02/lesson.md", 3),
    ("02-lesson-02/lesson.md", 4),
    ("03-lesson-03/lesson.md", 7),
    ("06-lesson-06/answers_quiz.md", 1),
}

EXPECTED_ERROR_BLOCKS = {
    ("01-lesson-01/lesson.md", 18),
    ("03-lesson-03/lesson.md", 19),
    ("07-lesson-07/lesson.md", 9),
    ("07-lesson-07/lesson.md", 18),
    ("09-lesson-09/lesson.md", 8),
    ("09-lesson-09/lesson.md", 9),
    ("09-lesson-09/lesson.md", 10),
    ("09-lesson-09/lesson.md", 13),
    ("09-lesson-09/lesson.md", 19),
    ("09-lesson-09/lesson.md", 20),
    ("09-lesson-09/lesson.md", 21),
    ("09-lesson-09/lesson.md", 25),
}


def course_documents(root: Path):
    documents = []
    for number in range(1, 11):
        folder = f"{number:02d}-lesson-{number:02d}"
        documents.extend((Document(f"{folder}/lesson.md", "chinook"),
                          Document(f"{folder}/answers_practical.md", "chinook"),
                          Document(f"{folder}/answers_quiz.md", "chinook")))
    documents.extend((
        Document("11-final-test/answers.md", "northwind"),
        Document("11-final-test/guided-solutions.md", "northwind"),
    ))
    return documents


def block_mode(relative_path: str, block_number: int):
    key = (relative_path, block_number)
    if key in TEMPLATE_BLOCKS:
        return "template"
    if key in EXPECTED_ERROR_BLOCKS:
        return "expected_error"
    return "run"


def audit_document(root: Path, document: Document):
    database = root / "12-data" / f"{document.database}.db"
    markdown_path = root / document.relative_path
    result = DocumentResult(document.relative_path)
    with tempfile.TemporaryDirectory(prefix="sql-course-audit-") as directory:
        scratch = Path(directory) / "course.db"
        shutil.copyfile(database, scratch)
        connection = sqlite3.connect(scratch, isolation_level=None)
        try:
            blocks = extract_sql_blocks(markdown_path.read_text(encoding="utf-8"))
            for block_number, (_, sql, _) in enumerate(blocks, 1):
                mode = block_mode(document.relative_path, block_number)
                if mode == "template":
                    result.skipped += 1
                    continue
                try:
                    for statement in split_sql(sql):
                        connection.execute(statement).fetchall()
                except sqlite3.Error as error:
                    if mode == "expected_error":
                        result.expected_errors += 1
                    else:
                        result.failures.append(f"block {block_number}: {error}")
                else:
                    if mode == "expected_error":
                        result.failures.append(f"block {block_number}: expected SQLite error")
                    else:
                        result.executed += 1
        finally:
            connection.close()
    return result


def validate_final_exam(root: Path):
    final = root / "11-final-test"
    missing = [name for name in ("README.md", "exam.md", "answers.md", "guided-solutions.md")
               if not (final / name).is_file()]
    if missing:
        return [f"missing final-test file: {name}" for name in missing]
    numbers = re.findall(r"(?m)^(\d+)\. ", (final / "exam.md").read_text(encoding="utf-8"))
    expected = [str(number) for number in range(1, 51)]
    if numbers != expected:
        return ["final-test exam must contain questions 1 through 50"]
    return []


def resolve_litecli():
    litecli = shutil.which("litecli")
    if litecli is None:
        raise RuntimeError("LiteCLI requested but not found on PATH")
    return litecli


def audit_litecli_document(root: Path, document: Document, litecli_path: str):
    database = root / "12-data" / f"{document.database}.db"
    markdown_path = root / document.relative_path
    blocks = extract_sql_blocks(markdown_path.read_text(encoding="utf-8"))
    script = "\n\n".join(
        sql for block_number, (_, sql, _) in enumerate(blocks, 1)
        if block_mode(document.relative_path, block_number) == "run"
    )
    with tempfile.TemporaryDirectory(prefix="sql-course-litecli-") as directory:
        scratch = Path(directory) / "course.db"
        shutil.copyfile(database, scratch)
        completed = subprocess.run(
            [litecli_path, str(scratch), "--execute", script],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    if completed.returncode:
        return completed.stderr.strip() or "LiteCLI returned a nonzero exit status"
    return None


def audit_course(root: Path, use_litecli=False):
    litecli_path = resolve_litecli() if use_litecli else None
    results = []
    for document in course_documents(root):
        result = audit_document(root, document)
        markdown = (root / document.relative_path).read_text(encoding="utf-8")
        for line in accidental_setext_heading_lines(markdown):
            result.failures.append(f"line {line}: add a blank line before the rule")
        if litecli_path:
            error = audit_litecli_document(root, document, litecli_path)
            if error:
                result.failures.append(f"LiteCLI: {error}")
        results.append(result)
    final_exam_errors = validate_final_exam(root)
    return results, final_exam_errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--litecli", action="store_true", help="also execute normal blocks through LiteCLI")
    arguments = parser.parse_args()
    try:
        results, final_exam_errors = audit_course(arguments.root.resolve(), arguments.litecli)
    except RuntimeError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    total_executed = total_skipped = total_expected_errors = total_failures = 0
    for result in results:
        total_executed += result.executed
        total_skipped += result.skipped
        total_expected_errors += result.expected_errors
        total_failures += len(result.failures)
        status = "PASS" if not result.failures else "FAIL"
        print(f"{status} {result.relative_path}: {result.executed} executed, "
              f"{result.skipped} template, {result.expected_errors} expected error")
        for failure in result.failures:
            print(f"  {failure}")
    for error in final_exam_errors:
        print(f"FAIL 11-final-test/exam.md: {error}")
    total_failures += len(final_exam_errors)
    print(f"Course total: {total_executed} executed, {total_skipped} template, "
          f"{total_expected_errors} expected error, {total_failures} failure")
    return 1 if total_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
