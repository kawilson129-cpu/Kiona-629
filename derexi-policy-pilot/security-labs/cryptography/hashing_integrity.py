"""
DeRexi: Policy Pilot -- Cryptography Lab 1
==========================================

A beginner-friendly demonstration of three everyday security tools:

    1. Password hashing (PBKDF2-HMAC + SHA-256)
    2. HMAC message integrity (HMAC + SHA-256)
    3. File integrity verification (SHA-256)

WHY A HASH FUNCTION?
--------------------
A hash function turns any input into a short, fixed-length fingerprint
called a *digest*. Two useful properties make hashing the foundation of
this lab:

  * ONE-WAY: you cannot work backwards from the digest to recover the
    original input. Trying every possible input is computationally
    hopeless for a good hash function. This is why we store password
    *hashes* instead of passwords.
  * DETERMINISTIC: the same input always produces the same digest. That
    is what lets us check "has this file changed?" (part 3).

CLASSROOM DEMONSTRATION ONLY
----------------------------
Everything below uses invented demo values. There are no real passwords,
real API keys, or real bank secrets anywhere in this file. This lab is
kept separate from the DeRexi backend on purpose: it demonstrates the
concepts and does not touch production authentication.

Run it with:

    python hashing_integrity.py

Only the Python standard library is used (hashlib, hmac, secrets).
"""

import hashlib
import hmac
import secrets
from pathlib import Path

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def to_hex(value: bytes) -> str:
    """Return a digest/bytes as readable lowercase hexadecimal."""
    return value.hex()


# ---------------------------------------------------------------------------
# 1. PASSWORD HASHING
# ---------------------------------------------------------------------------


def demonstrate_password_hashing() -> None:
    """
    Show how a password should be protected: hashed with PBKDF2-HMAC-SHA256.

    Why not store the plaintext password?
    -------------------------------------
    If a system stores passwords in plaintext, then anyone who gains read
    access to the database (a stolen backup, a careless admin, a SQL
    injection bug) immediately owns every real user's password. Worse,
    people reuse passwords, so one breach would expose their email and
    banking logins too.

    Hashing avoids that: the server keeps only a fingerprint that nobody
    can reverse. Even if the database leaks, the attacker sees hashes
    instead of usable passwords.

    Why add a SALT?
    ---------------
    A *salt* is a random value mixed into the hash before it is computed.
    If two users both choose "Sunshine123!", a database with no salt
    would store the exact same hash for both -- and the attacker can
    precompute hashes of the most common passwords in advance (a
    "rainbow table") and then just look up the answers.

    Because every user gets a DIFFERENT random salt, their hashes are all
    different even when their passwords match. That defeats precomputed
    hash attacks completely.

    PBKDF2 also repeats the hashing step many thousands of times on
    purpose. That makes each guess deliberately slow, so brute-forcing
    becomes expensive for an attacker while staying fast for the user.
    """

    # A random salt. secrets.token_bytes uses the operating system's secure
    # random number generator, so the salt is unpredictable to others.
    salt = secrets.token_bytes(16)

    # Iteration count: how many times PBKDF2 re-hashes internally.
    # Modern guidance is 600,000+ for PBKDF2-HMAC-SHA256. We use a smaller
    # number here so the lab runs instantly on a classroom laptop; the real
    # production value would be much higher.
    iterations = 100_000

    # A clearly fake demo password. NEVER put a real password in a script.
    fake_password = b"DeRexi-Demo-Password-2026"

    # derived_key = PBKDF2-HMAC-SHA256(password, salt, iterations)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",  # hash algorithm
        fake_password,  # the password (never logged or stored)
        salt,  # the random per-user salt
        iterations,  # how many rounds
        dklen=32,  # output length in bytes (32 bytes = 256 bits)
    )

    # Show that the same password with a DIFFERENT salt produces a
    # completely different hash -- this is what defeats rainbow tables.
    different_salt = secrets.token_bytes(16)
    different_hash = hashlib.pbkdf2_hmac(
        "sha256", fake_password, different_salt, iterations, dklen=32
    )

    print("Demonstration password (fake):", fake_password.decode())
    print()
    print("Random salt (hex)        :", to_hex(salt))
    print("Hash algorithm           : PBKDF2-HMAC-SHA256")
    print("Iterations               :", iterations)
    print("Derived key length       :", len(derived_key), "bytes")
    print()
    print("PASSWORD HASH (hex)      :", to_hex(derived_key))
    print()
    print("Same password, NEW salt  :", to_hex(different_hash))
    print("Hashes match?            :", to_hex(derived_key) == to_hex(different_hash))
    print("-> Even with the SAME password, a different salt produces a")
    print("   different hash. That is why each password needs its own salt.")
    print()

    # How login verification actually works in a real system:
    # the stored salt + hash are kept, the typed password is re-hashed with
    # that same salt, and the two digests are compared.
    entered_password = fake_password  # pretend the user typed the right one
    check_hash = hashlib.pbkdf2_hmac(
        "sha256", entered_password, salt, iterations, dklen=32
    )
    login_ok = hmac.compare_digest(to_hex(check_hash), to_hex(derived_key))
    print("Login check (correct password):", "PASS" if login_ok else "FAIL")

    wrong_password = b"wrong-guess"
    bad_hash = hashlib.pbkdf2_hmac("sha256", wrong_password, salt, iterations, dklen=32)
    login_bad = hmac.compare_digest(to_hex(bad_hash), to_hex(derived_key))
    print("Login check (wrong password)  :", "PASS" if login_bad else "FAIL")
    print("-> The server never sees or stores the real password; it only")
    print("   recomputes the hash and compares.")
    print()


