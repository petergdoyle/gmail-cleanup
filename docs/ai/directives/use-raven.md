# Directive — Use raven

**Rule:** raven is installed to do certain jobs the same way every time. When a task matches a
raven command, **run the command**; do not rebuild its function by hand. If raven is not installed,
tell the human how to install it; do not reimplement it. If raven has no command for the task, say so
and follow [When raven has no command](#when-raven-has-no-command-for-the-task) below.

## Why

- **The same result every time.** A hand-built version of a raven job comes out a little different in
  each session and from each agent. The command is tested, so it does not.
- **It costs less.** What a raven command costs in AI effort was paid once, when it was built. Doing the
  same job by hand pays again each time, with small variations.
- **The human reviews one thing.** A raven command's output is familiar and its rules are written down.
  A one-off script has to be read from scratch.

## Is raven here?

Check before relying on it:

```bash
command -v raven && raven --version
raven doctor        # read-only: the build, the docs/ai template, this project's docs/ai, companion tools, glab
```

- **Not found:** tell the human, and give them the install command from raven's README
  (`uv tool install --python 3.12 "git+ssh://git@repo.dpsk12.org/amazon-web-services/dps-productivity/project-raven.git"`).
  Ask before installing it. Do not write a substitute.
- **`raven doctor` says the build is behind:** tell the human (`make update` in a raven checkout fixes it).
  It is information; carry on with the installed build.

## The commands

| Task | Command | Reads or writes | How to use it |
|------|---------|-----------------|---------------|
| Is this project conformant? | `raven check [PATH]` (`--json`) | Reads | Exit 1 means gaps; advisories do not fail it. Read each finding's detail: it names the fix. Run it before and after a structural change |
| Start a new project | `raven new NAME --archetype KIND` | Writes a new folder | Run it with `--dry-run` first and show the human. The wizard (`raven new` alone) needs the human, not you. Never use `--force` without their go-ahead |
| Is `docs/ai` current? | `raven docs-ai status [PATH]` | Reads | Exit 1 means files are missing, behind, or differ with no record |
| Bring `docs/ai` up to date | `raven docs-ai update [PATH]` | Writes `docs/ai/` and `.raven/` | Run with `--dry-run` first. Files the project edited are kept and listed. Do not use `--force` without the human's go-ahead. It does not commit |
| Check the machine and raven | `raven doctor` | Reads | Run it at the start of a session, or when something raven-shaped fails. It also says whether `glab` is installed and logged in for this project's host, which you need before opening a request |
| A dev server is holding a port | `raven port-scan --list` | Reads (stopping writes) | List first. Stop a process only when the human has chosen it. Do not run `--all` or `--force` on your own |

`raven <command> --help` prints the options and worked examples. raven's own repository documents every
command, option and exit code in `docs/help/`.

## When raven has no command for the task

raven does not do everything. Today it has **no command** to upgrade a project's Python version or
libraries, to adopt a project it did not scaffold, to add a database or an LLM provider, to check the
structure of the task, bug and decision logs, or to set up a CI pipeline. Some of these are planned.

When a task is raven-shaped but there is no command:

1. **Say so plainly:** "raven has no command for this yet."
2. **Name the plan if there is one.** raven's `docs/help/01-what-raven-does.md` lists what is not built
   yet and its epic. Do not guess.
3. **Offer the human the choice:** wait for the command, or do it by hand now. Do not improvise silently.
4. **If they choose by hand:** keep it small and reversible (its own branch, one concern per commit), verify
   it, and write in the task-log that it was a raven candidate, so it can become a command.

## What raven will not do, and what stays with you

- raven **never commits, pushes, merges or publishes**. You still run the pre-commit routine, hold for
  review, and open the request ([review and publish](../workflow/05-review-and-publish.md),
  [git host and reviews](./git-host-and-reviews.md)).
- `raven new --force`, `raven docs-ai update --force` and any `raven port-scan` that stops a process change
  things that are hard to undo or that the human may not expect: they need the human's go-ahead.
- raven's output is evidence, not a verdict. A clean `raven check` means the structure matches. It does not
  mean the tests pass or the code is right. Report what raven said, including advisories.

## Don't

- Don't rebuild a raven command's job by hand when the command exists: no hand-made `docs/ai` folder, no
  copied scaffold, no checking the structure by listing files, no killing processes by id.
- Don't claim raven can do something it cannot. If you are unsure, run `raven --help` or `raven <command> --help`.
- Don't edit `.raven/manifest.json` or `.raven/docs-ai.json` by hand: raven writes them, and
  `raven docs-ai status` relies on them.
- Don't hide it when a task was done by hand because raven had no command. Say so in the task-log.

## Note

This directive is part of the working model raven installs, so it arrives in a project with
`raven new` or `raven docs-ai update`. When raven gains a command, its row is added here, and a test in
raven fails until it is.
