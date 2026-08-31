import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE = Path(__file__).with_name("audit_course.py")


def load_module():
    spec = importlib.util.spec_from_file_location("audit_course", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CourseManifestTests(unittest.TestCase):
    def test_accidental_setext_heading_requires_a_blank_line(self):
        audit = load_module()
        self.assertEqual([2], audit.accidental_setext_heading_lines("Normal prose\n---\n"))
        self.assertEqual([], audit.accidental_setext_heading_lines("Normal prose\n\n---\n"))
        self.assertEqual([], audit.accidental_setext_heading_lines("  list continuation\n---\n"))

    def test_extract_sql_blocks_records_sql_fences(self):
        audit = load_module()
        self.assertEqual([(1, "SELECT 1;", 4)], audit.extract_sql_blocks("```sql\nSELECT 1;\n```"))

    def test_split_sql_preserves_inline_comment_with_next_statement(self):
        audit = load_module()
        self.assertEqual(
            ["SELECT 1;", "-- note\nSELECT 2;"],
            audit.split_sql("SELECT 1; -- note\nSELECT 2;"),
        )

    def test_manifest_has_twenty_lesson_documents_and_two_final_documents(self):
        audit = load_module()
        documents = audit.course_documents(Path("."))
        self.assertEqual(32, len(documents))
        self.assertEqual(30, sum(item.database == "chinook" for item in documents))
        self.assertEqual(2, sum(item.database == "northwind" for item in documents))

    def test_instructional_blocks_are_classified_explicitly(self):
        audit = load_module()
        self.assertEqual("template", audit.block_mode("01-lesson-01/lesson.md", 1))
        self.assertEqual("expected_error", audit.block_mode("09-lesson-09/lesson.md", 8))
        self.assertEqual("run", audit.block_mode("10-lesson-10/answers_quiz.md", 1))


class CourseExecutionTests(unittest.TestCase):
    def test_audit_document_executes_normal_sql(self):
        audit = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "12-data").mkdir()
            shutil.copyfile(Path("12-data/chinook.db"), root / "12-data/chinook.db")
            (root / "sample.md").write_text("```sql\nSELECT 1;\n```\n", encoding="utf-8")
            result = audit.audit_document(root, audit.Document("sample.md", "chinook"))
        self.assertEqual(1, result.executed)
        self.assertEqual([], result.failures)

    def test_audit_document_confirms_expected_error(self):
        audit = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "12-data").mkdir()
            shutil.copyfile(Path("12-data/chinook.db"), root / "12-data/chinook.db")
            (root / "09-lesson-09").mkdir()
            (root / "09-lesson-09/lesson.md").write_text(
                "```sql\nSELECT 1;\n```\n" * 7
                + "```sql\nCREATE TABLE Review (Code TEXT UNIQUE);\n"
                "INSERT INTO Review VALUES ('A');\nINSERT INTO Review VALUES ('A');\n```\n",
                encoding="utf-8",
            )
            result = audit.audit_document(root, audit.Document("09-lesson-09/lesson.md", "chinook"))
        self.assertEqual(1, result.expected_errors)
        self.assertEqual([], result.failures)

    def test_final_exam_has_fifty_numbered_questions(self):
        audit = load_module()
        self.assertEqual([], audit.validate_final_exam(Path(".")))


class CourseLiteCliTests(unittest.TestCase):
    def test_missing_litecli_is_an_error(self):
        audit = load_module()
        with patch.object(audit.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "LiteCLI requested but not found on PATH"):
                audit.resolve_litecli()


if __name__ == "__main__":
    unittest.main()
