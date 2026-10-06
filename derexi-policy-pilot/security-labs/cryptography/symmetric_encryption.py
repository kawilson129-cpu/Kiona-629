"""
DeRexi: Policy Pilot -- Cryptography Lab 2: Symmetric Encryption
================================================================

A beginner-friendly demonstration of symmetric (single-key) cryptography:

    1. AES in ECB mode        (required by the rubric, with strong caveats)
    2. AES in CBC mode        (random IV, hides repeating patterns)
    3. Key management         (secure generation, storage, rotation)
    4. Stream cipher          (ChaCha20)
    5. Security considerations

SYMMETRIC vs ASYMMETRIC
-----------------------
Symmetric cryptography uses ONE shared key to both encrypt and decrypt.
It is fast and well suited to bulk data (files, database fields, backups).
The hard part is not the algorithm -- it is getting the key to the other
side safely. That is why key management (section 3) matters as much as
the encryption itself.

DEPENDENCY
----------
This lab uses the PyCA ``cryptography`` package (recorded in
``requirements-dev.txt`` for classroom use only). Python's standard
library does NOT include AES or ChaCha20, so an external library is
required. The production DeRexi application does not import this package.

CLASSROOM DEMONSTRATION ONLY
----------------------------
Every key, IV, nonce, and message below is fictional and generated fresh
at runtime. No real credentials, API keys, or Supabase values are used.
This file lives in ``security-labs/`` and is completely separate from
DeRexi's production authentication, database, and API.

Run it with:

    python security-labs/cryptography/symmetric_encryption.py
"""

import hashlib
import os

from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

AES_BLOCK_BITS = 128  # AES processes data in 128-bit (16-byte) blocks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def to_hex(data: bytes) -> str:
    """Return bytes as readable lowercase hexadecimal."""
    return data.hex()


def generate_aes_key() -> bytes:
    """
    Generate a 256-bit AES key using the OS secure random generator.

    ``os.urandom`` pulls from the operating system's CSPRNG (the same
    source used for generating salts and session tokens), so the key is
    unpredictable to anyone else.

    NOTE FOR BEGINNERS: never use Python's ``random`` module for
    cryptography. It is a pseudo-random generator meant for games and
    simulations -- its output can be predicted if you see enough of it.
    """
    return os.urandom(32)  # 32 bytes = 256 bits -> AES-256


def pkcs7_pad(data: bytes, block_size: int = AES_BLOCK_BITS // 8) -> bytes:
    """
    Pad data so its length is an exact multiple of the AES block size.

    ECB and CBC are *block* modes: they can only encrypt whole 16-byte
    blocks. PKCS#7 appends N bytes of value N. If the data is already
    aligned it adds a full extra block (also of value 16), which is
    what lets the decryptor tell real padding apart from data.
    """
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes, block_size: int = AES_BLOCK_BITS // 8) -> bytes:
    """Remove PKCS#7 padding, raising if the padding is malformed."""
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padding: data length is not block-aligned")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid padding: bad pad value")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding: bytes do not match")
    return data[:-pad_len]


# ---------------------------------------------------------------------------
# 1. AES ECB MODE
# ---------------------------------------------------------------------------


def demonstrate_aes_ecb() -> bool:
    """
    AES-256 in Electronic Codebook (ECB) mode.

    WHY ECB IS HERE: the coursework rubric explicitly requires a working
    ECB example, so it is demonstrated below -- with a clear warning.

    WHY ECB SHOULD NOT BE USED FOR SENSITIVE PRODUCTION DATA:
    ECB encrypts every 16-byte block INDEPENDENTLY with the same key and
    no IV. That means identical plaintext blocks always produce
    identical ciphertext blocks. Any repeating structure in the data
    (repeated phrases, fixed record formats, padding) shows up as
    repeating patterns in the ciphertext. Someone looking at the
    ciphertext alone can detect those patterns -- and for images, ECB
    famously preserves the picture's shape.

    ECB is fine for teaching the mechanics of a block cipher. It is not
    fine for encrypting real customer information.
    """
    # The plaintext must be padded to a whole number of 16-byte blocks.
    plaintext = (
        b"Aurum Capital Bank employees must protect confidential "
        b"customer information."
    )

    key = generate_aes_key()
    padded = pkcs7_pad(plaintext)

    # Encrypt: same key, ECB mode = no IV at all.
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    # Decrypt with the same key.
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    recovered = pkcs7_unpad(decryptor.update(ciphertext) + decryptor.finalize())

    verified = recovered == plaintext

    print("Plaintext (fictional policy message):")
    print(" ", plaintext.decode())
    print()
    print("DEMO key (fictional, generated fresh):", to_hex(key))
    print("Plaintext after PKCS#7 padding        :", to_hex(padded))
    print()
    print("Ciphertext (hex):")
    print(" ", to_hex(ciphertext))
    print()
    print("Decrypted plaintext:")
    print(" ", recovered.decode())
    print()
    print("AES-ECB decryption verification:", "PASS" if verified else "FAIL")
    print()
    print("Why ECB is not for production:")
    print("  - No IV, so identical 16-byte blocks encrypt identically.")
    print("  - Repeating plaintext patterns remain visible in ciphertext.")
    print("  - Included here because the rubric requires it (demo only).")

    return verified


