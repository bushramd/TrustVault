# THREATS.md

Status words: Fixed = done and tested by hand. Partly = some protection, a gap remains.
Planned = not done yet. Accepted = I know about it and chose to leave it.

| # | Threat | What I did | Status |
|---|--------|-----------|--------|
| 1 | A user changes the number in the URL to open someone else's document | Will use one function, can_access(), on every document route | Planned |
| 2 | A removed user keeps access through an old session | The cookie holds only the user id. Every request reloads the user from the database and checks is_active | Fixed |
| 3 | A viewer types an admin URL directly | role_required checks the role on the server and logs the refusal | Fixed (by hand), automated test planned |
| 4 | A harmful or very large file is uploaded | Will limit type and size and rename files | Planned |
| 5 | Someone edits or deletes audit log rows | Database triggers refuse UPDATE and DELETE on audit_log. Someone with access to the database file could remove the triggers | Partly |
| 6 | Someone guesses a file's direct URL | Will store files outside public folders and serve them only after a check | Planned |
| 7 | Passwords stolen from the database | Passwords are stored as hashes, never as plain text | Fixed |
| 8 | SQL injection | All queries use ? placeholders | Fixed |
| 9 | Script injection (XSS) through user text | Pages use Jinja templates, which escape text automatically. I removed my early /hello route that returned raw text | Fixed |
| 10 | Guessing passwords again and again | Failed logins are logged. There is no lockout or rate limit yet | Planned |
| 11 | Forged requests from another website (CSRF) | Cookies use SameSite=Lax. No CSRF tokens yet | Partly |
| 12 | The default secret key is used on the live site | I must set SECRET_KEY on the host before deploying | Planned |
| 13 | Debug mode left on in production, which lets attackers run code | See the fix below | Planned |
| 14 | Refused attempts by people who are not logged in are not recorded | See the fix below | Planned |