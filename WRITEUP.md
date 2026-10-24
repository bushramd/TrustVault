# WRITEUP.md

## What I built
TrustVault is a document sharing app. Owners upload documents and give other users read or edit access, and take it back. Every important action is written to an audit log, including refused attempts. Live site: https://trustvault-bushra.onrender.com

## My permission model
One function, can_access(), decides who may read, edit, delete or share a document. The owner can do everything. Anyone else needs a grant, and delete and share are never given by a grant. Every document route calls it, and the database is checked on every request, so taking access away works straight away. A refused request returns 404.

## What I tested
23 automated tests cover access between users, revoke, disguised uploads, search, the audit log and login lockout. I also tried the live site in a private window.

## What I left out, and why
- CSRF tokens. They touch every form and I did not have time to test them well.
- Paging and filters on the admin pages.
- Virus scanning of uploads.
- Permanent storage. The free host erases data on restart, so the demo accounts are created again at startup.

## How I used AI
I used AI for most of the code and checked it myself. Things it got wrong are in PROMPTS.md, for example refused attempts that were logged under the wrong name, caught by a failing test.

## What is unfinished
The items above under "What I left out".