# ---------------------------------------------------------------------------
# 2. HMAC MESSAGE INTEGRITY
# ---------------------------------------------------------------------------


def demonstrate_hmac() -> None:
    """
    Show how HMAC proves a message is both intact and genuine.

    A plain hash only proves the message has not changed -- but anyone
    could change the message AND recompute the hash, and you would have no
    way to tell. That is a weakness, not security.

    HMAC (Hash-based Message Authentication Code) fixes this by hashing
    the message together with a SECRET KEY that only the sender and
    receiver know. To forge a valid-looking message, an attacker would
    need the secret key.

    So HMAC gives us two guarantees at once:
      * INTEGRITY  -- the message was not altered in transit.
      * AUTHENTICITY -- the message really came from someone holding the key.

    In DeRexi terms: this is how a policy notice could be signed so the
    bank can be sure nobody tampered with it in transit or emailed a fake.
    """

    # A fictional DeRexi policy message.
    policy_message = (
        "Aurum Capital Bank employees must report suspicious customer "
        "activity to the BSA/AML Compliance Officer."
    )

    # A clearly fake demo secret key. In a real system this key would be
    # kept in a secrets manager, never hard-coded in source code.
    fake_secret_key = b"DeRexi-Demo-HMAC-Key-2026"

    # Compute the HMAC tag: SHA-256 of (key + message), in one standard step.
    tag = hmac.new(fake_secret_key, policy_message.encode(), hashlib.sha256)

    print("Policy message:", policy_message)
    print()
    print("Demo secret key (fake):", fake_secret_key.decode())
    print("HMAC algorithm       : HMAC-SHA256")
    print()
    print("HMAC TAG (hex)       :", tag.hexdigest())
    print()

    # --- Verify the ORIGINAL, untouched message ---------------------------
    # hmac.compare_digest is the correct way to compare MACs. It is
    # constant-time, so an attacker cannot learn the right value by
    # timing how long a comparison takes.
    original_tag = hmac.new(fake_secret_key, policy_message.encode(), hashlib.sha256).digest()
    original_verified = hmac.compare_digest(tag.hexdigest(), original_tag.hex())

    if original_verified:
        print("Original message verification: PASS")
    else:
        print("Original message verification: FAIL")
    print("-> The message and its tag match, so nothing was altered.")
    print()

    # --- Verify a TAMPERED message ---------------------------------------
    # Change one word ("must report" -> "may ignore") to simulate an
    # attacker editing the message in transit.
    tampered_message = (
        "Aurum Capital Bank employees may ignore suspicious customer "
        "activity to the BSA/AML Compliance Officer."
    )
    tampered_tag = hmac.new(fake_secret_key, tampered_message.encode(), hashlib.sha256).digest()
    tampered_verified = hmac.compare_digest(tampered_tag.hex(), tag.hexdigest())

    print("Modified message:", tampered_message)
    print()

    if not tampered_verified:
        print("Modified message verification: CHANGE DETECTED")
    else:
        print("Modified message verification: VERIFIED (unexpected!)")
    print("-> Even though the attacker recomputed a hash, they could not")
    print("   produce a valid HMAC tag without the secret key.")
    print()


