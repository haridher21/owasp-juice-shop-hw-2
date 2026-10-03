#  OWASP Juice Shop - Assignment 2B

Two small Flask /JS applications demonstrate the same three threats in opposite ways:

- `vulnerable/` intentionally contains SQL injection, reflected XSS, and an authentication/authorization bypass.
- `secure/` prevents those flaws with parameterized queries, bcrypt, escaped output, Content Security Policy, trusted sessions, and server-side role checks.

**Safety:** Run the vulnerable version only on `127.0.0.1` in an isolated classroom environment. Never deploy it or test techniques against systems without explicit permission.

## Setup

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
```

## Run the vulnerable version

```bash
python vulnerable/app.py
```

Open <http://127.0.0.1:5001>.

## Run the secure version

In another terminal:

```bash
python secure/app.py
```

Open <http://127.0.0.1:5002>.

## Authorized comparison tests

All three attacks are driven from the login form or the browser — there are no artificial widgets. Run each against the vulnerable app (`:5001`) and then the secure app (`:5002`).

| Scenario | What you enter | Vulnerable result | Secure result |
|---|---|---|---|
| SQL injection | Email: `' OR '1'='1' --@`, password: `anything8` | Logs in as the first account | Invalid login; no profile access |
| Reflected XSS | Email: `<script>alert(1)</script>@a.com`, password: `wrongpass` | An `alert(1)` box pops — your script ran | Payload shows as plain text; no box |
| Broken access control | Log in as the student, then change the `role` cookie to `admin` (see below) | Admin dashboard opens | HTTP 403 Forbidden |

### Notes on running each test

- **SQL injection:** the payload `' OR '1'='1' --@` contains an `@`, so the client-side JavaScript validation lets it through; the server then falls over because it builds the query by string concatenation. This shows why client validation is not a security control.
- **Reflected XSS:** the payload avoids single quotes on purpose. In this app the email is *also* fed into the SQL query, so `alert('XSS')` would break the SQL string before it ever reaches the page — `alert(1)` sidesteps that.
- **Broken access control (cookie tampering):** the vulnerable app stores your role in a plain browser cookie and trusts it. To forge it:
  1. Log in as `student@example.com` / `Password123!`.
  2. Open DevTools (press **F12**, or right-click the page → **Inspect**).
  3. Go to the **Application** tab (in Firefox: **Storage**) → **Cookies** → `http://127.0.0.1:5001` in the left sidebar.
  4. Find the `role` cookie, double-click its **Value** (`customer`), change it to `admin`, press Enter.
  5. Visit <http://127.0.0.1:5001/admin> — the dashboard opens. On the secure app the same steps give 403, because it re-reads your role from the database and ignores the cookie.


## Demo accounts

| Role | Email | Password |
|---|---|---|
| Customer | `student@example.com` | `Password123!` |
| Admin | `admin@example.com` | `AdminPassword123!` |

The vulnerable app stores these passwords as plaintext for demonstration. The secure app stores bcrypt hashes. These credentials are classroom-only.

## Code locations

- SQL injection flaw: `vulnerable/app.py`, `login()` (string-concatenated query)
- SQL injection defense: `secure/app.py`, `login()` (parameterized query + bcrypt)
- XSS flaw: `vulnerable/app.py`, `login()` failure message + `templates/index.html` (`{{ message | safe }}`)
- XSS defense: `secure/templates/index.html` (`{{ message }}`, Jinja auto-escaping) + CSP in `secure/app.py`
- Access-control flaw: `vulnerable/app.py`, `admin()` (trusts the `role` cookie)
- Access-control defense: `secure/app.py`, `role_required()` (role loaded from the DB per request)