# ---------------------------------------------------------------------------
# 2. AES CBC MODE
# ---------------------------------------------------------------------------


def demonstrate_aes_cbc() -> bool:
    """
    AES-256 in Cipher Block Chaining (CBC) mode.

    HOW CBC IMPROVES ON ECB: instead of encrypting each block on its
    own, CBC XORs each plaintext block with the PREVIOUS ciphertext
    block before encrypting it. The very first block is XORed with an
    Initialization Vector (IV). The result: two identical plaintext
    blocks produce different ciphertext blocks, because they sit in
    different chain positions. Repeating patterns disappear.

    THE IV:
      * Required by CBC for the first block.
      * It does NOT need to be secret -- it is usually stored or sent
        alongside the ciphertext.
      * It MUST be unique and unpredictable for each encryption under
        the same key. Reusing an IV with the same key leaks
        relationships between messages.

    THE IMPORTANT LIMITATION:
      CBC provides confidentiality ONLY. It does not authenticate the
      ciphertext -- an attacker who cannot read the data can still flip
      bits in it and produce a subtly modified plaintext that a naive
      decryptor will accept. For that reason modern systems should use
      authenticated encryption (AES-GCM, ChaCha20-Poly1305) instead of
      bare CBC. See the SECURITY CONSIDERATIONS section.
    """
    plaintext = (
        b"Aurum Capital Bank security policies must be reviewed and "
        b"approved by the Compliance Officer."
    )

    key = generate_aes_key()

    # The IV must be random and unique per encryption. It is public --
    # we display it openly below -- but it must never be REUSED with
    # the same key.
    iv = os.urandom(16)  # one IV per AES block size

    padded = pkcs7_pad(plaintext)

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    # Decryption needs the SAME key AND the SAME IV.
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    recovered = pkcs7_unpad(decryptor.update(ciphertext) + decryptor.finalize())

    verified = recovered == plaintext

    # Bonus demonstration: encrypt the SAME plaintext again under the
    # same key but a fresh IV -> completely different ciphertext.
    iv2 = os.urandom(16)
    encryptor2 = Cipher(algorithms.AES(key), modes.CBC(iv2)).encryptor()
    ciphertext2 = encryptor2.update(padded) + encryptor2.finalize()
    different = ciphertext2 != ciphertext

    print("Plaintext (fictional policy message):")
    print(" ", plaintext.decode())
    print()
    print("DEMO key (fictional, generated fresh):", to_hex(key))
    print("IV  (random, unique, NOT secret)     :", to_hex(iv))
    print()
    print("Ciphertext (hex):")
    print(" ", to_hex(ciphertext))
    print()
    print("Decrypted plaintext:")
    print(" ", recovered.decode())
    print()
    print("AES-CBC decryption verification:", "PASS" if verified else "FAIL")
    print()
    print("Same plaintext + same key + NEW IV -> different ciphertext:", different)
    print("  -> A fresh IV per encryption prevents ciphertext from revealing")
    print("     that two messages were identical.")
    print()
    print("CBC notes:")
    print("  - CBC hides repeating block patterns that ECB leaks.")
    print("  - CBC needs an IV; the IV may be public but must be unique.")
    print("  - CBC encryption alone does NOT authenticate the ciphertext.")

    return verified and different


# ---------------------------------------------------------------------------
# 3. KEY MANAGEMENT
# ---------------------------------------------------------------------------


