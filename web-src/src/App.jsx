import React, { useEffect, useState } from "react";
import Help from "./Help";
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
    error.code = result.code;
    throw error;
  }
  return result;
}

function Icon({ name }) {
  const paths = {
    mail: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></>,
    settings: <><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="3" /></>,
    help: <><circle cx="12" cy="12" r="9" /><path d="M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1.2-1.5 2.5M12 17h.01" /></>,
    logout: <><path d="M10 4H5v16h5M14 8l4 4-4 4M8 12h10" /></>,
  };
  return <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
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
  const [setupError, setSetupError] = useState(false);
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
    setSetupError(false);
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
    setSetupError(false);
    try {
      const result = await api("accounts/connect", {});
      window.location.assign(result.url);
    } catch (err) {
      if (err.code === "google_web_client_configuration") {
        setSetupError(true);
      } else {
        throw err;
      }
    }
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
    const testedAccount = account;
    setConnection((prev) => ({ ...prev, [testedAccount]: null }));
    try {
      const result = await api("test-connection", { account: testedAccount });
      setConnection((prev) => ({ ...prev, [testedAccount]: result }));
      setMessage(`Gmail connection succeeded for ${testedAccount}.`);
    } catch (err) {
      if (err.status !== 401) {
        setConnection((prev) => ({ ...prev, [testedAccount]: { status: "failed" } }));
      }
      throw err;
    }
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
        <div className="brand"><span className="brand-icon"><Icon name="mail" /></span>
          <div><strong>gmail-cleanup</strong><small>A calmer inbox</small></div></div>
        <div className="nav-heading">Workspace</div>
        <nav aria-label="Main navigation">
          {[["cleanup", "mail", "Cleanup"], ["settings", "settings", "Settings"], ["help", "help", "Help & Docs"]].map(([key, icon, label]) =>
            <button key={key} className={tab === key ? "active" : ""} aria-current={tab === key ? "page" : undefined}
              onClick={() => { setTab(key); setError(""); setMessage(""); }}>
              <Icon name={icon} />{label}
            </button>)}
        </nav>
        <div className="sidebar-user">
          <div className="identity"><span className="avatar" aria-hidden="true">{user.trim().slice(0, 2).toUpperCase()}</span>
            <div><strong>{user}</strong><small>Signed in</small></div></div>
          <button onClick={() => run(async () => {
            await api("logout", {}); clearUser();
          })}><Icon name="logout" />Sign out</button>
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
        ) : tab === "settings" ? (
          <>
            <h1>Settings</h1>
            <p>Your connected Gmail accounts and preferences are private to your user.</p>
            <section>
              <h2>Google accounts</h2>
              <button className="primary" disabled={busy} onClick={() => run(addAccount)}>+ Connect Google account</button>
              <p>Connect the accounts you want to clean up. App sign-in is separate.</p>
              {accounts.length ? <label className="field">Selected Google account
                <select value={account} onChange={(e) => changeAccount(e.target.value)} disabled={busy}>
                  {accounts.map((email) => <option key={email}>{email}</option>)}
                </select>
              </label> : <p>No Google accounts connected yet.</p>}
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
              {setupError && <div role="alert" className="setup-warning">
                <strong>Google authorization needs setup</strong>
                <p>The web OAuth client is missing or invalid. If you run this app locally,
                  follow the setup guide; otherwise ask your app operator for help.</p>
                <button className="text-button" onClick={() => { setTab("help"); setError(""); }}>
                  Open Google setup guide →
                </button>
              </div>}
            </section>
            <section>
              <h2>Connection test</h2>
              {!account ? <p>No account selected. Connect a Google account to test its connection.</p> :
                <p role="status">{account}: {connection[account]?.status === "connected" ?
                  `Test succeeded${connection[account].tested_at ? ` at ${new Date(connection[account].tested_at).toLocaleString()}` : ""}.` :
                  connection[account]?.status === "failed" ? "Test failed. Try again or reconnect the account." :
                    "Not tested in this session."}</p>}
              <button disabled={busy || !account} onClick={() => run(testConnection)}>Test selected account</button>
              <p>A test result applies only to the selected account and current session.</p>
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
        ) : <Help />}
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
