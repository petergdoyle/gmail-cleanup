# Directive — Git Host & Reviews

**Rule:** The agent pushes **working branches** and opens **pull/merge requests**.
It **never merges, approves, deploys, or pushes to the mainline** (except the
one-time initial scaffold on a repo with no remote mainline yet). The human runs
the merge.

> **SUBSTITUTE: git host + review tooling.** This directive is written for a
> protected-mainline + request flow. The examples use a GitLab-style CLI
> (`glab`) and "merge request"; on GitHub substitute `gh` and "pull request", and
> on any other host its equivalent. The *rules* (branch + request, never merge,
> target the mainline explicitly, specific-file staging, no force-push to shared
> refs) are host-neutral.

## Why

This is the contract enforced at the mechanical level: agent proposes, human
disposes ([00 — Working Relationship](../00-working-relationship.md)). It is
defended three ways — the credential scope (no merge/approve), the agent's behavior
(this directive), and a protected mainline.

## Before you open a request or start another effort: look at what is already open

Another open request can change the order you should work in. Check before you push and before you start
a second effort, and tell the human what you found.

1. **List the open requests.**
   GitLab: `glab mr list --output json` (the default is open ones; add `--author` to narrow it).
   GitHub: `gh pr list --json number,title,headRefName,author`.
2. **Report them to the human** in a few lines: number, title, source branch, whether it is yours, and how far
   behind the mainline it is (`git rev-list --count origin/<branch>..origin/<mainline>`).
3. **Find the files you share.** Compare the files each open request changes with the files you have changed
   or will change (`git diff --name-only origin/<mainline>...HEAD`).
   GitLab: `glab api "projects/:id/merge_requests/<iid>/diffs"` (each entry has a `new_path`).
   GitHub: `gh pr diff <number> --name-only`.
   Shared files will conflict or need care. Files that every effort adds to at the top, such as a task-log or a
   bug-log, are the usual cause, and the conflict is trivial: keep both rows.
4. **Ask before going on.** Say which request should merge first and why (usually the smaller or the earlier one),
   and let the human decide whether to wait, merge first, or carry on. You never merge it.
5. **If you stack requests** (the second depends on the first), branch from the earlier branch and target the
   earlier branch explicitly, not the mainline, and say "merge in order" in the description. If they are merged
   out of order, nothing unreviewed reaches the mainline, and the host retargets the later request when the
   earlier branch is merged and removed.
6. **If the host CLI is missing or not logged in,** tell the human (for GitLab, `glab auth login --hostname <host>`)
   and wait. Do not fall back to raw `curl`. `raven doctor` says whether `glab` is installed and logged in for
   this project's host, so run it first.

## Do

- Work on a branch named for the effort; push it with `git push -u origin <branch>`.
- Open the request with your host's CLI, targeting the mainline **explicitly**.
  GitLab example:

  ```bash
  glab mr create --source-branch <branch> --target-branch <mainline> \
    --title "…" --description "…" --remove-source-branch --yes
  ```

  GitHub equivalent:

  ```bash
  gh pr create --base <mainline> --head <branch> --title "…" --body "…"
  ```

- Always pass the target branch **explicitly** — tooling can otherwise silently
  target a stale branch and show a spurious "N commits behind / conflicts" wall.
- Keep request titles concise (≈70 chars); put detail in the description (summary
  of changes, what was tested, anything still open). Keep the description
  single-line safe.
- Prefer `git commit -F <file>` for commit messages with special characters.
- After the human merges: `git fetch --prune`, fast-forward the local mainline,
  delete the merged branch, and start the next effort on a **fresh** branch off the
  updated mainline.
- Stage **specific files by name**; guard that no `.env`, `node_modules`, caches, or
  real (non-example) config get staged.

## Don't

- Don't `merge`, `approve`, or deploy. Don't push to the mainline (after the
  scaffold).
- Don't use `git push --force`, `reset --hard`, `clean -fd`, `branch -D` on shared
  refs, or `--no-verify`, unless the human explicitly asks.
- Don't modify git config. Don't use interactive flags (`-i`) — they hang.
- Don't fall back to raw `curl` for request creation when the host CLI is
  available; a hanging write call means retry with the CLI, not more `curl`.
- Don't reuse a branch whose request removed it on merge — re-pushing that name
  recreates it off a stale base and re-shows merged commits.

## Reading a request's state without the UI

GitLab:

```bash
glab api "projects/:id/merge_requests/<iid>"
# check: state, detailed_merge_status (mergeable), has_conflicts, target_branch
```

GitHub:

```bash
gh pr view <number> --json state,mergeable,mergeStateStatus,baseRefName
```

Deletion of a lingering/stale **remote** branch is a **human** action (the agent's
credential omits that permission by design).
