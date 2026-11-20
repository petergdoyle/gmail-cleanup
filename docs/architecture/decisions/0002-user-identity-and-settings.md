# ADR 0002 — Application Identity and Per-User Settings

**Status:** Accepted for local development; implementation under review
**Date:** 2026-11-19

## Context

The current UI is a single-user, loopback-only prototype. Its shared process
token and global Keychain account index do not authenticate application users
or isolate their Google accounts. A multi-user application must distinguish
application identity from authorization to access each Gmail account.

## Decision

- Use a pluggable application sign-in boundary. For local development, use a
  locally configured username and password. Authentik/OIDC is deferred to the
  deployment effort; it is not implemented by selecting the local provider.
  Future OIDC identities must use the verified issuer and subject, not email alone.
- The application operator configures a Google OAuth client. Each signed-in
  user separately grants Gmail access to each Google account they connect.
- Store user-owned Google account associations, cleanup settings and theme
  preferences in SQLite. Encrypt stored Google credentials using an
  operator-provided key held separately from the database.
- Preserve the existing CLI's independently configured credentials and
  scripting use. Do not silently import the current global Keychain accounts
  into a user profile.
- Make Settings, the authenticated user and sign-out visible in the UI.
  Users can choose light or dark and retain their settings across sessions.

## Rationale

The authentication provider supplies application identity without conflating it
with Gmail access.
Explicit per-user ownership prevents one user's linked accounts and cleanup
settings from becoming another's. SQLite is adequate for the agreed local
development direction without deciding the final shared deployment topology.

## Consequences

- The existing process-global preview, Google configuration and account index
  must not be used as multi-user authorization boundaries. All account access,
  previews and cleanup operations require user ownership checks.
- Replace the server-side desktop OAuth callback with a browser-based web OAuth
  flow for the web UI. The Google client type and registered redirect URI must
  match that flow. The CLI desktop flow remains separate.
- Validate OIDC issuer, audience, signature, nonce and state; protect sessions,
  callback state and state-changing requests when Authentik is implemented.
  The local development provider must be explicitly configured, restricted to
  loopback, and must not be presented as production authentication.
- Encryption-key management, backup, rotation and production HTTPS, session and
  proxy settings must be documented and reviewed before shared deployment.
  Losing the encryption key makes stored Gmail credentials unrecoverable.
- Google OAuth scopes and consent-screen verification may impose restrictions
  beyond app configuration.

## Alternatives Considered

- **Authentik for local development:** initially chosen, but replaced by a
  local development provider at the user's request; Authentik remains a future
  deployment provider.
- **Google login as application identity:** not selected; application login
  must be separate from Gmail authorization.
- **Global macOS Keychain account index:** retained only for the existing CLI
  workflow; it does not isolate different application users.

## Follow-ups

- Review the local implementation and verify it against real Google test accounts.
- Implement and exercise Authentik as part of the future deployment effort.
- Decide the shared Proxmox deployment separately; see
  [D04](../../product/backlog/design-decision-log.md).
