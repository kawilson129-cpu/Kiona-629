# Cryptography Lab 1 — Hashing & Integrity

Part of **Cryptography 1, Rubric Item #1** for DeRexi: Policy Pilot.

A classroom demonstration of three everyday security tools: password
hashing, HMAC message authentication, and file integrity verification.
Everything is illustrative — no real credentials, API keys, or sensitive
data are used anywhere in this lab.

## What it demonstrates

| Section | Concept |
|---|---|
| `=== PASSWORD HASHING ===` | PBKDF2-HMAC-SHA256 with a random per-password salt |
| `=== HMAC MESSAGE INTEGRITY ===` | HMAC-SHA256 proving a policy message is intact and genuine |
| `=== FILE INTEGRITY ===` | SHA-256 detecting a change to a policy file |

## Requirements

Python **3.9+** with the **standard library only** — `hashlib`, `hmac`,
`secrets`, `pathlib`. Nothing to install, and the DeRexi virtual
environment is optional.

## Run it

From the `derexi-policy-pilot/` project folder:

```bash
python security-labs/cryptography/hashing_integrity.py
```

Or with the project virtual environment (macOS/Linux):

```bash
.venv/bin/python security-labs/cryptography/hashing_integrity.py
```

On Windows:

```powershell
.venv\Scripts\python.exe security-labs\cryptography\hashing_integrity.py
```

Each run writes `sample_policy.txt` next to the script, verifies it,
temporarily modifies it, and **restores the original contents** — so the
lab is safe to re-run as many times as you like.

## What to look for in the output

- **Password hashing** — a random salt and the resulting hash are printed
  in hex. The *same* password with a *different* salt yields a different
  hash (this is what defeats precomputed-hash/rainbow-table attacks), and
  a login-style check passes for the correct password but fails for a
  wrong one.
- **HMAC** — the original message verifies with `PASS`; a tampered
  version reports `CHANGE DETECTED` even though an attacker could
  recompute a plain hash. They cannot forge a valid tag without the
  secret key.
- **File integrity** — the unchanged file reports `PASS`; after a single
  word is changed the hash no longer matches and reports
  `CHANGE DETECTED`; the file is then restored and verified.

## Key ideas explained

- **Hashing is one-way.** A digest cannot be reversed back into the
  original input, so systems store hashes instead of passwords.
- **A salt defeats precomputed hash attacks.** A random value mixed in
  before hashing gives each password a unique digest, even when two users
  choose the same password.
- **HMAC provides integrity *plus* authenticity.** It combines the message
  with a secret key, so you can tell both that the message is unaltered
  and that it came from someone holding the key.
- **SHA-256 file hashing detects change.** Save a fingerprint of an
  approved file, re-hash it later, and a mismatch means the file was
  modified. Note that a plain hash does not prove *who* changed it — for
  that you also need to sign or HMAC the digest.

## Notes

- PBKDF2 iterations are set to `100,000` so the lab runs instantly on a
  classroom laptop. Current production guidance for
  PBKDF2-HMAC-SHA256 is **600,000+** — a real system should use the
  higher value. The script flags this in its comments.
- The demo secret key is a fake string hardcoded for illustration. In a
  real system a secret would live in a secrets manager, never in source.
- This lab is deliberately kept in `security-labs/` and is **separate
  from production DeRexi authentication** — it demonstrates the concepts
  only.
