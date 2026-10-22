# TrustVault

Secure document sharing with an audit trail.
Built for the Snovasys Fresher Hiring Challenge 2026.

## What works
- Login and logout. Passwords are stored as hashes.
- Three roles: admin, owner, viewer.
- Owners upload documents. Uploads are checked for type, size and real content.
- Owners give other users read or edit access to a document, and take it back.
- One function, can_access(), decides who may use a document. Every document route calls it.
- Taking access away works on the very next request, because the database is checked every time.
- Files are stored outside any public folder under random names and are served only after a check.
- The audit log records logins, failed logins, uploads, downloads, deletes, grants, revokes and refused attempts.
- The audit log cannot be updated or deleted through the app, and database triggers refuse changes.
- An admin page shows the latest 50 audit entries.
- 13 automated tests cover access control and the audit log.

## What is not built yet
- Search by name, owner, category and date
- Editing a document. The edit permission can be granted but no route uses it yet.
- A full admin view of permission changes
- Login rate limiting and CSRF tokens
- Live deployment

## Run it on your computer
1. Create and activate a virtual environment:
   python -m venv venv
   venv\Scripts\activate
2. Install the libraries:
   pip install -r requirements.txt
3. Create the database and demo users:
   python seed.py
4. Start the app:
   python app.py
5. Open http://127.0.0.1:5000

## Run the tests
python -m pytest -v

## Demo accounts (demo use only)
| Role | Username | Password |
|------|----------|----------|
| Admin | admin1 | AdminDemo#2026 |
| Owner | owner1 | OwnerOneDemo#2026 |
| Owner | owner2 | OwnerTwoDemo#2026 |
| Viewer | viewer1 | ViewerDemo#2026 |

## My permission model
- An owner can do everything with their own documents: read, download, share, revoke and delete.
- Anyone else needs a grant. A grant is a row that says "this user may read (or edit) this document".
- Delete and share are owner-only. A grant never gives them.
- Anyone without access gets a 404, so they cannot tell whether a document exists. The attempt is logged.

## Files
- app.py: routes, login, roles, can_access(), audit logging
- db.py: database connection
- schema.sql: the four tables and the audit log triggers
- seed.py: creates the demo users
- templates/: the pages
- tests/: automated tests
- THREATS.md: how this could be attacked and what I did
- PROMPTS.md: where AI was wrong and how I fixed it