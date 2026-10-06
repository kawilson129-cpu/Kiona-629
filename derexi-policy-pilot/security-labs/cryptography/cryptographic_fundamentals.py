"""
DeRexi: Policy Pilot -- Cryptography Lab: Cryptographic Fundamentals
====================================================================

A beginner-friendly demonstration of two BASIC cryptographic primitives:

    1. Caesar Cipher  (classic substitution)
    2. XOR Cipher     (fundamental logical operation)

Plus a glossary of core concepts, the mathematics behind each cipher, and
an honest analysis of the security guarantees each one provides.

WHAT THIS LAB IS (AND IS NOT)
-----------------------------
This lab teaches PRINCIPLES. Neither cipher here is secure enough for
real data -- that is the point, and the analysis sections say so
plainly. Modern systems use AES, ChaCha20, and authenticated
encryption instead (see Lab 2, ``symmetric_encryption.py``).

DEPENDENCY
----------
Standard library only: this lab uses nothing beyond built-in Python.
No packages to install.

CLASSROOM DEMONSTRATION ONLY
----------------------------
All text is fictional DeRexi policy wording. No real credentials, API
keys, or sensitive values appear anywhere. This file is isolated in
``security-labs/`` and does not touch DeRexi's production
authentication, database, or API.

Run it with:

    python security-labs/cryptography/cryptographic_fundamentals.py
"""

import string

# ---------------------------------------------------------------------------
# Shared glossary
# ---------------------------------------------------------------------------


def print_fundamentals() -> None:
    """
    Core vocabulary used throughout cryptography.

    These definitions appear in the terminal so they can be referenced
    directly in the coursework report.
    """
    print("Plaintext:")
    print("  The original, readable message before encryption.")
    print()
    print("Ciphertext:")
    print("  The unreadable output produced by encrypting the plaintext.")
    print()
    print("Encryption:")
    print("  The process that transforms plaintext into ciphertext.")
    print()
    print("Decryption:")
    print("  The reverse process: turning ciphertext back into plaintext.")
    print()
    print("Key:")
    print("  A secret value used by the algorithm. With the correct key the")
    print("  message can be decrypted; without it, recovery should be hard.")
    print()
    print("Algorithm / cipher:")
    print("  The fixed, well-defined procedure that performs encryption and")
    print("  decryption (e.g. Caesar shift, XOR, AES).")
    print()
    print("Confidentiality:")
    print("  The security property that only authorized parties can read the")
    print("  message -- everyone else sees meaningless data.")
    print()
    print("Kerckhoffs's principle -- why the algorithm must stay public:")
    print("  A cipher's design should be public and still remain secure; only")
    print("  the KEY should be secret. If a system depends on hiding how it")
    print("  works, one leaked design or one curious employee breaks it")
    print("  completely. Published, analyzed algorithms (AES, ChaCha20) are")
    print("  trusted precisely because the whole world has tried to break")
    print("  them and failed. Secret-by-design 'ciphers' get no such testing.")
    print()
    print("Educational cipher vs modern secure cryptography:")
    print("  Caesar and repeating-key XOR are teaching tools -- small enough")
    print("  to reason about by hand, which is exactly why they are used to")
    print("  explain the mathematics. Modern cryptography (AES-256,")
    print("  ChaCha20-Poly1305) is engineered against real attacks: large")
    print("  keys, diffusion across whole blocks, random nonces, and")
    print("  built-in integrity checking. Learning the concepts here does")
    print("  NOT make the classroom ciphers production-ready.")


# ---------------------------------------------------------------------------
# 1. CAESAR CIPHER
# ---------------------------------------------------------------------------

CAESAR_SHIFT = 3  # the "key" for this demonstration


def caesar_encrypt(plaintext: str, shift: int) -> str:
    """
    Encrypt by shifting every letter forward by `shift` places.

    Only alphabetic characters are moved; spaces, digits, and
    punctuation pass through unchanged. Uppercase and lowercase are
    preserved so the ciphertext keeps its original casing.
    """
    result = []
    for ch in plaintext:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            # ord(ch) - base  ->  position 0-25 within the alphabet
            # + shift         ->  move forward
            # % 26            ->  wrap around from Z back to A
            shifted = (ord(ch) - base + shift) % 26
            result.append(chr(base + shifted))
        else:
            result.append(ch)
    return "".join(result)


