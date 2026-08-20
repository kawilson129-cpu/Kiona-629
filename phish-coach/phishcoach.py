import os
import re
import time
import requests
from urllib.parse import urlparse

# ==========================
# PHISHCOACH CONFIGURATION
# ==========================

VT_API_KEY = os.getenv("VT_API_KEY")

VIRUSTOTAL_SCAN_URL = "https://www.virustotal.com/api/v3/urls"
VIRUSTOTAL_ANALYSIS_URL = "https://www.virustotal.com/api/v3/analyses/"

# ==========================
# RULE-BASED PHISHING CHECKS
# ==========================

RED_FLAG_RULES = {
    "Urgency Language": {
        "keywords": ["urgent", "immediately", "act now", "right away", "final notice", "limited time"],
        "points": 2,
        "lesson": "Phishing messages often pressure people to act quickly before they think."
    },
    "Fear-Based Language": {
        "keywords": ["suspended", "locked", "compromised", "unauthorized", "security alert", "breach"],
        "points": 2,
        "lesson": "Attackers use fear to make users click links or give up information."
    },
    "Credential Request": {
        "keywords": ["password", "verify your account", "login", "sign in", "confirm your identity"],
        "points": 3,
        "lesson": "Legitimate companies usually do not ask you to confirm passwords through email links."
    },
    "Money or Payment Language": {
        "keywords": ["invoice", "payment", "refund", "wire transfer", "bank account", "payroll"],
        "points": 2,
        "lesson": "Financial language is commonly used in phishing to create urgency or curiosity."
    },
    "Generic Greeting": {
        "keywords": ["dear customer", "dear user", "valued customer"],
        "points": 1,
        "lesson": "Generic greetings can be suspicious when the sender should know your name."
    },
    "Click Prompt": {
        "keywords": ["click here", "open attachment", "download now", "view document"],
        "points": 2,
        "lesson": "Phishing emails often push users to click links or open attachments."
    }
}

SUSPICIOUS_URL_SHORTENERS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly"
]

# ==========================
# HELPER FUNCTIONS
# ==========================

def get_multiline_input():
    print("\nPaste the suspicious email or text message below.")
    print("When finished, type DONE on a new line and press Enter.\n")

    lines = []

    while True:
        line = input()
        if line.strip().upper() == "DONE":
            break
        lines.append(line)

    return "\n".join(lines)


def extract_urls(text):
    url_pattern = r"https?://[^\s<>\"]+"
    urls = re.findall(url_pattern, text)
    return list(set(urls))


def extract_email_addresses(text):
    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    emails = re.findall(email_pattern, text)
    return list(set(emails))


def check_sender_domain(email_addresses):
    findings = []

    for email in email_addresses:
        domain = email.split("@")[-1].lower()

        if domain.endswith(".ru") or domain.endswith(".cn"):
            findings.append(f"{email} uses a domain that may deserve closer review.")

        if any(fake in domain for fake in ["support-", "secure-", "verify-", "account-"]):
            findings.append(f"{email} has wording often used in fake support/security addresses.")

    return findings


def rule_based_scan(text):
    lower_text = text.lower()
    total_score = 0
    findings = []

    for rule_name, rule_data in RED_FLAG_RULES.items():
        for keyword in rule_data["keywords"]:
            if keyword in lower_text:
                total_score += rule_data["points"]
                findings.append({
                    "rule": rule_name,
                    "keyword": keyword,
                    "points": rule_data["points"],
                    "lesson": rule_data["lesson"]
                })
                break

    return total_score, findings


def check_urls_locally(urls):
    findings = []
    score = 0

    for url in urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        if domain in SUSPICIOUS_URL_SHORTENERS:
            score += 2
            findings.append(f"{url} uses a URL shortener, which can hide the final destination.")

        if parsed_url.scheme == "http":
            score += 1
            findings.append(f"{url} does not use HTTPS.")

        if "@" in url:
            score += 2
            findings.append(f"{url} contains '@', which can be used to disguise the real destination.")

    return score, findings


