import importlib.util
import re
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("audit_legacy_lessons.py")


def load_module():
    spec = importlib.util.spec_from_file_location("audit_legacy_lessons", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LegacyAuditTests(unittest.TestCase):
    def test_split_sql_keeps_inline_comment_with_following_statement(self):
        audit = load_module()
        sql = "SELECT 1; -- explain the first result\nSELECT 2;"
        self.assertEqual(
            audit.split_sql(sql),
            ["SELECT 1;", "-- explain the first result\nSELECT 2;"],
        )

    def test_missing_output_does_not_consume_the_next_sql_block(self):
        audit = load_module()
        markdown = "```sql\nSELECT 1;\n```\n\n```sql\nSELECT 2;\n```\n"
        self.assertIsNone(audit.next_plain_fence(markdown, 4))

    def test_ellipsis_output_matches_a_prefix_of_a_long_result(self):
        audit = load_module()
        self.assertTrue(
            audit.tables_match(
                (["Name"], [["AC/DC"], ["Accept"], ["..."]]),
                (["Name"], [["AC/DC"], ["Accept"], ["Aerosmith"]]),
            )
        )

    def test_clause_fragment_is_not_a_runnable_sql_statement(self):
        audit = load_module()
        self.assertFalse(audit.is_runnable_sql("A OR B AND C -- grammar example"))

    def test_sampled_rows_match_a_prefix_without_an_ellipsis_marker(self):
        audit = load_module()
        self.assertTrue(audit.tables_match((['Name'], [['AC/DC']]), (['Name'], [['AC/DC'], ['Accept']])))

    def test_session_reset_marker_is_detected(self):
        audit = load_module()
        self.assertTrue(audit.needs_fresh_database("## 2. WORKED EXAMPLES"))

    def test_session_reset_marker_accepts_title_case_heading(self):
        audit = load_module()
        self.assertTrue(audit.needs_fresh_database("## 2. Worked examples"))

    def test_lessons_01_to_03_use_detailed_readme_labels(self):
        root = Path(__file__).resolve().parent.parent
        labels = (
            "**Promise:**",
            "**You need from before:**",
            "**Keywords this lesson:**",
            "**Files in this folder:**",
        )
        for number in ("01", "02", "03"):
            readme = (root / f"lesson-{number}" / "README.md").read_text(encoding="utf-8")
            for label in labels:
                self.assertIn(label, readme)

    def test_lessons_01_to_03_use_title_case_major_sections(self):
        root = Path(__file__).resolve().parent.parent
        headings = (
            "## 1. The concept",
            "## 2. Worked examples",
            "## 3. Your turn",
            "## 4. Quiz",
            "## 5. Pitfalls",
            "## 6. Recap",
            "## 7. Look ahead",
        )
        for number in ("01", "02", "03"):
            lesson = (root / f"lesson-{number}" / "lesson.md").read_text(encoding="utf-8")
            for heading in headings:
                self.assertIn(heading, lesson)

    def test_lesson_one_ordering_examples_are_independent(self):
        root = Path(__file__).resolve().parent.parent
        lesson = (root / "lesson-01" / "lesson.md").read_text(encoding="utf-8")
        self.assertIn("```sql\nSELECT Name\nFROM   Artist\nORDER  BY Name;", lesson)
        self.assertIn("```sql\nSELECT Name\nFROM   Artist\nORDER  BY Name DESC;", lesson)
        self.assertNotIn(
            "ORDER  BY Name;            -- default: A → Z (ASC = ascending)\n"
            "ORDER  BY Name DESC;",
            lesson,
        )

    def test_lessons_05_and_06_use_detailed_readme_labels(self):
        root = Path(__file__).resolve().parent.parent
        labels = (
            "**Promise:**",
            "**You need from before:**",
            "**Keywords this lesson:**",
            "**Files in this folder:**",
        )
        for number in ("05", "06"):
            readme = (root / f"lesson-{number}" / "README.md").read_text(encoding="utf-8")
            for label in labels:
                self.assertIn(label, readme)

    def test_lessons_01_to_06_have_seven_major_sections(self):
        root = Path(__file__).resolve().parent.parent
        for number in ("01", "02", "03", "04", "05", "06"):
            lesson = (root / f"lesson-{number}" / "lesson.md").read_text(encoding="utf-8")
            self.assertIn("## 7. Look ahead", lesson)

    def test_lesson_10_has_the_standard_student_structure(self):
        root = Path(__file__).resolve().parent.parent
        readme_path = root / "lesson-10" / "README.md"
        lesson_path = root / "lesson-10" / "lesson.md"
        answers_path = root / "lesson-10" / "answers.md"
        for path in (readme_path, lesson_path, answers_path):
            self.assertTrue(path.is_file(), f"missing {path}")
        readme = readme_path.read_text(encoding="utf-8")
        for label in ("**Promise:**", "**You need from before:**", "**Keywords this lesson:**", "**Files in this folder:**", "**Before you start**"):
            self.assertIn(label, readme)
        lesson = lesson_path.read_text(encoding="utf-8")
        for heading in (
            "## 1. The concept",
            "## 2. Worked examples",
            "## 3. Your turn",
            "## 4. Quiz",
            "## 5. Pitfalls",
            "## 6. Recap",
            "## 7. Look ahead",
        ):
            self.assertIn(heading, lesson)

    def test_northwind_final_has_fifty_questions_and_learning_support(self):
        root = Path(__file__).resolve().parent.parent
        final = root / "final-test"
        for name in ("README.md", "exam.md", "answers.md", "guided-solutions.md"):
            self.assertTrue((final / name).is_file(), f"missing {final / name}")
        exam = (final / "exam.md").read_text(encoding="utf-8")
        numbers = re.findall(r"(?m)^(\d+)\. ", exam)
        self.assertEqual([str(number) for number in range(1, 51)], numbers)


if __name__ == "__main__":
    unittest.main()
