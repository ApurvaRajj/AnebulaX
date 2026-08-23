#!/usr/bin/env python3
"""
Pre-commit hook to scan for hardcoded secrets, private keys, and high-entropy hex strings.
"""
import sys
import re
from pathlib import Path

# Patterns that signal private keys or unapproved secret exposures
SUSPICIOUS_PATTERNS = [
    (r'(?i)(?:vendor|demo|master|admin)?_?priv(?:ate)?_?(?:hex|key)\s*=\s*["\'][a-f0-9]{32,128}["\']', "Hardcoded Private Key Variable"),
    (r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----', "PEM Private Key Block"),
    (r'(?i)(?:secret|api_key|token|auth_token)\s*=\s*["\'][A-Za-z0-9_\-]{24,128}["\']', "Hardcoded Secret / API Key"),
    (r'(?i)VENDOR_DEMO_PRIV_HEX', "Legacy Compromised Key Identifier"),
    (r'(?i)VENDOR_PRIV_HEX', "Private Key Variable Identifier"),
]

# Allowlisted files and patterns (e.g., test fixtures that test rejection of fake keys, public verification keys)
ALLOWLIST_PATTERNS = [
    r'EMBEDDED_PUBLIC_KEY_HEX',
    r'NEW_EMBEDDED_PUBLIC_KEY_HEX',
    r'public_key',
    r'public_hex',
    r'signature',
]


def scan_file(file_path: Path) -> list:
    issues = []
    if file_path.name == "pre_commit_secret_scan.py":
        return issues
    if file_path.suffix not in (".py", ".json", ".txt", ".md", ".sh", ".yml", ".yaml"):
        return issues

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return issues

    is_test = file_path.name.startswith("test_")
    is_doc = file_path.suffix == ".md"

    for line_no, line in enumerate(content.splitlines(), start=1):
        if is_test and ("assert not hasattr" in line or "assert \"" in line or "not in" in line):
            continue
        if is_doc and "VENDOR_DEMO_PRIV_HEX" in line and not re.search(r'=\s*["\'][a-f0-9]{32,128}["\']', line):
            continue
        for pattern, desc in SUSPICIOUS_PATTERNS:
            if re.search(pattern, line):
                # Check allowlist
                if any(re.search(al, line) for al in ALLOWLIST_PATTERNS) and "priv" not in line.lower():
                    continue
                issues.append((file_path, line_no, desc, line.strip()[:80]))
    return issues


def main():
    root = Path(__file__).resolve().parent.parent
    scan_targets = []

    # If git is available, scan staged files; otherwise scan workspace
    import subprocess
    try:
        res = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, cwd=root)
        if res.returncode == 0 and res.stdout.strip():
            staged = [root / p for p in res.stdout.strip().splitlines()]
            scan_targets = [p for p in staged if p.exists()]
    except Exception:
        pass

    if not scan_targets:
        # Full workspace sweep
        for ext in ("*.py", "*.json", "*.md"):
            scan_targets.extend(root.glob(ext))
        scan_targets.extend((root / "executors").glob("*.py"))

    all_issues = []
    for path in set(scan_targets):
        # Skip git cache and venv
        if ".git" in path.parts or ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        all_issues.extend(scan_file(path))

    if all_issues:
        print("\n❌ PRE-COMMIT SECRET SCANNER BLOCKED COMMIT:")
        for path, line_no, desc, snippet in all_issues:
            print(f"  [{desc}] {path.name}:{line_no} -> {snippet}")
        print("\nPlease remove hardcoded credentials / private keys before committing.\n")
        sys.exit(1)
    else:
        print("✓ Secret scan passed: Zero hardcoded private keys or credentials detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
