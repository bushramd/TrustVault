## Entry 1 - 2026-10-20
- **What I asked:** An example route that takes a name from the URL.
- **What it produced:** A route that returned the name inside an f-string with no escaping.
- **What was wrong:** Whatever the user types goes straight into the page, so a script could run in the browser (XSS).
- **What I did instead:** Deleted the route. I use Jinja templates, which escape text. Commit: <paste link>

## Entry 2 - 2026-10-21
- **What I asked:** A role check that also records refused attempts in the audit log.
- **What it produced:** role_required logged refusals only for logged-in users. A visitor who was not logged in was redirected without any record.
- **What was wrong:** The requirement says refused attempts must be recorded. Logged-out attempts were missing.
- **What I did instead:** Added log_event to both decorators for the not-logged-in case, and tested it by opening /admin while logged out. Commit: <paste link>

## Entry 3 - 2026-10-21
- **What I asked:** A starter Flask app.
- **What it produced:** app.run(debug=True) at the bottom.
- **What was wrong:** Debug mode shows an interactive debugger that can run code. It must never be on in production.
- **What I did instead:** Debug mode now turns on only if FLASK_DEBUG=1. Commit: <paste link>