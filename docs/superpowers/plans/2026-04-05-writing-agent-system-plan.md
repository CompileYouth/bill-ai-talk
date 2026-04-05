# Writing Agent System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn this repository from a publish-production workspace into a writing-agent system with explicit state, feedback, repository boundaries, and reusable execution rules.

**Architecture:** Introduce an `article-state/` layer that stores per-article metadata and outcomes, keep `articles/` as the content source of truth, add a concise repository-level `AGENTS.md`, and slim the main writing skill into a workflow shell that delegates detailed guidance to reference files. Update `heyBill` and publisher scripts to read confirmed packaging data from the state layer, then remove repository noise that weakens agent clarity.

**Tech Stack:** Python standard library, Markdown content files, JSON state files, local skill markdown references, Git

---

### Task 1: Add State Layer Skeleton

**Files:**
- Create: `article-state/README.md`
- Create: `article-state/schema.md`
- Create: `article-state/articles/.gitkeep`
- Modify: `scripts/run_heybill.py`
- Test: `tests/test_run_heybill.py`

- [ ] **Step 1: Write the failing test**

```python
def test_cover_selection_persists_to_article_state() -> None:
    file_name = "2026-04/2026-04-05：测试文章.md"
    selection = run_heybill.save_cover_selection(file_name, text="确定词", background="#123456")
    state_path = run_heybill.article_state_path(file_name)
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["packaging"]["cover"]["text"] == "确定词"
    assert state["packaging"]["cover"]["background"] == "#123456"
    assert selection["text"] == "确定词"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_run_heybill.py`
Expected: FAIL because `article_state_path` or `save_cover_selection` state behavior does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
STATE_DIR = ROOT / "article-state" / "articles"

def article_state_path(file_name: str) -> Path:
    stem = file_name.replace("/", "__").removesuffix(".md")
    return STATE_DIR / f"{stem}.json"

