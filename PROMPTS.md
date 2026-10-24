## Entry 1 - 2026-10-20
- **What I asked:** An example route that takes a name from the URL.
- **What it produced:** A route that returned the name inside an f-string with no escaping.
- **What was wrong:** Whatever the user types goes straight into the page, so a script could run in the browser (XSS).
- **What I did instead:** Deleted the route. I use Jinja templates, which escape text. Commit: <https://github.com/bushramd/TrustVault>

## Entry 2 - 2026-10-21
- **What I asked:** A role check that also records refused attempts in the audit log.
- **What it produced:** role_required logged refusals only for logged-in users. A visitor who was not logged in was redirected without any record.
- **What was wrong:** The requirement says refused attempts must be recorded. Logged-out attempts were missing.
- **What I did instead:** Added log_event to both decorators for the not-logged-in case, and tested it by opening /admin while logged out. Commit: <https://github.com/bushramd/TrustVault>

## Entry 3 - 2026-10-21
- **What I asked:** A starter Flask app.
- **What it produced:** app.run(debug=True) at the bottom.
- **What was wrong:** Debug mode shows an interactive debugger that can run code. It must never be on in production.
- **What I did instead:** Debug mode now turns on only if FLASK_DEBUG=1. Commit: <https://github.com/bushramd/TrustVault/commits/main/>

## Instructions I give the AI every time
- Check authorisation on the server for every route. A hidden button is not security.
- Record refused attempts in the audit log, not only successful ones.
- Use ? placeholders in every SQL query.
- Tell me what could be wrong with the code you just gave me.

## Entry 4 - 2026-10-22
- **What I asked:** A permission check that logs refused attempts in the audit log.
- **What it produced:** require_access logged refusals using the permission name ("read"), while successful downloads were logged as "download".
- **What was wrong:** A refused download showed up as "read denied", so searching the log for refused downloads found nothing. My automated test test_denied_download_is_in_audit_log failed and showed it.
- **What I did instead:** Added an audit_action argument so download and revoke log under their own names. All 13 tests pass. Commit: <https://github.com/bushramd/TrustVault/commits/main/>

## Entry 5 - 2026-10-23
- **What I asked:** How to deploy the Flask app on Render.
- **What happened:** My first deploy failed with "gunicorn: command not found".
- **What was wrong:** The gunicorn line and the deployment changes were not committed yet, so Render built an older commit.
- **What I did instead:** Added gunicorn to requirements.txt, committed and pushed, then checked that the deploy's source commit changed. Commit: <https://github.com/bushramd/TrustVault/commits/main/>
