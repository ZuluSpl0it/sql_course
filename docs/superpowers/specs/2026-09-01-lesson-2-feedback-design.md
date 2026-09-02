# Lesson 2 Feedback Design

## Goal

Improve Lesson 2 instructions and answer-key alignment based on learner
feedback, without changing the lesson's filtering scope.

## Changes

1. Explain when `ORDER BY` is required: only prompts that request ordering,
   alphabetical order, or a first/last subset require it. Reference answers
   may still include deterministic ordering for readable output.
2. Clarify Practical 3's `IS NOT NULL` note using the Canadian customer count,
   the two qualifying rows, and François Tremblay's excluded NULL company.
3. Rewrite Practical 4 so the listed countries are filter criteria and the
   selected output is useful rather than repeating the filter value.
4. Keep Pitfall 3 focused on `NOT IN` and `NOT EXISTS`; defer `LEFT JOIN` until
   joins are taught.
5. Spell out precedence in Recap item 3 instead of using `>` between words.
6. Revise Final Test Q7, interpreted as the question numbered 7 in the final
   test, so it exercises a different filtering task from Lesson 2 examples.

## Verification

Run the course audit tests and verify the revised SQL answer output against the
Chinook database where applicable.
