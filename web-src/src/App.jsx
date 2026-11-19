import React, { useEffect, useState } from "react";
import "./style.css";

const initialSelection = () => ({
  inbox: { selected: true, months: 6, before: "" },
  archive: { selected: true, months: 3, before: "" },
});

async function api(path, body) {
  const response = await fetch(`/api/${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-Token": window.__GMAIL_SESSION_TOKEN__,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const result = await response.json();
  if (!response.ok) {
    const message = typeof result.detail === "string" ? result.detail : "Invalid request.";
    throw new Error(message);
  }
  return result;
}

export default function App() {
  const [tab, setTab] = useState("cleanup");
  const [accounts, setAccounts] = useState([]);
  const [account, setAccount] = useState("");
  const [selections, setSelections] = useState({});
  const [preview, setPreview] = useState(null);
  const [confirming, setConfirming] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [path, setPath] = useState("");
  const [credentialValue, setCredentialValue] = useState("");
  const [connection, setConnection] = useState({});
  const [config, setConfig] = useState({ source: "not checked", path: null });
  const selection = selections[account] || initialSelection();

  async function run(action) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await action();
    } catch (err) {
      setError(err.message || "Operation failed.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    run(async () => {
      const result = await api("accounts");
      setAccounts(result.accounts);
      setAccount(result.accounts[0] || "");
      setConfig(await api("config"));
    });
  }, []);

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
    const result = await api("accounts", {});
    const list = await api("accounts");
    setAccounts(list.accounts);
    changeAccount(result.account);
    setMessage(`Authorized ${result.account}.`);
  }

  async function applyConfig(config) {
    await api("config", config);
    setCredentialValue("");
    setConfig(await api("config"));
    setMessage("OAuth client override applied for this session.");
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

  return (
    <div className="layout">
      <aside>
        <strong>gmail-cleanup</strong>
        <nav>
          <button className={tab === "cleanup" ? "active" : ""} onClick={() => setTab("cleanup")}>Cleanup</button>
          <button className={tab === "admin" ? "active" : ""} onClick={() => setTab("admin")}>Admin</button>
        </nav>
        <div className="status">Gmail: {connection[account]?.status || "not tested"}</div>
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
              ) : <p>No accounts connected. Open Admin to add an account.</p>}
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
            <h1>Admin</h1>
            <p>Connect accounts, configure Gmail access and verify connections.</p>
            <section>
              <h2>Google accounts</h2>
              <ul>{accounts.map((email) => <li key={email}>{email} {account === email ? "(selected)" : ""}</li>)}</ul>
              <button className="primary" disabled={busy} onClick={() => run(addAccount)}>+ Add account</button>
              <p>Each account is authorized separately using Google’s account chooser.</p>
            </section>
            <section>
              <h2>Gmail connection</h2>
              <p>Configure a Google OAuth desktop client in .env or override it for this session.</p>
              <p>Current source: {config.source}{config.path ? ` (${config.path})` : ""}</p>
              <label className="field">OAuth client credentials path
                <input value={path} onChange={(e) => setPath(e.target.value)} placeholder="Use configured .env value" />
              </label>
              <button disabled={busy || !path} onClick={() => run(() => applyConfig({ path }))}>Use path</button>
              <label className="field">Or override the OAuth client JSON value
                <input type="password" value={credentialValue} onChange={(e) => setCredentialValue(e.target.value)} placeholder="Enter client JSON (masked)" />
              </label>
              <label className="field">Or choose a local OAuth client JSON file
                <input type="file" accept=".json,application/json" onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) run(async () => setCredentialValue(await file.text()));
                }} />
              </label>
              <button disabled={busy || !credentialValue} onClick={() => run(() => applyConfig({ value: credentialValue }))}>Apply value</button>
              <p>Account: {account || "none selected"} · Status: {connection[account]?.status || "not tested"}
                {connection[account]?.tested_at ? ` · Last tested: ${connection[account].tested_at}` : ""}</p>
              <button className="primary" disabled={busy || !account} onClick={() => run(testConnection)}>Test connection</button>
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
