import os
from functools import wraps

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from db import close_db, get_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
app.teardown_appcontext(close_db)


def log_event(action, outcome, document_id=None, detail="", user_id=None):
    if user_id is None and g.get("user") is not None:
        user_id = g.user["id"]
    db = get_db()
    db.execute(
        "INSERT INTO audit_log (user_id, action, document_id, outcome, detail, ip) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, action, document_id, outcome, detail, request.remote_addr),
    )
    db.commit()


@app.before_request
def load_user():
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, role FROM users WHERE id = ? AND is_active = 1",
            (user_id,),
        ).fetchone()
        if g.user is None:
            session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            log_event("route_access", "denied", detail="not logged in: " + request.path)
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                log_event("route_access", "denied", detail="not logged in: " + request.path)
                return redirect(url_for("login"))
            if g.user["role"] not in roles:
                log_event("route_access", "denied", detail=request.path)
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


@app.route("/")
def home():
    if g.user is None:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, password_hash FROM users WHERE username = ? AND is_active = 1",
            (username,),
        ).fetchone()
        if user is not None and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            log_event("login", "allowed", user_id=user["id"])
            return redirect(url_for("dashboard"))
        log_event("login", "denied", detail="username tried: " + username[:50])
        return render_template("login.html", error="Wrong username or password."), 401
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    log_event("logout", "allowed")
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=g.user)


@app.route("/admin")
@role_required("admin")
def admin():
    rows = get_db().execute(
        "SELECT a.ts, u.username, a.action, a.document_id, a.outcome, a.detail "
        "FROM audit_log a LEFT JOIN users u ON u.id = a.user_id "
        "ORDER BY a.id DESC LIMIT 50"
    ).fetchall()
    return render_template("admin.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")