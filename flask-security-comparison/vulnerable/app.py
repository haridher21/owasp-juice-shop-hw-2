"""INTENTIONALLY VULNERABLE. Run only on 127.0.0.1 for an authorized lab."""

import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "users.db"

app = Flask(__name__)
app.config.update(SECRET_KEY="hard-coded-classroom-secret", DATABASE=str(DATABASE))


def get_db():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            password TEXT,
            role TEXT
        );
        INSERT INTO users (email, password, role)
        VALUES
          ('student@example.com', 'Password123!', 'customer'),
          ('admin@example.com', 'AdminPassword123!', 'admin');
        """
    )
    db.commit()
    db.close()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/login")
def login():
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    # VULNERABILITY 1 (SQL injection): user input is concatenated into SQL.
    query = f"SELECT id, email, role FROM users WHERE email = '{email}' AND password = '{password}'"
    try:
        user = get_db().execute(query).fetchone()
    except sqlite3.Error as error:
        return render_template("index.html", message=f"Database error: {error}"), 400

    if not user:
        # VULNERABILITY 2 (reflected XSS): the submitted email is echoed back and the
        # template renders it with `| safe`, so any HTML/JS in it runs in the browser.
        return render_template(
            "index.html", message=f"No account found for the email {email}"
        ), 401

    session["user_id"] = user["id"]
    session["email"] = user["email"]

    response = redirect(url_for("profile"))
    # VULNERABILITY 3 (broken access control): the role is stored in a plain, client
    # readable cookie and trusted on later requests. The browser can edit it freely.
    response.set_cookie("role", user["role"])
    return response


@app.get("/profile")
def profile():
    return render_template(
        "profile.html", email=session.get("email"), role=request.cookies.get("role")
    )


@app.get("/admin")
def admin():
    # VULNERABILITY 3: access is decided by the attacker-controlled `role` cookie.
    if request.cookies.get("role") != "admin":
        return render_template("index.html", message="Access denied: admins only."), 403
    return render_template("admin.html")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=False)
