# Historical zero-day research: CVE-2023-4863

## Research question and method

On November 17, 2026, this analysis asked: what evidence establishes a real zero-day, what code failed, and how could Aurum identify and treat exposure without reproducing an exploit? A zero-day is a vulnerability exploited before an effective patch is available; a severe CVE alone does not establish that history.

Method: start with the vendor's contemporaneous notice; follow its bug ID to the upstream fix; compare technical research and version records; distinguish report/disclosure dates from unknown first exploitation; translate the mechanism into inventory, detection and patch checks. No search hit alone was treated as exploit proof. Failed retrievals are listed in [research ledger](../evidence/research-ledger.md).

## Discovery and exploitation timeline

| Date | Supported event | Source and limits |
|---|---|---|
| September 6, 2023 | Apple SEAR and Citizen Lab reported the issue to Chrome | [Google release notice](https://chromereleases.googleblog.com/2023/09/stable-channel-update-for-desktop_11.html); not a known first exploit date |
| September 7, 2023 | Upstream commit fixes out-of-bounds writes in BuildHuffmanTable | [Commit 902bc919](https://chromium.googlesource.com/webm/libwebp/+/902bc9190331343b2017211debcec8d2ab87e17a); references Chromium bug 1479274 |
| September 11, 2023 | Chrome emergency release and public in-the-wild exploitation acknowledgement | Same [Google notice](https://chromereleases.googleblog.com/2023/09/stable-channel-update-for-desktop_11.html) |
| September 13, 2023 | CISA KEV addition recorded | [NVD record](https://nvd.nist.gov/vuln/detail/CVE-2023-4863); KEV deadline applied to covered federal entities, not automatically Aurum |
| September 2023 | Independent code/patch analysis explains the decoder flaw | [Isosceles technical research](https://blog.isosceles.com/the-webp-0day/); secondary analysis here, no exploit reproduction |

The official in-the-wild acknowledgement plus urgent fix supports classification as a historical zero-day. Exact first exploitation, full victim set and original exploit chain remain unknown here. The selected sources do **not** establish APT38 involvement. Reports discussing possible relationships to Apple/BLASTPASS issues do not authorize treating different CVE identifiers as equivalent.

## Affected versions and technical behavior

Historically affected upstream libwebp versions precede **1.3.2**; Chrome's September fix shipped as **116.0.5845.187** for Mac/Linux and **116.0.5845.187/.188** for Windows. These are historical fix boundaries, not suitable current deployment targets in 2026. Distribution backports must be checked against their own advisories rather than rejected solely for an older-looking version. [Google release](https://chromereleases.googleblog.com/2023/09/stable-channel-update-for-desktop_11.html), [NVD](https://nvd.nist.gov/vuln/detail/CVE-2023-4863), [Debian tracker](https://security-tracker.debian.org/tracker/CVE-2023-4863)

The vulnerable path decodes lossless WebP (VP8L) Huffman tables. The technical analysis locates an allocation in `ReadHuffmanCodes` and table construction through `BuildHuffmanTable`. Specially structured code lengths can cause writes beyond the allocated table area before rejection. An image extension is not a security boundary: an application that decodes attacker-controlled bytes may reach vulnerable library code. [Original technical research](https://blog.isosceles.com/the-webp-0day/)

The upstream fix performs validity/size analysis before table materialization and allocates additional space as needed. The changed files include `src/dec/vp8l_dec.c` and `src/utils/huffman_utils.c/.h`. This supports a memory-safety root cause rather than an authentication flaw. [Upstream fix](https://chromium.googlesource.com/webm/libwebp/+/902bc9190331343b2017211debcec8d2ab87e17a)

Our implication: malicious image decoding can corrupt the decoder process; arbitrary code execution depends on exploit and process defenses, and a complete host compromise may require further steps. We did not run a decoder, build a trigger, or observe a crash. A library's presence establishes potential exposure only after vulnerable build and reachable input are confirmed.

## Detection, patching and verification plan

| Step | Proposed Aurum owner | Evidence required / completion criterion |
|---|---|---|
| Inventory | IT asset owner | Browser, Electron, image-processing service and embedded/static libwebp builds; vendor backport status |
| Prioritize | SOC + application owner | Untrusted-image exposure, privilege level and Internet reachability; do not rely solely on CVSS |
| Detect | Chris Tanaka, SOC | Correlate image-decoder crashes, suspicious child processes and EDR alerts; each alone may have benign causes |
| Patch | Platform engineering | Current supported vendor release carrying the fix; restart apps/processes and rebuild images where library is embedded |
| Validate | QA + owner | Capture actual deployed versions, advisory/backport match, benign image compatibility and restart evidence |
| Compensate | Security engineering | Restrict risky image inputs where feasible, sandbox parsing, least privilege and egress controls while patching |

There is no universal exploit IOC in these sources; decoder crashes are weak behavioral signals. Do not invent a malicious WebP hash or detection signature. This assignment's Python distribution inventory does not inventory the user's browsers, all embedded libraries or production containers. No claim is made that DeRexi currently contains or is vulnerable to libwebp. Original exploit and deployed remediation verification are outside this safe research scope.

Outcome: PASS — research chain from report to patch to version boundaries documented. BLOCKED — actual Aurum/browser/image build exposure and deployed patch acceptance, because no corresponding deployed inventory was available.