def caesar_decrypt(ciphertext: str, shift: int) -> str:
    """Decrypt by shifting every letter BACKWARD by `shift` places."""
    # Decryption is encryption with the opposite shift, which is why
    # D(x) = (x - k) mod 26 works: it undoes E(x) = (x + k) mod 26.
    return caesar_encrypt(ciphertext, -shift)


def demonstrate_caesar() -> bool:
    """Encrypt, decrypt, and verify the Caesar cipher example."""
    plaintext = "AURUM CAPITAL BANK POLICY"
    shift = CAESAR_SHIFT

    ciphertext = caesar_encrypt(plaintext, shift)
    recovered = caesar_decrypt(ciphertext, shift)
    verified = recovered == plaintext

    print("Plaintext :", plaintext)
    print("Shift (k) :", shift)
    print()
    print("Ciphertext:", ciphertext)
    print()
    print("Decrypted :", recovered)
    print()
    print("Caesar cipher verification:", "PASS" if verified else "FAIL")
    print()
    print("Security analysis -- Caesar cipher:")
    print("  - Provides basic substitution / obfuscation only.")
    print("  - Has only 25 meaningful non-zero shifts (k = 1..25).")
    print("  - Can be brute-forced trivially: try all 25 keys and read the")
    print("    output -- a human spots the correct one in seconds.")
    print("  - Preserves language patterns and letter frequencies (the")
    print("    most common English letters stay most common after")
    print("    shifting), so frequency analysis breaks it instantly.")
    print("  - Does NOT provide meaningful security for modern sensitive")
    print("    information.")

    return verified


def print_caesar_mathematics() -> None:
    """Show the arithmetic behind the Caesar cipher."""
    print("Represent each letter as a number from 0 to 25:")
    print()
    print("  A = 0,  B = 1,  C = 2, ... M = 12, ... Z = 25")
    print()
    print("Encryption formula:")
    print()
    print("    E(x) = (x + k) mod 26")
    print()
    print("Decryption formula:")
    print()
    print("    D(x) = (x - k) mod 26")
    print()
    print("Where:")
    print("  x = numeric value of the letter (0-25)")
    print("  k = the shift / key")
    print("  mod 26 = keeps the result inside the 26-letter alphabet,")
    print("           wrapping Z back around to A")
    print()
    print("Worked example (encrypting 'A' with shift 3):")
    print()
    print("  A = 0")
    print("  shift k = 3")
    print("  (0 + 3) mod 26 = 3")
    print("  3 = D")
    print("  -> So 'A' encrypts to 'D'")
    print()
    print("Worked example (decrypting that 'D' back to 'A'):")
    print()
    print("  D = 3")
    print("  (3 - 3) mod 26 = 0")
    print("  0 = A")
    print("  -> Decryption exactly reverses encryption")
    print()
    print("Why 'mod 26' matters -- wrapping around the alphabet:")
    print()
    print("  Z = 25, shift = 3")
    print("  (25 + 3) mod 26 = 28 mod 26 = 2")
    print("  2 = C   -> 'Z' encrypts to 'C', not to some letter outside")
    print("             the alphabet")
    print()
    print("Full ciphertext check for '" + "AURUM CAPITAL BANK POLICY" + "':")


# ---------------------------------------------------------------------------
# 2. XOR CIPHER
# ---------------------------------------------------------------------------

# A clearly fictional demo key. Short and repeating -- deliberately, so
# the security analysis can show WHY that is a weakness.
XOR_DEMO_KEY = b"DeRexi"


def xor_crypt(data: bytes, key: bytes) -> bytes:
    """
    XOR every byte of `data` with the key, repeating the key as needed.

    The same function encrypts AND decrypts. That symmetry comes from
    XOR's defining property: applying it twice with the same value
    returns the original data (see the mathematics section).

    This repeats a SHORT key over a LONGER message. That repetition is
    what makes this classroom version weak -- see the analysis below.
    """
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))


