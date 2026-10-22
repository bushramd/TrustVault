# THREATS.md

Status words: Fixed = done and proven by a test or by hand. Partly = some protection, a gap remains.
Planned = not done yet. Accepted = I know about it and chose to leave it.

| # | Threat | What I did | Proof | Status |
|---|--------|-----------|-------|--------|
| 1 | A user changes the number in the URL to open someone else's document | Every document route calls can_access(). Without a grant the answer is 404 | test_other_owner_cannot_download, test_viewer_without_grant_cannot_download | Fixed |
| 2 | A removed user keeps access through an old session | The cookie holds only the user id. Every request reloads the user and checks is_active | test_deactivated_user_loses_access_immediately | Fixed |
| 3 | A viewer types an admin or upload URL directly | role_required checks the role on the server and logs the refusal | test_viewer_cannot_open_admin_page, test_viewer_cannot_upload | Fixed |
| 4 | A harmful, disguised or very large file is uploaded | Type list, 5 MB limit, the file's first bytes must match its type, random stored name | test_disguised_file_is_rejected | Partly. No virus scan |
| 5 | Someone edits or deletes audit log rows | The app has no route that changes the log. Database triggers refuse UPDATE and DELETE | test_audit_log_cannot_be_changed | Partly. Anyone with the database file could drop the triggers |
| 6 | Someone guesses a file's direct URL | Files are in uploads/, outside public folders, with random names. They are served only through the checked download route | By hand | Fixed |
| 7 | Passwords stolen from the database | Passwords are stored as hashes | By hand | Fixed |
| 8 | SQL injection | All queries use ? placeholders | Code review | Fixed |
| 9 | Script injection (XSS) through user text | Pages use Jinja templates, which escape text | Code review | Fixed |
| 10 | Guessing passwords again and again | Failed logins are logged. No lockout or rate limit yet | None | Planned |
| 11 | Forged requests from another website (CSRF) | Cookies use SameSite=Lax. No CSRF tokens yet | None | Partly |
| 12 | The default secret key is used on the live site | I must set SECRET_KEY on the host | None | Planned |
| 13 | Debug mode left on in production | Debug turns on only if FLASK_DEBUG=1 | Code review | Fixed |
| 14 | Refused attempts by logged-out visitors are not recorded | login_required and role_required log them | By hand: opened /admin logged out and saw the row | Fixed |
| 15 | A user with only read access deletes or shares a document | Delete and share are owner-only in can_access() | test_reader_cannot_delete_document, test_non_owner_cannot_share_document | Fixed |
| 16 | Taking access away does not work | The grant row is deleted and the database is checked on every request | test_grant_gives_access_and_revoke_removes_it | Fixed |
| 17 | Refused downloads missing from the audit log | Refusals are logged under the action name download | test_denied_download_is_in_audit_log | Fixed |
| 18 | Deleted documents stay on disk | Delete only hides the document. The stored file stays | None | Accepted for now, because recovery may be needed. Retention is not built |
| 19 | The edit permission does nothing | No route uses it yet | None | Planned |
| 20 | The admin page shows only 50 rows and mixes everything | No filter or paging yet | None | Planned |