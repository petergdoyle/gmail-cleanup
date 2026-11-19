# Directive — Connectivity

**Rule:** When an **internal** host (git, tracker, docs, or any service reachable
only on a private/corporate network) fails to resolve, treat it as a dropped
network/VPN connection. Tell the human and wait. **Do not debug the network.**

> **SUBSTITUTE / optional.** Keep this directive only if your project's hosts sit
> behind a VPN or private network that drops intermittently. If everything the
> agent touches is on the public internet, generalize it to ordinary transient
> network handling, or remove it. The reusable core is the *behavior*: don't spin
> on network diagnostics — report, pause, retry on the human's word.

## Why

Self-hosted/internal services are reachable only on the private network, and a VPN
can drop intermittently. A resolution failure for an internal host is almost always
the connection, not DNS, not the server, not the credential. Network diagnostics
waste the human's time and tell us nothing we don't already know.

## Do

- When a `git push` / `git fetch` / host-CLI call fails with
  "Could not resolve hostname <internal-host>" (or similar), say plainly:
  *"Can't resolve `<host>` — looks like the connection/VPN dropped. Let me know
  when it's back and I'll retry."*
- Note that **local work is safe** (the commit already exists locally; nothing is
  lost).
- When the human says the connection is back, **retry the exact operation** with no
  extra ceremony.

## Don't

- Don't run `ping`, `dig`, `host`, `nslookup`, `traceroute`, or any network
  diagnostic.
- Don't retry in a loop or "wait and try again" repeatedly on your own.
- Don't investigate DNS, SSH config, or the credential — none of those is the
  cause.
- Don't treat it as a server or auth error.
