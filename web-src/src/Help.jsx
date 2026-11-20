import React from "react";

export default function Help() {
  const callback = `${window.location.origin}/oauth/google/callback`;
  return <>
    <h1>Help &amp; Docs</h1>
    <p>Practical help for connecting Gmail and cleaning up safely.</p>
    <section id="google-setup">
      <span className="help-label">Local operator guide</span>
      <h2>Set up Google authorization</h2>
      <p>Signing in to this app is separate from granting access to a Google account.
        If someone else runs the app, ask its operator to complete this setup.</p>
      <ol className="help-steps">
        <li><strong>Prepare Google Cloud</strong>
          <p>In <a href="https://console.cloud.google.com/" target="_blank" rel="noreferrer">Google Cloud Console</a>,
            create or select a project, enable the Gmail API, and configure the OAuth consent screen.
            If the app is in testing, add each Google account as a test user.</p></li>
        <li><strong>Create a web application OAuth client</strong>
          <p>Under Credentials, create an OAuth client ID for a <strong>Web application</strong>.
            Add this exact authorized redirect URI for the address you are using:</p>
          <code className="help-code">{callback}</code>
          <p>The host and port must match exactly. Download the client JSON file.</p></li>
        <li><strong>Save the downloaded JSON privately</strong>
          <p>Place the file somewhere private. In the directory you use to launch the app,
            add its absolute path to the ignored <code>.env</code> file, for example:</p>
          <code className="help-code">GMAIL_WEB_CREDENTIALS_PATH="/private/path/client.json"</code>
          <p>Replace the example with your actual path. Do not paste the JSON or client secret
            into the app or commit it to Git. Environment variables override <code>.env</code>.</p></li>
        <li><strong>Restart and connect</strong>
          <p>Run <code>make dev-down</code> followed by <code>make dev-up</code>, then open
            Settings, connect your Google account and grant Gmail access. Select the account
            and test its connection.</p></li>
      </ol>
      <p>The CLI uses a separate desktop OAuth client and macOS Keychain. Google consent
        verification and testing settings can limit who can authorize and how long tokens last.</p>
      <p><a href="https://developers.google.com/workspace/gmail/api/quickstart/python" target="_blank" rel="noreferrer">Google Gmail API setup documentation</a></p>
    </section>
    <section>
      <h2>Preview before cleanup</h2>
      <p>Select a Google account and mailbox age or date, then preview and review the results.
        A preview does not change mail. Confirm separately to move the previewed messages to Trash.
        Gmail labels overlap: moving a message affects all its labels.</p>
    </section>
    <section>
      <h2>Recover mail</h2>
      <p>Restore messages from Gmail Trash before Google removes them, normally after 30 days;
        account policies can differ. This app does not restore messages itself.</p>
    </section>
  </>;
}
