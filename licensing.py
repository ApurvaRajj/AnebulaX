"""
Nebula v9 — Offline Asymmetric Licensing System (Option B: Ed25519)

Features:
- Cryptographic asymmetric signing using Ed25519 (RFC 8032)
- Zero server dependency: runs 100% offline
- Tamper-proof: client ships strictly with the public verification key (EMBEDDED_PUBLIC_KEY_HEX)
- The vendor private key is kept strictly offline / in vendor secret storage (NEBULA_VENDOR_PRIVATE_KEY)
- Payload binds customer identity, issue date, optional expiry, and optional machine fingerprint
"""
import os
import json
import base64
import platform
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False

# ── Embedded Master Verification Public Key (Ed25519 raw bytes hex) ───────────
# The client ships ONLY with this public key to verify genuine vendor signatures.
# The vendor private key is NOT stored in this repository or client codebase.
EMBEDDED_PUBLIC_KEY_HEX = "46e23a9ef0b0794ffb693fa5d39de9c2fbe8ca56f3c5de3411f07897a731e8b3"

# Pre-signed evaluation / community license payload (signed once offline by vendor)
DEFAULT_COMMUNITY_LICENSE: Dict[str, Any] = {
    "customer": "Nebula Community User",
    "email": "community@nebula.ai",
    "tier": "Evaluation / Community",
    "issued_at": "2026-08-23T18:00:00+00:00",
    "expires_at": "2099-12-31T23:59:59+00:00",
    "machine_id": "any",
    "signature": "OCWQ3rCls+g7uTLZC4+tdvaC+ymdA3x6Zn4zsGeZbnbAozsVVL+BLt3qw1ngaE15TFZxs+2YMpQOZ8Aq73t8Bg=="
}

from config import _LICENSE_FILE

LICENSE_FILE_PATH = _LICENSE_FILE if _LICENSE_FILE.exists() else (Path.home() / ".anebulax_license.key")


def get_machine_fingerprint() -> str:
    """Generate a deterministic, anonymized machine fingerprint (HWID)."""
    raw = f"{platform.node()}:{platform.machine()}:{platform.processor()}:{platform.system()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _canonical_payload_bytes(payload: Dict[str, Any]) -> bytes:
    """Create deterministic canonical JSON bytes for signing/verifying."""
    signable = {k: v for k, v in payload.items() if k != "signature"}
    canonical_json = json.dumps(signable, sort_keys=True, separators=(",", ":"))
    return canonical_json.encode("utf-8")


def generate_keypair() -> Tuple[str, str]:
    """Generate a new vendor Ed25519 keypair for offline vendor use. Returns (private_hex, public_hex)."""
    if not _CRYPTO_AVAILABLE:
        raise RuntimeError("The 'cryptography' library is required for key generation.")
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    priv_bytes = private_key.private_bytes_raw()
    pub_bytes = public_key.public_bytes_raw()
    return priv_bytes.hex(), pub_bytes.hex()


def sign_license(
    customer: str,
    email: str,
    tier: str = "pro",
    expires_at: Optional[str] = None,
    bind_machine: bool = False,
    private_key_hex: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Vendor utility to sign a customer license payload.
    The vendor private key must be supplied via parameter or NEBULA_VENDOR_PRIVATE_KEY environment variable.
    """
    if not _CRYPTO_AVAILABLE:
        raise RuntimeError("The 'cryptography' library is required for signing licenses.")

    priv_key_str = private_key_hex or os.environ.get("NEBULA_VENDOR_PRIVATE_KEY")
    if not priv_key_str:
        raise ValueError(
            "Vendor private key is required for signing. Provide private_key_hex or set NEBULA_VENDOR_PRIVATE_KEY env var."
        )

    priv_bytes = bytes.fromhex(priv_key_str.strip())
    private_key = Ed25519PrivateKey.from_bytes(priv_bytes) if hasattr(Ed25519PrivateKey, "from_bytes") else Ed25519PrivateKey.from_private_bytes(priv_bytes)

    payload: Dict[str, Any] = {
        "customer": customer.strip(),
        "email": email.strip().lower(),
        "tier": tier.strip().lower(),
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at or "never",
        "machine_id": get_machine_fingerprint() if bind_machine else "any",
    }

    data_to_sign = _canonical_payload_bytes(payload)
    signature_bytes = private_key.sign(data_to_sign)
    payload["signature"] = base64.b64encode(signature_bytes).decode("utf-8")
    return payload


def verify_license(
    license_data: Optional[Dict[str, Any]] = None,
    license_path: Optional[Path] = None,
    public_key_hex: str = EMBEDDED_PUBLIC_KEY_HEX,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verify an offline signed license file against the embedded vendor public key.
    Returns: (is_valid: bool, status_message: str, license_info: dict)
    """
    if not _CRYPTO_AVAILABLE:
        return False, "Cryptographic verification library (cryptography) is not installed.", {}

    target_path = license_path or LICENSE_FILE_PATH
    if license_data is None:
        if not target_path.exists():
            return False, f"License file not found at {target_path}", {}
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                license_data = json.load(f)
        except Exception as e:
            return False, f"Failed to read license file: {e}", {}

    if not isinstance(license_data, dict):
        return False, "Invalid license format (must be JSON object).", {}

    sig_b64 = license_data.get("signature")
    if not sig_b64:
        return False, "Missing cryptographic signature in license.", license_data

    try:
        sig_bytes = base64.b64decode(sig_b64)
    except Exception:
        return False, "Invalid base64 signature encoding.", license_data

    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        data_to_verify = _canonical_payload_bytes(license_data)
        public_key.verify(sig_bytes, data_to_verify)
    except Exception:
        return False, "Invalid cryptographic signature (tampered or forged license).", license_data

    # Check expiration date
    expires_at_str = license_data.get("expires_at", "never")
    if expires_at_str != "never":
        try:
            clean_exp = expires_at_str.replace("Z", "+00:00")
            exp_date = datetime.fromisoformat(clean_exp)
            if exp_date.tzinfo is None:
                exp_date = exp_date.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc).timestamp() > exp_date.timestamp():
                return False, f"License expired on {expires_at_str}", license_data
        except Exception as e:
            return False, f"Invalid expiration date format in license: {e}", license_data

    # Check machine binding
    licensed_machine = license_data.get("machine_id", "any")
    if licensed_machine != "any":
        current_hwid = get_machine_fingerprint()
        if licensed_machine != current_hwid:
            return False, f"License is bound to machine {licensed_machine}, current machine is {current_hwid}", license_data

    tier = license_data.get("tier", "standard").capitalize()
    customer = license_data.get("customer", "Authorized User")
    return True, f"Valid {tier} License (Licensed to {customer})", license_data


def save_license_file(license_dict: Dict[str, Any], path: Optional[Path] = None) -> Path:
    """Save a signed license dict to disk."""
    target = path or LICENSE_FILE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(license_dict, f, indent=2)
    return target


def ensure_default_license() -> Tuple[bool, str]:
    """Ensure a valid pre-signed community/evaluation license exists on the machine."""
    valid, msg, _ = verify_license()
    if not valid:
        try:
            save_license_file(DEFAULT_COMMUNITY_LICENSE)
            valid, msg, _ = verify_license()
        except Exception as e:
            return False, f"Failed to initialize default license: {e}"
    return valid, msg
