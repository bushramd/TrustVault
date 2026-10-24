# TrustVault

Secure document sharing with an audit trail.
Built for the Snovasys Fresher Hiring Challenge 2026.

Live site: https://trustvault-bushra.onrender.com

## What works
- Login and logout. Passwords are stored as hashes.
- Three roles: admin, owner, viewer.
- Owners upload documents. Uploads are checked for type, size and real content.
- Owners give other users read or edit access to a document, and take it back.
- One function, can_access(), decides who may use a document. Every document route calls it.
- Taking access away works on the very next request, because the database is checked every time.
- Files are stored outside any public folder under random names. They are served only after a check.
- Search by name, owner, category and date. Search only looks inside documents the user may see.
- The audit log records logins, failed logins, uploads, downloads, deletes, grants, revokes and refused attempts.
- The app has no route that changes or deletes audit rows, and database triggers refuse changes.
- An admin page shows the latest 50 audit entries. Allowed and denied are colour coded.
- 17 automated tests cover access control, search and the audit log.
- Deployed on Render over HTTPS.
- A second admin page shows permission changes (grants and revokes) and refused attempts.
- An admin page that shows only permission changes.

## What is not built yet
- Editing a document. The edit permission can be granted, but no route uses it yet.
- An admin page that shows only permission changes.
- Login rate limiting and CSRF tokens.

## Limits you should know about
- The live site runs on a free host. When it restarts, the database and uploaded files are erased. The four demo accounts are created again at startup.
- After some time with no visits, the free host sleeps. The first page load can take about a minute.
- The demo passwords below are public on purpose, so the judges can log in. A real system would never do this.

## Try it
1. Open the live site and log in as owner1. Upload a small file.
2. Log in as viewer1 and try to open it. It is refused and the attempt is logged.
3. As owner1, share it with viewer1. Now viewer1 can download it.
4. Revoke it. viewer1 is refused again straight away.
5. Log in as admin1 and open the admin page to see every step in the audit log.

## Demo accounts (demo use only)
| Role | Username | Password |
|------|----------|----------|
| Admin | admin1 | AdminDemo#2026 |
| Owner | owner1 | OwnerOneDemo#2026 |
| Owner | owner2 | OwnerTwoDemo#2026 |
| Viewer | viewer1 | ViewerDemo#2026 |

## Run it on your computer
1. python -m venv venv
2. venv\Scripts\activate
3. pip install -r requirements.txt
4. python seed.py
5. python app.py
6. Open http://127.0.0.1:5000

## Run the tests
python -m pytest -v

## My permission model
- An owner can read, download, share, revoke and delete their own documents.
- Anyone else needs a grant. A grant is a row that says "this user may read (or edit) this document".
- Delete and share are owner-only. A grant never gives them.
- A user without access gets a 404, so they cannot tell if a document exists. The attempt is logged.

## Files
- app.py: routes, login, roles, can_access(), search, audit logging
- db.py: database connection
- schema.sql: the four tables and the audit log triggers
- seed.py: creates the demo users
- templates/ and static/: pages and styling
- tests/: automated tests
- THREATS.md: how this could be attacked and what I did
- PROMPTS.md: where AI was wrong and how I fixed it