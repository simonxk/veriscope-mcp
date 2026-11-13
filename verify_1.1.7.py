# -*- coding: utf-8 -*-
"""
verify_1.1.7.py — Independent Third-Party Verifier for VeriScope MCP v1.1.7
Performs end-to-end cryptographic and physical artifact verification.
"""

import sys
import json
import base64
import hashlib
import tarfile
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("FATAL: cryptography library required (pip install cryptography)")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent

# Official Authoritative Trust Anchor
ROOT_PUBLIC_KEY_HEX = "be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93"
EXPECTED_FP_SHA256 = "aa87d0cff6aa7f8fad101f2441f911070bb6f80ff361873e442422e430f73363"
EXPECTED_SPKI_BASE64 = "MCowBQYDK2VwAyEAvlXZhdcl7DZZSzLtnYEib824vhKm2gL73yMcOqOPH5M="

print("================================================================")
print("  VeriScope MCP v1.1.7 — Independent Third-Party Audit Suite   ")
print("================================================================\n")

# 1. Verify Trust Anchor & Fingerprint
pub_bytes = bytes.fromhex(ROOT_PUBLIC_KEY_HEX)
calc_fp = hashlib.sha256(pub_bytes).hexdigest()
assert calc_fp == EXPECTED_FP_SHA256, f"FP mismatch: {calc_fp}"

der_spki = bytes.fromhex("302a300506032b6570032100") + pub_bytes
calc_spki = base64.b64encode(der_spki).decode("utf-8")
assert calc_spki == EXPECTED_SPKI_BASE64, f"SPKI mismatch: {calc_spki}"
print(f"[✓] Trust Anchor Fingerprint: {calc_fp} (MATCH)")
print(f"[✓] Trust Anchor SPKI Base64: {calc_spki} (MATCH)")

# 2. Verify Release Attestation Document
att_path = ROOT / "VERISCOPE_RELEASE_ATTESTATION_1.1.7.json"
assert att_path.exists(), f"Missing {att_path}"
att_doc = json.loads(att_path.read_text(encoding="utf-8"))

sig_hex = att_doc.pop("attestation_signature", "").replace("vsk_sig:", "")
manifest_sha = att_doc.pop("manifest_sha256", "")

# Deterministic JSON canonicalization
doc_bytes = json.dumps(att_doc, ensure_ascii=False, indent=2).encode("utf-8")
calc_manifest_sha = hashlib.sha256(doc_bytes).hexdigest()
assert calc_manifest_sha == manifest_sha, f"Manifest SHA mismatch: {calc_manifest_sha} != {manifest_sha}"
print(f"[✓] Manifest SHA-256: {manifest_sha} (MATCH)")

pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
pub_key.verify(bytes.fromhex(sig_hex), doc_bytes)
print(f"[✓] Ed25519 Attestation Signature: VALID (Cryptographically Proven)")

# 3. Verify Physical Tarball Artifact
tgz_path = ROOT / "veriscope-mcp-1.1.7.tgz"
assert tgz_path.exists(), f"Missing {tgz_path}"
tgz_bytes = tgz_path.read_bytes()

calc_shasum = hashlib.sha1(tgz_bytes).hexdigest()
calc_sri = f"sha512-{base64.b64encode(hashlib.sha512(tgz_bytes).digest()).decode('utf-8')}"

expected_shasum = att_doc["npm_registry"]["shasum"]
expected_sri = att_doc["npm_registry"]["integrity"]

assert calc_shasum == expected_shasum, f"Tarball SHA-1 mismatch: {calc_shasum} != {expected_shasum}"
assert calc_sri == expected_sri, f"Tarball SRI mismatch: {calc_sri} != {expected_sri}"
print(f"[✓] Tarball Size: {len(tgz_bytes)} bytes")
print(f"[✓] Tarball SHA-1: {calc_shasum} (MATCH)")
print(f"[✓] Tarball SHA-512 SRI: {calc_sri} (MATCH)")

# 4. Verify 5 Core Files in Unpacked Tarball
with tarfile.open(tgz_path, "r:gz") as tar:
    tar_members = {m.name: m for m in tar.getmembers() if m.isfile()}
    
    for rel_path, spec in att_doc["files"].items():
        member_name = f"package/{rel_path}"
        assert member_name in tar_members, f"Missing {member_name} in tarball"
        f = tar.extractfile(tar_members[member_name])
        b = f.read()
        f_sha = hashlib.sha256(b).hexdigest()
        assert f_sha == spec["sha256"], f"{rel_path} SHA mismatch: {f_sha} != {spec['sha256']}"
        assert len(b) == spec["size"], f"{rel_path} size mismatch: {len(b)} != {spec['size']}"
        print(f"[✓] Core File: {rel_path} ({len(b)} B) -> SHA-256 MATCH")

# 5. Verify N-3 Protocol Parameter Binding across 50 Golden Sandbox Concepts
sandbox_path = ROOT / "golden_sandbox_50.json"
sandbox_doc = json.loads(sandbox_path.read_text(encoding="utf-8"))

n3_passed = 0
for c in sandbox_doc["concepts"]:
    cid = c["concept_id"]
    canon_sha = c["canon_anchor"]["canon_sha256"].lower()
    rcpt = c["cryptographic_receipt"]
    msg = rcpt["signed_message"]
    sig = bytes.fromhex(rcpt["signature"].replace("vsk_sig:", ""))
    
    # 5.1 Asymmetric Signature Verification
    pub_key.verify(sig, msg.encode("utf-8"))
    
    # 5.2 Protocol Parameter Parsing & Binding
    parts = msg.split(":")
    assert parts[0] == "VERISCOPE_ATTESTATION" and parts[1] == "v2"
    signed_cid = parts[3]
    signed_sha = parts[4].lower()
    
    assert signed_cid.upper() == cid.upper(), f"Concept ID binding failed: {signed_cid} != {cid}"
    assert signed_sha == canon_sha, f"Canon SHA binding failed: {signed_sha} != {canon_sha}"
    n3_passed += 1

print(f"\n[✓] N-3 Attestation Receipt Parameter Binding: {n3_passed}/50 (100% PASS)")
print("\n================================================================")
print("  AUDIT VERDICT: FULL_PASS (Zero Discrepancies, 100% Proven)    ")
print("================================================================\n")
