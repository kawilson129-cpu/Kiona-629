# Assignment 5 Docker execution evidence

Executed November 9, 2026 on Windows Docker Desktop using Linux containers. Project name derexi-ctv2. The deployed service is the standalone DeRexi Pulse lab, with synthetic publisher data on the dashboard. The full policy/persona FastAPI application is outside this image.

## Verified results

- Docker engine and Compose available. Version output is preserved.
- Image build succeeded. build.txt records base layers, output configuration and manifest hashes.
- Compose startup returned exit 0 and healthy status.
- Container self-test passed normalization, simulated outage handling, metrics and escaping.
- All 14 checks in container-checks.json passed. Effective UID is 65532, capabilities are zero, NoNewPrivs is 1, and a write to the read-only root failed with EROFS.
- HTTP / and /healthz return 200 with restrictive CSP. Four source bars, one synthetic normalized item and three simulated publisher outages match the fixture.
- Separate read-only retrieval from within the container reached all four public publishers. Federal Register 38, FDIC 25, NIST 9 and Federal Reserve 15. Total normalized 87, default returned window 40. HTTPS links and URL uniqueness assertions passed.
- No database environment variable, database module or mounted host volume was present. Only approved source modules and the lab dashboard enter the image.
- Browser verification confirmed the visible dashboard. dashboard-synthetic.png is an actual screenshot.

## Reproduce

Run from repository root. The script records exact command arguments and exit codes. It uses the isolated project name and writes fresh execution output into this folder, so archive this evidence before rerunning.

    docker compose -p derexi-ctv2 -f cyber_threats_vulnerabilities_2_final/compose.yaml build
    powershell -File cyber_threats_vulnerabilities_2_final/docker-evidence/run-verification.ps1

The feed probe runs in a separate process inside the container. It does not change the dashboard's synthetic mode. Its full responses are in container-feeds.json. The tested publisher transports include JSON and RSS, using the existing Pulse code. This lab exposes / and /healthz, not the full application's /api/pulse route.

## Files

| Evidence | File |
|---|---|
| Docker engine/Compose | docker-version-authorized.txt, compose-version.txt |
| Build | build.txt, image-inspect.json |
| Effective configuration | compose-resolved.yaml, compose.verified.yaml, Dockerfile.verified |
| Startup and health | startup.txt, services.txt, container-inspect.json |
| Synthetic and security checks | self-test.txt, container-checks.json, security-summary.json |
| Public feeds | container-feeds.json, verify_feeds.py |
| Actual screenshot | dashboard-synthetic.png |
| Commands and test code | commands.txt, run-verification.ps1, verify_container.py |
| Server activity | logs.txt |

## Submission screenshots

1. Already saved — dashboard-synthetic.png. Keep the synthetic label and three simulated outages visible.
2. Capture Docker Desktop Containers with derexi-ctv2 expanded and pulse-lab running. Also show terminal output of the exact Compose ps command from commands.txt so healthy status and loopback mapping are visible.
3. Capture security-summary.json together with container-checks.json showing non-root UID, read-only storage, dropped capabilities, no-new-privileges, zero mounts and passing checks.
4. Capture the sources section near the end of container-feeds.json showing all four ok=true states and counts. Include checked_at and total_normalized. This documents actual publisher access separately from the synthetic screenshot.
5. Capture docker-version-authorized.txt, compose-version.txt and the final build.txt lines if installation/build screenshots are requested.

Underlying text/JSON is the primary reproducible evidence. Steps 2–5 are presentation captures the user can take from the saved outputs.

## Operating state and limitations

The healthy synthetic container remains running at http://127.0.0.1:8080/ for screenshot capture. Stop it with:

    docker compose -p derexi-ctv2 -f cyber_threats_vulnerabilities_2_final/compose.yaml stop

The image tag python:3.12-slim is movable, while the tested output image ID is retained in security-summary.json. Deployment-level firewall egress enforcement, enterprise authentication and publisher redirect host binding were not established. They are outside the isolated dashboard proof. Feed results are a timestamped observation and can change.

Status COMPLETE for Assignment 5's isolated Pulse platform implementation and verification. This is an evidence assessment against the supplied criterion, subject to instructor acceptance of the Pulse platform scope.
