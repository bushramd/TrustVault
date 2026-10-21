# TrustVault

Secure document sharing with an audit trail.
Built for the Snovasys Fresher Hiring Challenge 2026.

## What works so far
- Login and logout with hashed passwords
- Three roles: admin, owner, viewer
- The server checks the user in the database on every request
- An audit log that records logins, failed logins and refused attempts
- An admin page that shows the latest activity

## What is not built yet
- Document upload, download, sharing and revoking
- Search
- Automated tests
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

## Demo accounts (demo use only)
| Role | Username | Password |
|------|----------|----------|
| Admin | admin1 | AdminDemo#2026 |
| Owner | owner1 | OwnerOneDemo#2026 |
| Owner | owner2 | OwnerTwoDemo#2026 |
| Viewer | viewer1 | ViewerDemo#2026 |

## Files
- app.py: routes, login, roles, audit logging
- db.py: database connection
- schema.sql: the four tables
- seed.py: creates the demo users
- THREATS.md: how this could be attacked and what I did
- PROMPTS.md: where AI was wrong and how I fixed it