def demonstrate_key_management() -> bool:
    """
    Secure key-generation practices.

    WHAT A REAL APPLICATION SHOULD DO (this is the part that matters in
    production):

      * Generate keys with a cryptographically secure random source --
        the OS CSPRNG (``os.urandom`` / ``secrets``), never Python's
        ``random`` module.
      * Store keys OUTSIDE source code: a secrets manager, a key
        management service (KMS), protected environment configuration,
        or hardware-backed storage (HSM/TPM). Never commit a real key
        to Git -- history is forever and clones are everywhere.
      * Apply least privilege: only the services that must encrypt or
        decrypt should be able to read the key.
      * Rotate keys when appropriate (on a schedule, after staff
        changes, or immediately after a suspected exposure), and plan
        how old ciphertext will be read after rotation (key versioning).

    It is acceptable for THIS classroom script to print the demo key so
    you can watch the encryption happen -- every value below is
    fictional and generated fresh on each run. A production script
    would never print its key.
    """
    print("Generating keys with the OS secure random generator...")
    print()

    # AES-256 key: 32 bytes.
    aes_key = generate_aes_key()

    # A separate key for the stream cipher later -- never reuse one key
    # across different algorithms/uses if you can avoid it.
    stream_key = generate_aes_key()

    # Keys are compared/stored by fingerprint, not by printing them.
    # SHA-256 of the key gives a stable ID you can safely log.
    key_fingerprint = hashlib.sha256(aes_key).hexdigest()[:16]

    print("AES-256 demo key (FICTIONAL / DEMO ONLY) :", to_hex(aes_key))
    print("ChaCha20 demo key (FICTIONAL/DEMO ONLY)  :", to_hex(stream_key))
    print()
    print("Key length (AES-256)                     :", len(aes_key), "bytes =", len(aes_key) * 8, "bits")
    print("Key fingerprint (SHA-256, first 16 hex)  :", key_fingerprint)
    print()
    print("Randomness sanity check -- two keys differ:", aes_key != stream_key)
    print()
    print("Production key management rules (NOT done in this demo script):")
    print("  - Store keys in a secrets manager / KMS / HSM, never in source code.")
    print("  - Never commit real keys to Git.")
    print("  - Limit access to keys on a least-privilege basis.")
    print("  - Rotate keys on a schedule or after suspected exposure.")

    # Verify both keys are well-formed and independent.
    ok = (
        len(aes_key) == 32
        and len(stream_key) == 32
        and aes_key != stream_key
        and all(isinstance(b, int) for b in aes_key)
    )
    return ok


# ---------------------------------------------------------------------------
# 4. STREAM CIPHER (ChaCha20)
# ---------------------------------------------------------------------------


def demonstrate_stream_cipher() -> bool:
    """
    A modern stream cipher: ChaCha20.

    WHAT A STREAM CIPHER IS:
    A stream cipher does NOT encrypt in fixed-size blocks like AES-ECB
    or AES-CBC. Instead it generates a long pseudo-random keystream
    from a key + nonce, then XORs that keystream with the plaintext
    byte-by-byte. Because it is XOR, encryption and decryption are the
    exact same operation -- you just XOR the ciphertext again.

    This means stream ciphers:
      * accept plaintext of ANY length (no padding, no block alignment),
      * are very fast in software,
      * are particularly good for network traffic and streaming data.

    WHY THE NONCE MUST NEVER BE REUSED WITH THE SAME KEY:
    The nonce ("number used once") varies the keystream. If you encrypt
    two different messages with the SAME key and the SAME nonce, they
    get the SAME keystream. XOR the two ciphertexts together and the
    keystream cancels out, leaving an attacker with
    plaintext1 XOR plaintext2 -- from which both can often be
    recovered. So: a fresh random nonce for every message, always.

    ChaCha20 is a widely used, high-performance stream cipher designed
    by Daniel Bernstein. In this lab we use it as a *raw* stream cipher
    to demonstrate the primitive itself. Note that modern systems
    normally use the authenticated form, ChaCha20-Poly1305 (available
    in this same library), which also detects tampering.
    """
    plaintext = (
        b"Aurum Capital Bank employees must report suspicious activity "
        b"to the BSA/AML Compliance Officer."
    )

    key = generate_aes_key()  # 32 bytes works for ChaCha20 too

    # ChaCha20 in the PyCA library takes a 16-byte nonce
    # (64-bit IV + 64-bit counter). It must be unique per message
    # under this key.
    nonce = os.urandom(16)

    encryptor = Cipher(algorithms.ChaCha20(key, nonce), None).encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Decryption uses the identical key + nonce (XOR is symmetric).
    decryptor = Cipher(algorithms.ChaCha20(key, nonce), None).decryptor()
    recovered = decryptor.update(ciphertext) + decryptor.finalize()

    verified = recovered == plaintext

    # Demonstrate the danger of nonce reuse: same key + same nonce on a
    # second message produces a keystream that cancels out.
    second_message = b"Aurum Capital Bank second demo message for nonce reuse."
    enc_a = Cipher(algorithms.ChaCha20(key, nonce), None).encryptor()
    ct_a = enc_a.update(plaintext) + enc_a.finalize()
    enc_b = Cipher(algorithms.ChaCha20(key, nonce), None).encryptor()
    ct_b = enc_b.update(second_message) + enc_b.finalize()
    leaked = bytes(x ^ y for x, y in zip(ct_a, ct_b))
    expected = bytes(x ^ y for x, y in zip(plaintext, second_message))
    reuse_exposed = leaked == expected  # keystream cancelled out

    print("Plaintext (fictional policy message):")
    print(" ", plaintext.decode())
    print()
    print("DEMO key (fictional, generated fresh):", to_hex(key))
    print("Nonce (16 bytes, unique per message) :", to_hex(nonce))
    print()
    print("Ciphertext (hex):")
    print(" ", to_hex(ciphertext))
    print()
    print("Decrypted plaintext:")
    print(" ", recovered.decode())
    print()
    print("Stream cipher decryption verification:", "PASS" if verified else "FAIL")
    print()
    print("Nonce-reuse demonstration (same key + same nonce, 2 messages):")
    print("  Attacker recovers msg1 XOR msg2 from ciphertexts alone:", reuse_exposed)
    print("  -> This is exactly why a nonce must NEVER be reused with the")
    print("     same key: the keystream cancels and the plaintext leaks.")

    return verified and reuse_exposed


