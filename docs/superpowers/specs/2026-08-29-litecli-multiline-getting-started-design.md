# LiteCLI Multiline Getting-Started Guidance Design

## Goal

Prevent `incomplete input` confusion by documenting LiteCLI's default single-line behavior and the `multi_line` configuration option.

## Scope

- Update `getting-started/README.md` only for user-facing guidance.
- Add a multiline SQL subsection after connection instructions.
- Show how to edit and verify `~/.config/litecli/config`.
- Update warm-up and troubleshooting wording so Enter/semicolon behavior is consistent.

## Approach

Use LiteCLI's documented `multi_line = True` setting. Explain that Enter continues input and a terminating semicolon executes the statement. Keep the existing single-line default as an explicit alternative.

## Validation

Review rendered Markdown and search the document for conflicting claims about Enter, semicolons, or multiline input.
