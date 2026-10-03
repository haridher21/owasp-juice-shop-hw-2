"""Hardened comparison app for SQLi, XSS, and authentication/authorization bypass."""

import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "users.db"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", secrets.token_hex(32)),
    DATABASE=str(DATABASE),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
bcrypt = Bcrypt(app)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
                CHECK (role IN ('customer', 'admin'))
        );
        """
    )
    users = [
        ("student@example.com", "Password123!", "customer"),
        ("admin@example.com", "AdminPassword123!", "admin"),
    ]
    for email, password, role in users:
        password_hash = bcrypt.generate_password_hash(password, rounds=12).decode("utf-8")
        # DEFENSE 1: values are bound parameters, not SQL source code.
        db.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email, password_hash, role),
        )
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


def role_required(required_role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            # DEFENSE 3: load trusted role data from the database on every request.
            user = get_db().execute(
                "SELECT id, email, role FROM users WHERE id = ?",
                (session.get("user_id"),),
            ).fetchone()
            if not user or user["role"] != required_role:
                abort(403)
            g.current_user = user
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.after_request
def security_headers(response):
    # Supporting XSS defense; escaping remains the primary defense here.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/login")
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not email or "@" not in email or len(password) < 8:
        return render_template("index.html", message="Enter a valid email and password."), 400

    # DEFENSE 1: parameterized query keeps input separate from SQL syntax.
    user = get_db().execute(
        "SELECT id, email, password_hash, role FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    if not user or not bcrypt.check_password_hash(user["password_hash"], password):
        # DEFENSE 2 (XSS): the same email is echoed back, but the template renders it
        # with Jinja's automatic escaping, so HTML/JS arrives as inert text.
        return render_template(
            "index.html", message=f"No account found for the email {email}"
        ), 401

    session.clear()
    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.get("/profile")
@login_required
def profile():
    user = get_db().execute(
        "SELECT email, role FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    if not user:
        session.clear()
        return redirect(url_for("index"))
    return render_template("profile.html", email=user["email"], role=user["role"])


@app.get("/admin")
@role_required("admin")
def admin():
    return render_template("admin.html")


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="127.0.0.1", port=5002, debug=False)