# ---------------------------------------------------------------------------
# 5. SECURITY CONSIDERATIONS
# ---------------------------------------------------------------------------


def print_security_considerations() -> None:
    """
    Concise security notes for the coursework report.

    These same points also appear as comments throughout the script.
    """
    print("ECB:")
    print("  - Reveals data patterns: identical plaintext blocks -> identical")
    print("    ciphertext blocks, because each block is encrypted independently.")
    print("  - Included for demonstration / rubric purposes only.")
    print("  - Not recommended for sensitive production encryption.")
    print()
    print("CBC:")
    print("  - Uses an IV and XORs each block with the previous ciphertext")
    print("    block, hiding repeating patterns far better than ECB.")
    print("  - The IV must be unique per message under a given key; it does")
    print("    not need to be secret.")
    print("  - Encryption alone does NOT authenticate the ciphertext -- an")
    print("    attacker can tamper with it undetected.")
    print("  - Modern authenticated encryption (AES-GCM, ChaCha20-Poly1305)")
    print("    should be preferred for production use.")
    print()
    print("Key management:")
    print("  - Keys must be generated securely with the OS CSPRNG.")
    print("  - Real keys must never be committed to Git.")
    print("  - Production keys belong outside source code (secrets manager,")
    print("    KMS, protected environment config, or hardware-backed storage).")
    print("  - Access should follow least privilege.")
    print("  - Keys should be rotated when necessary (schedule, staff change,")
    print("    or suspected exposure).")
    print()
    print("Stream cipher:")
    print("  - Nonces must not be reused with the same key.")
    print("  - Modern authenticated encryption should be preferred when")
    print("    available (e.g. ChaCha20-Poly1305 over bare ChaCha20).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=== DEREXI CRYPTOGRAPHY LAB 2 ===")
    print("Symmetric encryption -- classroom demonstration only.")
    print("All keys, IVs, nonces, and messages are fictional and generated")
    print("fresh at runtime. No real credentials are used.")
    print()

    print("=== AES ECB MODE ===")
    ecb_ok = demonstrate_aes_ecb()
    print()

    print("=== AES CBC MODE ===")
    cbc_ok = demonstrate_aes_cbc()
    print()

    print("=== KEY MANAGEMENT ===")
    keys_ok = demonstrate_key_management()
    print()

    print("=== STREAM CIPHER ===")
    stream_ok = demonstrate_stream_cipher()
    print()

    print("=== SECURITY CONSIDERATIONS ===")
    print_security_considerations()
    print()

    print("=== SUMMARY ===")
    print("AES-ECB encryption/decryption:", "PASS" if ecb_ok else "FAIL")
    print("AES-CBC encryption/decryption:", "PASS" if cbc_ok else "FAIL")
    print("Secure random key generation:", "PASS" if keys_ok else "FAIL")
    print("Stream cipher encryption/decryption:", "PASS" if stream_ok else "FAIL")
    print()
    print("DeRexi symmetric cryptography lab completed.")


if __name__ == "__main__":
    main()
