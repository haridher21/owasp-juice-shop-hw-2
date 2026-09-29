# owasp-juice-shop-hw-2

## Problem Statement

In this assignment, you'll explore OWASP Juice Shop — a deliberately vulnerable web application — to understand web security threats and how to defend against them. You'll work through three parts: designing a secure feature, building a basic front-end form, and exploiting a vulnerability.

### Part 1: Secure Feature Design (~100 words)

OWASP Juice Shop is full of exploitable vulnerabilities. Your task is to design a secure user registration system for Juice Shop that prevents common attacks like SQL Injection, Cross-Site Scripting (XSS), and authentication bypass.

Specifically:

Identify three vulnerabilities or possible exploit scenarios in Juice Shop.
Propose security measures to mitigate each one. Think about how you could exploit the site and how those exploits can be prevented.
Explain how your proposed measures prevent the attacks.
Provide an example of secure password handling (e.g., hashing with bcrypt).
Note: You are expected to actually identify and exploit vulnerabilities on the Juice Shop site, then propose mitigations based on what you found. Write up your exploitations, learnings, and mitigations in ~100 words (not a hard limit, but stay close).

### Part 2: Implement a Simple Front-End Form (~100 words)

Create a basic HTML + JavaScript login form that mimics Juice Shop's login page. Your form should include:

Email and password input fields
Client-side validation to prevent empty submissions
A JavaScript function that checks the email contains "@" and the password is at least 8 characters
Both client-side and server-side validations
Provide your HTML/JavaScript code via a public GitHub repo. As good developer practice, your README.md should clearly explain what the project does and how to run it.

Note: In ~100 words, write up what you implemented and how. Include your GitHub repo link directly in your submission document. Keep the repo public.

### Part 3: Exploit a Vulnerability in Your Own Form (~100 words)

Now try to break the form you just built. Attempt an SQL Injection or XSS attack on your own login page.

Document the exact steps you took to execute the attack.
Provide a screenshot or description showing whether the attack succeeded (e.g., executing JavaScript in the browser, accessing admin credentials, etc.).
Suggest one fix for the vulnerability.
Note: If you can't exploit it — that's a good sign; it means your security practices are solid. Either way, paste screenshots and explain what happened. If the attack succeeded, describe what fix you'd apply. Write up your learnings in ~100 words.

### Submission

Submit a single PDF containing:

Part 1 — Secure feature design write-up
Part 2 — Implementation write-up + your GitHub repo link(public, with a proper README)
Part 3 — Exploitation write-up with screenshots