def read_article_state(file_name: str) -> dict[str, object]:
    path = article_state_path(file_name)
    if not path.exists():
        return {
            "article_file": file_name,
            "core_judgment": "",
            "tldr": "",
            "packaging": {"cover": {}, "images": []},
            "outcomes": {},
            "review": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_run_heybill.py`
Expected: PASS for state persistence and payload restoration tests.

- [ ] **Step 5: Commit**

```bash
git add article-state/README.md article-state/schema.md article-state/articles/.gitkeep scripts/run_heybill.py tests/test_run_heybill.py
git commit -m "Add article state layer"
```

### Task 2: Document Repository Boundaries

**Files:**
- Create: `AGENTS.md`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Use a manual checklist test:

```text
1. AGENTS.md defines repo goal, source-of-truth boundaries, directory roles, skill precedence, and long-lived state locations.
2. README points readers to AGENTS.md for workspace behavior and to the skill for writing/publishing rules.
3. No detailed writing heuristics are duplicated into AGENTS.md.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `test -f AGENTS.md && rg -n "source of truth|article-state|bill-wechat-daily" AGENTS.md README.md`
Expected: FAIL because `AGENTS.md` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```md
# AGENTS

This workspace exists to run a high-feedback WeChat writing agent.

## Source of truth
- `articles/`: article body source of truth
- `article-state/`: packaging, outcomes, and retrospective state
- `skills/bill-wechat-daily/`: task workflow and writing/publishing rules

## Directory roles
- `assets/`: render outputs tied to articles
- `scripts/`: local preview, packaging, scheduling, publishing helpers
- `.publish/`: runtime caches only; do not treat as long-term memory
```

- [ ] **Step 4: Run test to verify it passes**

Run: `rg -n "article-state|source of truth|bill-wechat-daily" AGENTS.md README.md`
Expected: matches in both files.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md README.md
git commit -m "Add repository guidance entrypoint"
```

### Task 3: Split Skill Into Workflow and References

**Files:**
- Modify: `skills/bill-wechat-daily/SKILL.md`
- Create: `skills/bill-wechat-daily/references/writing-rules.md`
- Create: `skills/bill-wechat-daily/references/publishing-rules.md`
- Modify: `/Users/bytedance/.codex/skills/bill-wechat-daily/SKILL.md`

- [ ] **Step 1: Write the failing test**

Use a manual checklist test:

```text
1. Main skill stays under roughly 160 lines and contains workflow + priorities only.
2. Detailed prose/image/distribution rules move into reference files.
3. Main skill explicitly points to both references.
4. Local live skill and mirrored repo skill stay aligned.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `wc -l skills/bill-wechat-daily/SKILL.md`
Expected: FAIL against the target because the file is currently much longer and includes detailed rules directly.

- [ ] **Step 3: Write minimal implementation**

```md
## Load These References First
- `references/path-map.md`
- `references/writing-rules.md`
- `references/publishing-rules.md`

## Default Workflow
1. Lock the core judgment.
2. Stay in discussion mode until the user asks for the full article.
3. Write into `articles/`.
4. Keep `article-state/` and publish metadata in sync when packaging decisions are confirmed.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `wc -l skills/bill-wechat-daily/SKILL.md && rg -n "writing-rules|publishing-rules" skills/bill-wechat-daily/SKILL.md /Users/bytedance/.codex/skills/bill-wechat-daily/SKILL.md`
Expected: main skill shrinks and both copies reference the new files.

- [ ] **Step 5: Commit**

```bash
git add skills/bill-wechat-daily/SKILL.md skills/bill-wechat-daily/references/writing-rules.md skills/bill-wechat-daily/references/publishing-rules.md /Users/bytedance/.codex/skills/bill-wechat-daily/SKILL.md
git commit -m "Split writing skill references"
```

### Task 4: Wire State Layer Into heyBill and Publisher

**Files:**
- Modify: `scripts/run_heybill.py`
- Modify: `scripts/wechat_publisher.py`
- Test: `tests/test_run_heybill.py`

- [ ] **Step 1: Write the failing test**

```python
def test_wechat_publisher_prefers_confirmed_cover_text_and_background() -> None:
    state = {
        "article_file": file_name,
        "packaging": {"cover": {"text": "已确认", "background": "#abcdef"}},
    }
    # save state fixture
    result = wechat_publisher.load_cover_plan(article_path)
    assert result["text"] == "已确认"
    assert result["background"] == "#abcdef"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_run_heybill.py`
Expected: FAIL because publisher-specific state loading does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def load_cover_plan(article_path: Path) -> dict[str, str]:
    file_name = article_path.relative_to(ROOT / "articles").as_posix()
    state = run_heybill.read_article_state(file_name)
    cover = state.get("packaging", {}).get("cover", {})
    return {
        "text": cover.get("text") or derive_cover_text(title),
        "background": cover.get("background", ""),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_run_heybill.py && python3 -m py_compile scripts/wechat_publisher.py`
Expected: PASS and no syntax errors.

- [ ] **Step 5: Commit**

```bash
git add scripts/run_heybill.py scripts/wechat_publisher.py tests/test_run_heybill.py
git commit -m "Use article state in packaging flow"
```

### Task 5: Define Feedback Model

**Files:**
- Modify: `publishing-tracker.md`
- Create: `article-state/feedback-playbook.md`
- Create: `article-state/examples/README.md`

- [ ] **Step 1: Write the failing test**

Use a manual checklist test:

```text
1. publishing-tracker.md is explicitly human-readable overview only.
2. article-state docs define where outcomes and retrospective notes belong.
3. The feedback model names the fields the agent should later use for review.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `rg -n "human-readable overview|outcomes|review" publishing-tracker.md article-state`
Expected: FAIL because these feedback-layer docs do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```md
## Feedback capture
- `outcomes.reads`
- `outcomes.likes`
- `outcomes.shares`
- `outcomes.reader_feedback`
- `review.what_worked`
- `review.what_failed`
- `review.next_adjustment`
```

- [ ] **Step 4: Run test to verify it passes**

Run: `rg -n "outcomes|review|human-readable overview" publishing-tracker.md article-state`
Expected: matches across the tracker and feedback docs.

- [ ] **Step 5: Commit**

```bash
git add publishing-tracker.md article-state/feedback-playbook.md article-state/examples/README.md
git commit -m "Document feedback capture model"
```

### Task 6: Clean Repository Noise

**Files:**
- Modify: `.gitignore`
- Delete: `.DS_Store`
- Delete: `articles/.DS_Store`
- Delete: `assets/.DS_Store`
- Delete: `scripts/__pycache__/build_wechat_page.cpython-314.pyc`
- Delete: `scripts/__pycache__/publish_candidate.cpython-314.pyc`
- Delete: `scripts/__pycache__/publish_pipeline.cpython-314.pyc`
- Delete: `scripts/__pycache__/run_heybill.cpython-314.pyc`
- Delete: `scripts/__pycache__/shift_publish_dates.cpython-314.pyc`
- Delete: `scripts/__pycache__/wechat_publisher.cpython-314.pyc`
- Delete: `tests/__pycache__/test_run_heybill.cpython-314.pyc`

- [ ] **Step 1: Write the failing test**

Use a manual checklist test:

```text
1. No tracked `.DS_Store` or `__pycache__` files remain.
2. `.gitignore` blocks `.publish` runtime noise but allows intentional state files under `article-state/`.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `find . -name '.DS_Store' -o -path '*/__pycache__/*'`
Expected: FAIL because tracked noise files currently exist.

- [ ] **Step 3: Write minimal implementation**

```gitignore
.DS_Store
__pycache__/
*.pyc
.publish/*.tmp
.publish/*.log
```

- [ ] **Step 4: Run test to verify it passes**

Run: `find . -name '.DS_Store' -o -path '*/__pycache__/*'`
Expected: no output for tracked workspace files after deletions.

- [ ] **Step 5: Commit**

```bash
git add .gitignore
git rm .DS_Store articles/.DS_Store assets/.DS_Store scripts/__pycache__/*.pyc tests/__pycache__/*.pyc
git commit -m "Clean repository runtime noise"
```

### Task 7: Final Verification and Integration Check

**Files:**
- Modify: none unless verification exposes gaps

- [ ] **Step 1: Run focused automated verification**

Run: `python3 -m unittest tests/test_run_heybill.py`
Expected: `OK`

- [ ] **Step 2: Run syntax verification for the main Python entrypoints**

Run: `python3 -m py_compile scripts/run_heybill.py scripts/wechat_publisher.py scripts/publish_pipeline.py scripts/publish_candidate.py`
Expected: no output

- [ ] **Step 3: Run repository structure checks**

Run: `rg -n "article-state|AGENTS|writing-rules|publishing-rules" README.md AGENTS.md skills/bill-wechat-daily/SKILL.md article-state`
Expected: matches showing the new guidance layers exist and point to each other.

- [ ] **Step 4: Review git diff and status**

Run: `git status --short && git diff --stat`
Expected: only intended files are modified or newly added.

- [ ] **Step 5: Commit or amend only if verification uncovered required fixes**

```bash
git add <any verification follow-up files>
git commit -m "Polish writing agent system integration"
```
