# THREATS.md

| # | Threat | What I did / plan | Status |
|---|--------|-------------------|--------|
| 1 | User changes document ID in the URL to read someone else's file | Check a grant on every request in one function | Planned |
| 2 | Removed user keeps access with an old session | Check the database on every request | Planned |
| 3 | Viewer calls an edit/delete URL directly | Server checks permission, not just hidden buttons | Planned |
| 4 | Harmful or oversized file uploaded | Limit type and size, rename files | Planned |
| 5 | Someone edits or deletes audit log rows | Insert-only logging, no edit/delete route | Planned |
| 6 | Guessing a file's direct URL | Store files outside public folders, serve after a check | Planned |