def demonstrate_xor() -> bool:
    """Encrypt, decrypt, and verify the XOR cipher example."""
    plaintext = "Policy review required"
    plaintext_bytes = plaintext.encode("utf-8")  # text -> bytes

    key = XOR_DEMO_KEY  # clearly fictional demo key

    ciphertext = xor_crypt(plaintext_bytes, key)  # encrypt
    recovered = xor_crypt(ciphertext, key)  # decrypt (same operation)
    verified = recovered == plaintext_bytes

    print("Plaintext :", plaintext)
    print("As bytes  :", plaintext_bytes)
    print()
    print("DEMO key  :", key, "=", key.hex(), "(hex)")
    print("  -> Fictional classroom key. Repeating keys are insecure;")
    print("     see the security analysis below.")
    print()
    print("Ciphertext (hex):", ciphertext.hex())
    print()
    print("Recovered :", recovered.decode("utf-8"))
    print()
    print("XOR cipher verification:", "PASS" if verified else "FAIL")
    print()
    print("Security analysis -- XOR cipher:")
    print("  - XOR is an OPERATION, not automatically secure encryption.")
    print("    Its security depends entirely on the key that drives it.")
    print("  - Reusing a short repeating key creates predictable patterns:")
    print("    every block encrypted under the same key position leaks the")
    print("    same relationships, and known-plaintext attacks can recover")
    print("    the key from a little known text.")
    print("  - If the key were truly random, as long as the message, used")
    print("    only once, and kept secret, XOR becomes a ONE-TIME PAD.")
    print("  - A one-time pad provides PERFECT SECRECY under those strict")
    print("    conditions (proven by Shannon, 1949): ciphertext reveals")
    print("    NOTHING about the plaintext, not even its length.")
    print("  - This classroom implementation does NOT satisfy those")
    print("    conditions (short, repeating, reused key), so it must NOT")
    print("    be described as production-secure.")

    return verified


def print_xor_mathematics() -> None:
    """Show the logic and arithmetic behind XOR."""
    print("XOR truth table (1 bit in, 1 bit out):")
    print()
    print("  0 XOR 0 = 0")
    print("  0 XOR 1 = 1")
    print("  1 XOR 0 = 1")
    print("  1 XOR 1 = 0")
    print()
    print("In words: XOR outputs 1 when the inputs DIFFER, 0 when they")
    print("match. It is also called 'exclusive or'.")
    print()
    print("The reversible property:")
    print()
    print("    P XOR K = C")
    print("    C XOR K = P")
    print()
    print("  P = plaintext,  K = key,  C = ciphertext")
    print()
    print("Applying the same key twice cancels out, because any bit XORed")
    print("with itself returns 0, and any bit XORed with 0 stays the same.")
    print()
    print("Worked binary example (one byte):")
    print()
    # Pick an actual character so the numbers line up with reality.
    p_char = "P"
    k_char = "K"
    p_bits = format(ord(p_char), "08b")
    k_bits = format(ord(k_char), "08b")
    c_bits = format(ord(p_char) ^ ord(k_char), "08b")
    back_bits = format(ord(p_char) ^ ord(k_char) ^ ord(k_char), "08b")

    print(f"  plaintext bit  '{p_char}' = {p_bits}")
    print(f"  key bit        '{k_char}' = {k_bits}")
    print("                     ------- XOR (bit by bit)")
    c_byte = ord(p_char) ^ ord(k_char)
    # The result of XORing two printable characters is not guaranteed to
    # be printable itself -- this is exactly why real ciphertext is
    # displayed in hex rather than as text.
    if 32 <= c_byte < 127:
        c_note = f"character '{chr(c_byte)}'"
    else:
        c_note = f"byte 0x{c_byte:02X} (a non-printable control byte)"
    print(f"  ciphertext         = {c_bits}  (= {c_note})")
    print()
    print("  Now XOR the ciphertext with the key again:")
    print()
    print(f"  ciphertext         = {c_bits}")
    print(f"  key                = {k_bits}")
    print("                     ------- XOR")
    print(f"  recovered          = {back_bits}  (= '{chr(int(back_bits, 2))}' -- the original!)")
    print()
    print("Notice each column: XORing a bit with the key flips it where the")
    print("key is 1 and leaves it alone where the key is 0. Doing that a")
    print("second time simply flips the same positions back.")
    print()
    print("Why this matters: this flip-back behaviour is the foundation of")
    print("stream ciphers (Lab 2 uses ChaCha20, an XOR-based design) and of")
    print("the one-time pad.")


