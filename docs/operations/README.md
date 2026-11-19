# gmail-cleanup — Operations

How to set up, run, publish and operate gmail-cleanup: environment and tooling
setup, reusable procedures, deployment, and runbooks. This is the "how do I do this
thing" shelf, as opposed to `architecture/` (why it is built this way) and `help/`
(end-user guides for the running product).

## Contents

| Document | What it covers |
|----------|----------------|
| [01 — Setup and run](01-setup-and-run.md) | Install the dependencies, run the checks, and (for projects that run) start and stop the app |

## What belongs here

- Setting up a machine or an environment (tools, credentials, `.env` keys by name).
- Running, testing and publishing the project, and the commands that do it.
- Deployment steps and rollback, once the project is deployed.
- Runbooks: what to do when something breaks, and how to tell.

Add a numbered file (`02-…`, `03-…`) for each procedure and list it in the table above.
Never put a secret value in these pages; name the setting and say where it lives.
