# LiteCLI Multiline Getting-Started Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Document LiteCLI multiline configuration and align getting-started instructions with actual Enter/semicolon behavior.

**Architecture:** Documentation-only change in `getting-started/README.md`; add configuration guidance after connection setup, then reconcile warm-up and troubleshooting text.

**Tech Stack:** Markdown.

---

### Task 1: Update getting-started guidance

**Files:**
- Modify: `getting-started/README.md`

- [ ] **Step 1: Add multiline configuration section**

Insert after Step 3's command table: explain default `multi_line = False`, show editing `~/.config/litecli/config`, changing it to `True`, restarting LiteCLI, and verifying with `grep`.

- [ ] **Step 2: Add multiline query example**

Show a formatted `SELECT` query and continuation prompt. State that Enter adds lines and a terminating semicolon executes.

- [ ] **Step 3: Reconcile existing instructions**

Change warm-up wording and troubleshooting so they distinguish default single-line mode from enabled multiline mode, without claiming a missing semicolon always requires an empty-line Enter.

- [ ] **Step 4: Validate documentation consistency**

Run:

```bash
rg -n "multi_line|incomplete input|semicolon|semicolon|press Enter|Enter" getting-started/README.md
```

Review all matching lines for contradictions and inspect the rendered Markdown structure with `sed`.

- [ ] **Step 5: Commit**

```bash
git add getting-started/README.md
git commit -m "docs: explain litecli multiline mode"
```
