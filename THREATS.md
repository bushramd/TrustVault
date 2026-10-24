# THREATS.md

Status words: Fixed = done and proven by a test or by hand. Partly = some protection, a gap remains.
Planned = not done yet. Accepted = I know about it and chose to leave it.

| # | Threat | What I did | Proof | Status |
|---|--------|-----------|-------|--------|
| 1 | A user changes the number in the URL to open someone else's document | Every document route calls can_access(). Without a grant the answer is 404 | test_other_owner_cannot_download, test_viewer_without_grant_cannot_download | Fixed |
| 2 | A removed user keeps access through an old session | The cookie holds only the user id. Every request reloads the user and checks is_active | test_deactivated_user_loses_access_immediately | Fixed |
| 3 | A viewer types an admin or upload URL directly | role_required checks the role on the server and logs the refusal | test_viewer_cannot_open_admin_page, test_viewer_cannot_upload | Fixed |
| 4 | A harmful, disguised or very large file is uploaded | Type list, 5 MB limit, first bytes must match the type, random stored name | test_disguised_file_is_rejected | Partly. No virus scan |
| 5 | Someone edits or deletes audit log rows | The app has no route that changes the log. Database triggers refuse UPDATE and DELETE | test_audit_log_cannot_be_changed | Partly. Anyone with the database file could drop the triggers |
| 6 | Someone guesses a file's direct URL | Files are in uploads/, outside public folders, with random names. They are served only through the checked download route | By hand | Fixed |
| 7 | Passwords stolen from the database | Passwords are stored as hashes | Code review | Fixed |
| 8 | SQL injection | All queries use ? placeholders, including search | Code review, test_search_injection_attempt_leaks_nothing | Fixed |
| 9 | Script injection (XSS) through user text | Pages use Jinja templates, which escape text | Code review | Fixed |
| 10 | Guessing passwords again and again | After 10 failed logins for a username in 10 minutes, login is refused for 10 minutes. No per-address limit, and an attacker could lock a user out on purpose |
| 11 | Forged requests from another website (CSRF) | Cookies use SameSite=Lax. No CSRF tokens yet | None | Partly |
| 12 | The default secret key is used on the live site | SECRET_KEY is set on the host and is not in the code | Checked the Render Environment tab | Fixed |
| 13 | Debug mode left on in production | Debug turns on only if FLASK_DEBUG=1, which is not set on the host | Code review | Fixed |
| 14 | Refused attempts by logged-out visitors are not recorded | login_required and role_required log them | By hand: opened /admin logged out and saw the row | Fixed |
| 15 | A user with only read access deletes or shares a document | Delete and share are owner-only in can_access() | test_reader_cannot_delete_document, test_non_owner_cannot_share_document | Fixed |
| 16 | Taking access away does not work | The grant row is deleted and the database is checked on every request | test_grant_gives_access_and_revoke_removes_it | Fixed |
| 17 | Refused downloads missing from the audit log | Refusals are logged under the action name download | test_denied_download_is_in_audit_log | Fixed |
| 18 | Search shows titles of documents the user cannot see | Search filters are added on top of the access rule, so they can only narrow results | test_search_never_shows_other_users_documents | Fixed |
| 19 | Revoked user still finds the document in search | Search checks grants on every request | test_search_shows_shared_document_until_revoked | Fixed |
| 20 | Login cookie sent over plain HTTP | SESSION_COOKIE_SECURE is on in production, and the site is served over HTTPS | Opened the live site over https | Fixed |
| 21 | A downloaded file runs inside the browser | Files are sent as attachments, not displayed | Code review | Fixed |
| 22 | Deleted documents stay on disk | Delete only hides the document. The stored file stays | None | Accepted for now. Retention is not built |
| 23 | The edit permission does nothing | Users with an edit grant can replace the file through the same checks as upload | test_editor_can_replace_file, test_reader_cannot_replace_file, test_replace_rejects_disguised_file | Fixed |
| 24 | The admin pages show only the latest rows | A second admin page shows permission changes and refused attempts, the latest 100 of each. No paging or filters yet | test_admin_permissions_page_lists_grants_and_refusals | Partly |
| 25 | Live data is lost when the free host restarts | Demo users are created again at startup | None | Accepted because the host is free |
| 26 | Demo passwords are public in the README | They are demo only, so judges can log in. A real system would not do this | None | Accepted |
| 27 | No security headers such as Content-Security-Policy | Not added yet | None | Planned |
| 28 | A non-admin opens the permission page | role_required checks the role on the server and logs the refusal | test_viewer_cannot_open_permissions_page | Fixed |
| 29 | Old file versions stay on the server after a replace | The old file is kept as a simple version history. No cleanup yet | None | Accepted |