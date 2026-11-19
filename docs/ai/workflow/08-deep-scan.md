# 08 — The Deep Scan

Docs go out of date while nobody is looking at them. The pre-commit routine keeps up the docs a
change touches. A **deep scan** looks for the rest: the README that still says "four commands" after
a fifth was added, the epic still marked "not started" with its stories done, the doc that names a
file that moved. It is on request, because it costs effort ([directive](../directives/deep-scan.md)).

The work is split by what each side is good at. **Code** does the mechanical, exact, repeated checks:
no credits, the same answer every time. The **agent** does the judgment: does this still hold, what
did a decision make moot, what should the page say. The **human** decides.

| | Pre-commit routine | `raven check` | Deep scan |
|---|---|---|---|
| Question | Did this change update the docs it touches? | Is the structure there? | Is what the docs say still true? |
| When | Every commit | Any time, and in CI | On request, or after a major change |
| Who | The agent | Raven, no AI | Raven for the mechanical part, the agent for the rest |

## The steps

### 0. Agree the scope

Which repository or repositories, and whether the whole docs tree or only what a recent change
touched. Start from a checkout of the current mainline, on a new branch or worktree, so the scan and
its fixes land on current text.

### 1. The mechanical pass: use code

Run `raven docs-scan --json` and read the findings (it is read-only and free). If the command does
not exist yet, do these checks with a throwaway script **outside the repository**, and say so in the
report:

| Check | What it looks for |
|-------|-------------------|
| Links | A relative link to a file that does not exist |
| Anchors | A link to a heading that is gone or renamed |
| Folder indexes | A folder README that does not name a sibling file or subfolder |
| Orphans | A doc nothing links to |
| Backlog and ADR indexes | An epic or ADR file missing from its index, or an index entry with no file |
| `make` targets | A `make X` in the docs where the Makefile has no `X` |
| Counts | A number beside "commands", "scripts", "tools" or "checks" that disagrees with what can be counted |
| Python version | A version in the docs that differs from `requires-python` |
| Stale phrases | Words the project has retired |
| Statuses | An epic header that disagrees with its stories; an ADR still `Proposed` that was built |
| Backticked paths | A repository path written in backticks that no longer exists |

The first six rows are exact. The rest are heuristics: treat each as a prompt to look, not a verdict.

Whoever writes the throwaway script should avoid what went wrong the first time:

- Take the file list from git (tracked files plus untracked files git does not ignore). A directory
  walk reads `node_modules` and local output and reports thousands of false problems.
- Keep inline code in a heading when computing its anchor; skip only fenced blocks.
- Skip raven-managed `docs/ai` files; their example links are broken by design.
- Skip the three logs and the bodies of ADRs when looking for stale wording. They record what was
  true then.
- Never read a `{a,b,c}` in a tool's `--help` as a list of subcommands. It is often the choices of one
  option.

### 2. Fix what is mechanical

Fix broken links, missing index entries and wrong counts in place. Do not delete a doc to clear a
finding; retire it in its own change and say so.

### 3. The judgment pass

Read, and where a claim can be tested, test it. Work through these in order of how much a wrong
statement misleads a reader:

| Look at | Ask |
|---------|-----|
| The README, the docs index and the help index | Do the stated counts, commands, versions and install steps match `pyproject.toml`, the Makefile and what `--version` and `--help` print? |
| The user docs | Is every command, option and setting documented, and is what it says still what the tool does? (Raven does not check this yet; compare each tool's `--help` with its docs.) |
| The backlog | Does each epic header agree with its stories? Does any Done story's acceptance criterion no longer hold? Did a decision make an epic or story moot? Is a Backlog story already built? |
| Decisions (ADRs and the decision log) | Is a `Proposed` decision built? Was an `Accepted` one reversed? Do the docs that depended on a superseded decision still describe the old way? |
| The bug log | Is an open bug fixed, or moot? |
| Statements about other projects | Is a project described as active that is archived, renamed or moved? Check the other project (git, the host CLI), not memory |
| Text the project emits (templates, scaffolds, generated docs) | Does it still say what is true? A stale sentence here reaches every new project |
| Published copies | Does the publish plan list orphans? Report them; never reconcile on your own |

### 4. Sort what you found

Three piles, kept apart in the report:

- **Fixed:** mechanical, or plainly stale, with the evidence.
- **Proposed for the human:** anything that needs a decision (closing an epic, changing an ADR's
  status, publishing a section, retiring a story). Where a decision already recorded settles it, you
  may apply the change; name the decision and ask for confirmation.
- **Not checked.** Say what you did not read or run.

### 5. Verify

Run the mechanical pass again; each remaining finding is either fixed or explained. Run the project's
own gates: `raven check`, the tests, the diagram check. Confirm that links and indexes you touched
still resolve.

### 6. Report, then hold

One docs branch and one request per repository. The task-log row and the request description state:

1. **Scope:** which repositories, which docs.
2. **How it was scanned:** what ran as code, what was read by the agent, what was only sampled.
3. **Fixed.**
4. **For the owner:** the decisions.
5. **Not verified or not covered.**

Hold for review, as with any change ([05 — Review & Publish](./05-review-and-publish.md)).

## Keeping the cost down

- Let code clear the mechanical checks first, then read only where a judgment is needed.
- Do not re-read what a scan already cleared.
- A scan of one repository is one effort. Do the second repository as its own pass, from step 0.

## Related

- [Directive — Deep Scan](../directives/deep-scan.md): when to run one, and the rules.
- [03 — Backlog & Logs](./03-backlog-and-logs.md): the formats this checks, and the pre-commit routine.
- [use-raven](../directives/use-raven.md): what to do when raven has no command for a step.