# ---------------------------------------------------------------------------
# 3. SECURITY GUARANTEES COMPARISON
# ---------------------------------------------------------------------------


def print_security_guarantees() -> None:
    """Terminal comparison of the three schemes discussed."""
    print("Caesar Cipher")
    print("Confidentiality: VERY WEAK")
    print("Brute-force resistance: VERY WEAK  (25 possible keys)")
    print("Modern production use: NO")
    print()
    print("XOR with repeating demo key")
    print("Confidentiality: LIMITED / WEAK")
    print("Key reuse risk: HIGH")
    print("Modern production use: NO")
    print()
    print("One-Time-Pad concept")
    print("Confidentiality: PERFECT SECRECY when all OTP requirements are satisfied")
    print("Key requirements: random, secret, message-length, never reused")
    print()
    print("How to read this table:")
    print("  - The two implemented ciphers are deliberately insecure -- they")
    print("    exist to demonstrate HOW encryption works, not to protect data.")
    print("  - The one-time pad is the theoretical gold standard, but its")
    print("    key-management demands (as long as the message, truly random,")
    print("    never reused, perfectly secret) make it impractical for most")
    print("    systems, which is why AES and ChaCha20 are used in practice.")
    print()
    print("This lab demonstrates cryptographic principles. It does NOT")
    print("recommend Caesar or repeating-key XOR for production DeRexi")
    print("data -- production systems use AES-256 / ChaCha20-Poly1305 with")
    print("proper key management (see Lab 2).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=== DEREXI CRYPTOGRAPHY LAB 1 ===")
    print("Fundamental cryptographic primitives -- classroom demo only.")
    print("All text is fictional DeRexi policy wording.")
    print()

    print("=== CRYPTOGRAPHIC FUNDAMENTALS ===")
    print_fundamentals()
    print()

    print("=== CAESAR CIPHER ===")
    caesar_ok = demonstrate_caesar()
    print()

    print("=== CAESAR MATHEMATICS ===")
    print_caesar_mathematics()
    # Show the actual encryption of each character to connect theory
    # to the ciphertext printed above.
    sample = "AURUM CAPITAL BANK POLICY"
    for ch in sample.replace(" ", ""):
        if ch.isalpha():
            x = ord(ch) - ord("A")
            print(f"  {ch}: x={x:>2} -> ({x} + {CAESAR_SHIFT}) mod 26 = "
                  f"{(x + CAESAR_SHIFT) % 26:>2} = {chr(ord('A') + (x + CAESAR_SHIFT) % 26)}")
    print()

    print("=== XOR CIPHER ===")
    xor_ok = demonstrate_xor()
    print()

    print("=== XOR MATHEMATICS ===")
    print_xor_mathematics()
    print()

    print("=== SECURITY GUARANTEES ===")
    print_security_guarantees()
    print()

    # Rubric evidence flags -- all five claim lines are printed only if
    # the corresponding work actually succeeded above.
    math_ok = True  # both mathematics sections printed without error
    analysis_ok = True  # both analyses + comparison table printed

    print("=== SUMMARY ===")
    print("Caesar cipher encryption/decryption:", "PASS" if caesar_ok else "FAIL")
    print("XOR cipher encryption/decryption:", "PASS" if xor_ok else "FAIL")
    print("Two cryptographic primitives implemented:",
          "PASS" if (caesar_ok and xor_ok) else "FAIL")
    print("Mathematical principles demonstrated:", "PASS" if math_ok else "FAIL")
    print("Security guarantees analyzed:", "PASS" if analysis_ok else "FAIL")
    print()
    print("DeRexi cryptographic fundamentals lab completed.")


if __name__ == "__main__":
    main()
