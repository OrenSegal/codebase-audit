# Security and privacy

Fires: always

Leading word: **attacker with the binary**. They have your client, your network traffic and an account; walk STRIDE (spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege) across every entry point. For mobile apps, the OWASP MASVS categories (storage, crypto, auth, network, platform, code, resilience, privacy) are the checklist; for servers, the OWASP ASVS.

Artifact: an entry-point list (entry point → who can reach it → what it trusts → finding).

- **secrets**: Secrets committed to the repo, embedded in a client bundle, or in build logs. For each key: if it leaked today, how long to rotate it, and what breaks?
- **injection**: SQL, shell, HTML, template or path strings built from input; `eval`; deserializing untrusted data; model output used as code, SQL, HTML or a URL.
- **crypto**: Weak or homemade crypto: MD5 or SHA-1 for passwords or signatures, fast or unsalted password hashes (use bcrypt, scrypt or argon2), `Math.random` or `random` for tokens, hardcoded keys or IVs, ECB mode, secrets compared with `==` instead of a constant-time comparison.
- **local-storage** (when a client stores data on the device or in the browser): Tokens, passwords or personal data in plain local storage (`UserDefaults`, `SharedPreferences`, `localStorage`, `AsyncStorage`, unencrypted files) instead of the platform keystore or keychain.
- **transport**: Cleartext HTTP, disabled certificate checks, ATS or cleartext exceptions, secrets in URLs or query strings.
- **entry-points** (when the app has deep links, intents, URL schemes, webviews, push or uploads): Deep links, universal links, intents, URL schemes, push payloads, webviews with JavaScript bridges, file uploads and share extensions. Each one takes outside input: is it validated and authorized?
- **sessions** (when there is authentication): Every server route checks auth; tokens expire and refresh; logout and password change invalidate other sessions; nothing trusts a client-sent role or user id.
- **confused-deputy** (when a server fetches URLs or acts with elevated keys): The server acts with its own privileges on user-controlled input: SSRF via fetched URLs, service-role keys used on user requests, signed URLs for paths the user chose.
- **abuse** (when an endpoint is reachable from the internet): A bot calls each endpoint 10,000 times a minute. Rate limits, account enumeration through error messages, signup and free-tier farming, costly endpoints with no quota, and request bodies, uploads, pagination sizes and decompressed payloads with no size cap.
- **web-surface** (when the project serves web pages, or a browser calls its API): CORS that reflects any origin or pairs `*` with credentials; state-changing requests on cookie auth with no CSRF defense or `SameSite`; session cookies without `HttpOnly` and `Secure`; no `Content-Security-Policy`, `Strict-Transport-Security` or frame protection on pages that render user content; open redirects through a `next` or `returnTo` parameter; user-controlled file names served inline.
- **mass-assignment** (when a server writes request bodies into stored records): A whole body spread into a create or update (`...req.body`, `**request.json`, `permit!`, an ORM `update(body)`), so a user sets `role`, `owner_id`, `plan`, `verified` or `balance` by adding a field. Each writable field should come from an allowlist.
- **audit-trail** (when users or staff can take privileged, destructive or money actions): Repudiation in STRIDE: for each such action (role change, refund, deletion, export, impersonation, config change), is there an append-only record of who did it, when, and to what, that the actor cannot edit or delete, and that leaves secrets and personal data out?
- **supply-chain**: Known-vulnerable versions (the output of osv-scanner, npm audit, pip-audit, govulncheck or cargo audit from the tools step), unpinned or wildcard versions, missing lockfiles, install scripts from unknown packages, abandoned dependencies, licenses incompatible with distribution.
- **privacy-flows**: Trace personal data to every place it goes (analytics, crash reporting, logs, third-party SDKs, model providers). Is each flow needed, consented, and declared (privacy manifest, data-safety form, privacy policy)?

Done: every entry point is in the list with what it trusts, and every secret has a rotation answer.
