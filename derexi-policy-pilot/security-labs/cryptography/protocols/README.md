# Cryptography 1 Assignment #6 — Cryptographic Protocols (Classroom Lab)

DeRexi: Policy Pilot · Cryptography 1 · Classroom demonstration only

This folder demonstrates configuring cryptographic protocols for the DeRexi
coursework:

1. **TLS configuration for a web server** — an isolated HTTPS server on
   localhost with a throwaway self-signed certificate.
2. **SSH key-based authentication** — a dedicated throwaway Ed25519 key pair
   and the exact commands, demonstrated **without** changing your Mac's SSH
   configuration.
3. **Secure communication channel** — a fictional DeRexi policy message sent
   over HTTPS with a verified round trip.
4. **Wireshark protocol-security analysis** — step-by-step preparation for a
   **live** capture (no capture is fabricated by this folder).

> Fictional DeRexi/Aurum Capital Bank data only. No production code, no real
> credentials, no `.env` changes, no Remote Login changes, localhost only.

---

## Files

| File | Purpose |
|---|---|
| `cryptographic_protocols.py` | Main lab: prints all headings, runs everything end to end, cleans up |
| `tls_demo_server.py` | Standalone HTTPS/TLS server (use for the Wireshark capture) |
| `tls_demo_client.py` | Standalone HTTPS client (generates the Wireshark traffic) |
| `DEMO_ONLY_tls_cert.pem` / `.key` | Throwaway TLS certificate + private key (auto-created, auto-deleted) |
| `DEMO_ONLY_derexi_ssh_key` / `.pub` | Throwaway SSH key pair (auto-created, auto-deleted) |
| `DEMO_ONLY_authorized_keys` | Simulated `authorized_keys` file (never applied for real) |

---

## 1 — Run the automated lab (best evidence for the report)

```bash
python cryptographic_protocols.py
```

This prints all seven sections, starts/stops the TLS server, generates the
SSH key pair, verifies the secure-channel round trip, prints the Wireshark
preparation plus the security analysis, and deletes every `DEMO_ONLY` file
at the end.

## 2 — Wireshark capture (live, manual)

1. Terminal 1 — start the HTTPS traffic source:

   ```bash
   python tls_demo_server.py
   ```

2. Open Wireshark (macOS): `open -a Wireshark`

3. Select the **loopback** interface: **`lo0`** (this lab only talks to
   `127.0.0.1` — do not use Wi-Fi/ethernet).

4. Start capture, then in terminal 2:

   ```bash
   python tls_demo_client.py      # repeat a few times for a longer capture
   ```

5. Stop capture and apply display filters:

   ```
   tls
   tcp.port == 8443
   tls.handshake
   tls.record
   ip.addr == 127.0.0.1
   ```

6. Screenshot: **Client Hello**, **Server Hello**, **Certificate** (subject /
   issuer), negotiated **TLS version** and **cipher suite**, encrypted
   **Application Data**, and the **absence of readable plaintext**.

Without TLS decryption configured you should see handshake metadata and the
certificate, but **not** the `GET /secure HTTP/1.1` request or the JSON body —
that confidentiality is exactly what TLS provides.

Optional decryption (only if you want to demonstrate): set
`SSLKEYLOGFILE` to a demo log file, point Wireshark (Preferences → Protocols →
TLS → (Pre)-Master-Secret log filename) at it, and delete the log afterwards.

> This folder only *prepares* the capture. Perform it yourself and screenshot
> the result for your course report.

## 3 — SSH key-based authentication (safe, simulated)

Remote Login is **off** on this Mac (port 22 closed). The lab therefore:

- generates a throwaway **Ed25519** key pair (`DEMO_ONLY_derexi_ssh_key`),
- prints the public-key fingerprint and public key,
- writes a simulated `DEMO_ONLY_authorized_keys`,
- prints the exact commands to use if you ever enable Remote Login,
- **never** edits `~/.ssh/authorized_keys` and **never** enables Remote Login.

Commands you could run yourself (only after you choose to enable Remote
Login):

```bash
cat DEMO_ONLY_derexi_ssh_key.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
ssh -i DEMO_ONLY_derexi_ssh_key -o IdentitiesOnly=yes derexi@127.0.0.1 -p 22
```

## Security / cleanup notes

- Every artefact is prefixed `DEMO_ONLY`, stays inside this folder, and is
  deleted at the end of the automated run.
- Private keys are never printed and are chmod `0600` while they exist.
- The demo server binds to `127.0.0.1:8443` only.
- TLS minimum version is **1.2** (SSLv2/v3 and TLS 1.0/1.1 disabled). On this
  machine the system Python links LibreSSL 2.8.3, which does not support
  TLS 1.3, so the negotiated version is truthfully reported as **TLS 1.2**.
- Nothing here touches production DeRexi, `.env`, firewall settings, system
  certificates, or SSHD configuration.
- No new Python dependencies are required (Python standard library +
  the already-installed `cryptography` package).