def scan_url_with_virustotal(url):
    if not VT_API_KEY:
        return {
            "error": "Missing VirusTotal API key. Set VT_API_KEY before running the program."
        }

    headers = {
        "x-apikey": VT_API_KEY
    }

    try:
        submit_response = requests.post(
            VIRUSTOTAL_SCAN_URL,
            headers=headers,
            data={"url": url},
            timeout=20
        )

        if submit_response.status_code not in [200, 201]:
            return {
                "error": f"VirusTotal submit failed. Status code: {submit_response.status_code}"
            }

        analysis_id = submit_response.json()["data"]["id"]

        time.sleep(5)

        analysis_response = requests.get(
            VIRUSTOTAL_ANALYSIS_URL + analysis_id,
            headers=headers,
            timeout=20
        )

        if analysis_response.status_code != 200:
            return {
                "error": f"VirusTotal analysis failed. Status code: {analysis_response.status_code}"
            }

        analysis_data = analysis_response.json()
        stats = analysis_data["data"]["attributes"]["stats"]

        return {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0)
        }

    except requests.exceptions.RequestException as error:
        return {
            "error": f"Network error: {error}"
        }
    except KeyError:
        return {
            "error": "Unexpected VirusTotal response format."
        }


def classify_risk(score):
    if score >= 10:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    else:
        return "LOW"


def print_report(text, rule_score, rule_findings, urls, url_score, url_findings, emails, sender_findings):
    final_score = rule_score + url_score
    risk_level = classify_risk(final_score)

    print("\n" + "=" * 50)
    print("PHISHCOACH SECURITY REPORT")
    print("=" * 50)

    print(f"\nFinal Risk Level: {risk_level}")
    print(f"Final Risk Score: {final_score}/15+")

    print("\n--- Rule-Based Red Flags ---")
    if rule_findings:
        for finding in rule_findings:
            print(f"\n[{finding['rule']}]")
            print(f"Matched Keyword: {finding['keyword']}")
            print(f"Risk Points: +{finding['points']}")
            print(f"Lesson: {finding['lesson']}")
    else:
        print("No major phishing language patterns detected.")

    print("\n--- Email Addresses Found ---")
    if emails:
        for email in emails:
            print(f"- {email}")
    else:
        print("No email addresses found.")

    print("\n--- Sender/Email Domain Findings ---")
    if sender_findings:
        for finding in sender_findings:
            print(f"- {finding}")
    else:
        print("No obvious sender domain warning signs found.")

    print("\n--- URLs Found ---")
    if urls:
        for url in urls:
            print(f"- {url}")
    else:
        print("No URLs found.")

    print("\n--- Local URL Findings ---")
    if url_findings:
        for finding in url_findings:
            print(f"- {finding}")
    else:
        print("No obvious local URL warning signs found.")

    print("\n--- VirusTotal URL Results ---")
    if urls:
        for url in urls:
            print(f"\nScanning: {url}")
            vt_result = scan_url_with_virustotal(url)

            if "error" in vt_result:
                print(vt_result["error"])
            else:
                print(f"Malicious: {vt_result['malicious']}")
                print(f"Suspicious: {vt_result['suspicious']}")
                print(f"Harmless: {vt_result['harmless']}")
                print(f"Undetected: {vt_result['undetected']}")

                if vt_result["malicious"] > 0 or vt_result["suspicious"] > 0:
                    print("VirusTotal Warning: One or more security vendors flagged this URL.")
                else:
                    print("VirusTotal Note: No vendors flagged this URL in this scan.")
    else:
        print("No URLs to scan with VirusTotal.")

    print("\n--- Safety Recommendation ---")
    if risk_level == "HIGH":
        print("Do NOT click links, open attachments, or reply. Report this message to IT or delete it.")
    elif risk_level == "MEDIUM":
        print("Be cautious. Verify the sender through a trusted channel before taking action.")
    else:
        print("Low risk based on these checks, but still verify unexpected messages.")

    print("\nCyber Tip:")
    print("When in doubt, go directly to the official website instead of clicking email links.")


def main():
    print("=" * 50)
    print("WELCOME TO PHISHCOACH")
    print("A beginner-friendly phishing email awareness tool")
    print("=" * 50)

    email_text = get_multiline_input()

    if not email_text.strip():
        print("No text entered. Please run the program again.")
        return

    rule_score, rule_findings = rule_based_scan(email_text)
    urls = extract_urls(email_text)
    emails = extract_email_addresses(email_text)
    sender_findings = check_sender_domain(emails)
    url_score, url_findings = check_urls_locally(urls)

    print_report(
        email_text,
        rule_score,
        rule_findings,
        urls,
        url_score,
        url_findings,
        emails,
        sender_findings
    )


if __name__ == "__main__":
    main()