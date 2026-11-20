import React, { useEffect, useState } from "react";
import "./style.css";

const initialSelection = () => ({
  inbox: { selected: true, months: 6, before: "" },
  archive: { selected: true, months: 3, before: "" },
});

let csrfToken = "";

async function api(path, body) {
  const response = await fetch(`/api/${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Bootstrap-Token": window.__GMAIL_BOOTSTRAP_TOKEN__,
      "X-CSRF-Token": csrfToken,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const result = await response.json();
  if (!response.ok) {
    const message = typeof result.detail === "string" ? result.detail : "Invalid request.";
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return result;
}

export default function App() {
  const [tab, setTab] = useState("cleanup");
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [theme, setTheme] = useState("light");
  const [accounts, setAccounts] = useState([]);
  const [account, setAccount] = useState("");
  const [selections, setSelections] = useState({});
  const [preview, setPreview] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [connection, setConnection] = useState({});
  const selection = selections[account] || initialSelection();

  function clearUser() {
    csrfToken = "";
    setUser(null);
    setAccounts([]);
    setSelections({});
    setAccount("");
    setPreview(null);
    setConfirming(false);
    setConnection({});
    setTheme("light");
    setTab("cleanup");
    setPassword("");
  }

  async function run(action) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await action();
    } catch (err) {
      if (err.status === 401 && user) {
        clearUser();
        setError("Your session expired. Sign in again.");
      } else {
        setError(err.message || "Operation failed.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function loadUser(result) {
    csrfToken = result.csrf;
    const [accountData, settings] = await Promise.all([api("accounts"), api("settings")]);
    setUser(result.user);
    setAccounts(accountData.accounts);
    setAccount(accountData.accounts[0] || "");
    setSelections(Object.fromEntries(
      Object.entries(settings.accounts).filter(([, value]) => value !== null).map(
        ([email, value]) => [email, Object.fromEntries(
          Object.entries(value).map(([name, box]) => [name, { ...box, before: box.before || "" }])
        )]
      )
    ));
    setTheme(settings.theme);
    const url = new URL(window.location.href);
    const google = url.searchParams.get("google");
    if (google) {
      setTab("settings");
      if (google === "connected") setMessage("Google account connected.");
      if (google === "denied") setError("Google authorization was cancelled or denied.");
      url.searchParams.delete("google");
      window.history.replaceState(null, "", url);
    }
  }

  useEffect(() => {
    api("session").then(loadUser).catch((err) => {
      if (err.status !== 401) setError(err.message);
    }).finally(() => setCheckingSession(false));
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  function changeAccount(next) {
    setAccount(next);
    setPreview(null);
    setConfirming(false);
    setMessage("");
    setError("");
  }

  function updateBox(name, changes) {
    setSelections((previous) => ({
      ...previous,
      [account]: {
        ...(previous[account] || initialSelection()),
        [name]: { ...(previous[account] || initialSelection())[name], ...changes },
      },
    }));
    setPreview(null);
  }

  function moveAccount(offset) {
    const index = accounts.indexOf(account);
    const next = index + offset;
    if (next >= 0 && next < accounts.length) changeAccount(accounts[next]);
  }

  async function addAccount() {
    const result = await api("accounts/connect", {});
    window.location.assign(result.url);
  }

  async function savePreferences() {
    await api("settings/account", {
      account,
      ...Object.fromEntries(Object.entries(selection).map(([name, box]) => [
        name, { ...box, months: Number(box.months), before: box.before || null },
      ])),
    });
    setMessage(`Saved cleanup preferences for ${account}.`);
  }

  async function testConnection() {
    setConnection((prev) => ({ ...prev, [account]: null }));
    const result = await api("test-connection", { account });
    setConnection((prev) => ({ ...prev, [account]: result }));
    setMessage(`Gmail connection succeeded for ${account}.`);
  }

  async function showPreview() {
    const mailboxes = Object.entries(selection)
      .filter(([, box]) => box.selected)
      .map(([name, box]) => ({
        name,
        ...(box.before ? { before: box.before } : { months: Number(box.months) }),
      }));
    if (!mailboxes.length) throw new Error("Select at least one mailbox.");
    setPreview(await api("preview", { account, mailboxes }));
  }

  async function cleanup() {
    let result;
    try {
      result = await api("cleanup", { account, preview_id: preview.preview_id });
    } finally {
      setPreview(null);
      setConfirming(false);
    }
    setMessage(`Moved ${result.moved} messages to Gmail Trash for ${result.account} at ${result.completed_at}.`);
  }

  if (checkingSession) return <p role="status">Checking session…</p>;
  if (!user) return <div className="login-page"><section className="login-card">
    <h1>Sign in to gmail-cleanup</h1>
    <p>Local development sign-in. Gmail accounts are connected separately.</p>
    <form onSubmit={(event) => {
      event.preventDefault();
      run(async () => {
        const result = await api("login", { username, password });
        setPassword("");
        await loadUser(result);
      });
    }}>
      <label className="field">Username<input autoComplete="username" value={username}
        onChange={(e) => setUsername(e.target.value)} required /></label>
      <label className="field">Password<input type="password" autoComplete="current-password"
        value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
      <button className="primary" disabled={busy}>Sign in</button>
    </form>
    {error && <p role="alert" className="error">{error}</p>}
    <p>Development only. Do not expose this service to a network.</p>
  </section></div>;

  return (
    <div className="layout">
      <aside>
        <strong>gmail-cleanup</strong>
        <nav>
          <button className={tab === "cleanup" ? "active" : ""} onClick={() => setTab("cleanup")}>Cleanup</button>
          <button className={tab === "settings" ? "active" : ""} onClick={() => setTab("settings")}>Settings</button>
        </nav>
        <div className="status">
          <div>Gmail: {connection[account]?.status || "not tested"}</div>
          <div className="signed-in">{user}</div>
          <button onClick={() => run(async () => {
            await api("logout", {}); clearUser();
          })}>Sign out</button>
        </div>
      </aside>
      <main>
        {tab === "cleanup" ? (
          <>
            <h1>Clean up old mail</h1>
            <p>Select an account and mailboxes. Preview before moving messages to Trash.</p>
            <section>
              <h2>Google account</h2>
              {accounts.length ? (
                <div className="account-row">
                  <label className="sr-only" htmlFor="account">Google account</label>
                  <select id="account" value={account} onChange={(e) => changeAccount(e.target.value)} disabled={busy}>
                    {accounts.map((email) => <option key={email}>{email}</option>)}
                  </select>
                  <button onClick={() => moveAccount(-1)} disabled={busy || accounts.indexOf(account) <= 0}>← Previous</button>
                  <button onClick={() => moveAccount(1)} disabled={busy || accounts.indexOf(account) >= accounts.length - 1}>Next →</button>
                </div>
              ) : <p>No accounts connected. Open Settings to add an account.</p>}
            </section>
            <section>
              <h2>Mailboxes and age</h2>
              <p>Use months or a specific date for each selected mailbox.</p>
              {["inbox", "archive"].map((name) => {
                const box = selection[name];
                return (
                  <div className="mailbox" key={name}>
                    <div className="mailbox-name">
                      <label><input type="checkbox" checked={box.selected} disabled={!account || busy}
                        onChange={(e) => updateBox(name, { selected: e.target.checked })} />
                        <strong>{name === "inbox" ? "Inbox" : "Archive"}</strong>
                      </label>
                      {name === "archive" && <small>Received mail outside Inbox, Sent, Drafts, Spam and Trash, including mail with custom labels.</small>}
                    </div>
                    <label>Older than <input type="number" min="1" value={box.months}
                      disabled={!account || busy || !box.selected || Boolean(box.before)}
                      onChange={(e) => updateBox(name, { months: e.target.value })} /> months</label>
                    <label>or before <input type="date" value={box.before}
                      disabled={!account || busy || !box.selected}
                      onChange={(e) => updateBox(name, { before: e.target.value })} /></label>
                  </div>
                );
              })}
              <button className="primary" disabled={!account || busy} onClick={() => run(showPreview)}>Preview</button>
              <button disabled={!account || busy} onClick={() => run(savePreferences)}>Save preferences</button>
              <span className="hint"> Preview does not change your mail.</span>
            </section>
            {preview && <section>
              <h2>Preview results</h2>
              <p>Account: <strong>{preview.account}</strong></p>
              {Object.entries(preview.counts).map(([name, count]) => (
                <p key={name}>{name}: {count} messages ({preview.queries[name]})</p>
              ))}
              <p>{preview.total} messages total. Preview expires after 15 minutes.</p>
              <p>Moving a message to Trash affects all its labels. Archive includes eligible messages with custom labels.</p>
              <button className="danger" disabled={busy || preview.total === 0} onClick={() => setConfirming(true)}>Move to Trash…</button>
            </section>}
          </>
        ) : (
          <>
            <h1>Settings</h1>
            <p>Your connected Gmail accounts and preferences are private to your user.</p>
            <section>
              <h2>Google accounts</h2>
              <ul>{accounts.map((email) => <li key={email}>{email} {account === email ? "(selected)" : ""}</li>)}</ul>
              <button className="primary" disabled={busy} onClick={() => run(addAccount)}>+ Connect Google account</button>
              <p>Choose an account and grant Gmail access on Google. Ask your operator to configure Google OAuth if needed.</p>
              <button disabled={busy || !account} onClick={() => run(testConnection)}>Test selected account</button>
              <button disabled={busy || !account} onClick={() => run(async () => {
                await api("accounts/remove", { account });
                setSelections((previous) => {
                  const next = { ...previous };
                  delete next[account];
                  return next;
                });
                setConnection((previous) => {
                  const next = { ...previous };
                  delete next[account];
                  return next;
                });
                const list = await api("accounts"); setAccounts(list.accounts);
                changeAccount(list.accounts[0] || "");
              })}>Remove selected account</button>
            </section>
            <section>
              <h2>Cleanup preferences</h2>
              <p>Select an account and save its mailbox preferences on the Cleanup screen.</p>
              <button onClick={() => setTab("cleanup")}>Edit preferences</button>
            </section>
            <section>
              <h2>Appearance</h2>
              <p>Your theme is saved to your application account.</p>
              {["light", "dark"].map((choice) => <button key={choice}
                className={theme === choice ? "primary" : ""}
                onClick={() => run(async () => { await api("settings/theme", { theme: choice }); setTheme(choice); })}>
                {choice === "light" ? "Light" : "Dark"}
              </button>)}
            </section>
          </>
        )}
        {busy && <p role="status">Working… Google authorization may open in your browser.</p>}
        {message && <p role="status" className="notice">{message}</p>}
        {error && <p role="alert" className="error">{error}</p>}
      </main>
      {confirming && preview && <div className="overlay">
        <div className="dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
          <h2 id="confirm-title">Move {preview.total} messages to Trash?</h2>
          <p>Google account: <strong>{preview.account}</strong></p>
          {Object.entries(preview.counts).map(([name, count]) => <p key={name}>{name}: {count} messages ({preview.queries[name]})</p>)}
          <p>Moving a message to Trash affects all its labels. Archive includes eligible messages with custom labels.</p>
          <p className="warning">Recover messages in Gmail Trash before Gmail removes them. Gmail normally deletes Trash after 30 days.</p>
          <div className="actions">
            <button disabled={busy} onClick={() => setConfirming(false)}>Cancel</button>
            <button className="danger" disabled={busy} onClick={() => run(cleanup)}>Move to Trash</button>
          </div>
        </div>
      </div>}
    </div>
  );
}