# ---------------------------------------------------------------------------
# 3. FILE INTEGRITY
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file as hexadecimal."""
    # Read in chunks so this works on files of any size without loading the
    # whole file into memory at once.
    file_hash = hashlib.sha256()
    with open(path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(64 * 1024), b""):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def demonstrate_file_integrity() -> None:
    """
    Show how SHA-256 hashing detects whether a file has changed.

    Policies live in files, and an attacker who can edit a policy file
    could change the rules everyone must follow. Hashing the file gives
    you a fingerprint: save the hash today, re-hash the file later, and
    if the two digests differ, the file was modified.

    This detects ACCIDENTAL or UNAUTHORIZED changes. Note the difference
    from HMAC above: a plain file hash can be recomputed by anyone, so for
    proof of *who* made the change you would also need to sign the hash
    (or HMAC it) with a secret key.
    """

    script_dir = Path(__file__).resolve().parent
    policy_file = script_dir / "sample_policy.txt"

    # The original, approved fictional policy text.
    original_contents = (
        "Aurum Capital Bank - Sample Policy Document\n"
        "==========================================\n"
        "\n"
        "Policy ID: ACB-SAMPLE-001\n"
        "Owner: BSA/AML Compliance Officer\n"
        "\n"
        "1. Employees must escalate any suspicious customer transaction to\n"
        "   the BSA/AML Compliance Officer within one business day.\n"
        "2. Suspicious activity must never be discussed with the customer.\n"
        "3. All escalations must be recorded in the compliance case log.\n"
    )

    # --- Step 1: create the sample policy file ---------------------------
    policy_file.write_text(original_contents, encoding="utf-8")
    print("Created sample file:", policy_file.name)
    print()

    # --- Step 2: hash the original file and SAVE that hash in memory ------
    # Saving the original hash first is what makes later comparison possible.
    original_file_hash = sha256_file(policy_file)
    print("ORIGINAL FILE HASH (saved in memory):")
    print(original_file_hash)
    print()

    # --- Step 3: verify the UNCHANGED file --------------------------------
    unchanged_hash = sha256_file(policy_file)

    if unchanged_hash == original_file_hash:
        print("Unchanged policy file: PASS")
    else:
        print("Unchanged policy file: FAIL")
    print("-> Recomputed hash matches the saved hash, so the file is intact.")
    print()

    # --- Step 4: tamper with the file, then hash it again ----------------
    # Simulate an attacker (or a careless edit) changing the policy text.
    tampered_contents = original_contents.replace(
        "within one business day", "within thirty business days"
    )
    policy_file.write_text(tampered_contents, encoding="utf-8")
    modified_file_hash = sha256_file(policy_file)

    print("File hash AFTER modification:")
    print(modified_file_hash)
    print()

    if modified_file_hash != original_file_hash:
        print("Modified policy file: CHANGE DETECTED")
    else:
        print("Modified policy file: NO CHANGE (unexpected!)")
    print("-> The hash no longer matches the saved original, so the change")
    print("   was caught. A single changed word changes the entire digest.")
    print()

    # --- Step 5: restore the original file contents -----------------------
    # Always put the sample file back so the lab is re-runnable.
    policy_file.write_text(original_contents, encoding="utf-8")
    restored_hash = sha256_file(policy_file)

    if restored_hash == original_file_hash:
        print("Sample file restored to original contents: PASS")
    else:
        print("Sample file restored to original contents: FAIL")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("DeRexi: Policy Pilot - Cryptography Lab 1")
    print("Classroom demonstration - no real credentials are used.")
    print()

    print("=== PASSWORD HASHING ===")
    demonstrate_password_hashing()
    print()

    print("=== HMAC MESSAGE INTEGRITY ===")
    demonstrate_hmac()
    print()

    print("=== FILE INTEGRITY ===")
    demonstrate_file_integrity()

    print("=== SUMMARY ===")
    print("Password hashing  : PBKDF2-HMAC-SHA256 with a random salt (one-way)")
    print("HMAC              : SHA-256 keyed tag proves integrity + authenticity")
    print("File integrity    : SHA-256 digest detects any change to a policy file")
    print()
    print("DeRexi cryptography lab completed.")


if __name__ == "__main__":
    main()
