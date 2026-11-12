"""
Python Security & Cryptographic Integrity Regression Test Suite
Verifies fixes for S-2, S-3.
"""

import sys
import os
import json
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from veriscope_mcp.server import VeriScopeMCPServer


class TestSecurityAudit(unittest.TestCase):
    def setUp(self):
        self.server = VeriScopeMCPServer()
        with open(os.path.join(ROOT, "golden_sandbox_50.json"), encoding="utf-8") as f:
            self.sandbox = json.load(f)

    def test_s1_forged_signature_rejected(self):
        rcpt = self.sandbox["concepts"][0]["cryptographic_receipt"]
        forged_rcpt = {
            "signature": "vsk_sig:" + "0" * 128,
            "signed_message": "FORGED: Kant never wrote this",
            "public_key": rcpt["public_key"]
        }
        res = self.server.verify_attestation(attestation=forged_rcpt)
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertEqual(res["verification_status"], "SIGNATURE_INVALID")

    def test_legitimate_ed25519_verified(self):
        rcpt = self.sandbox["concepts"][0]["cryptographic_receipt"]
        res = self.server.verify_attestation(attestation=rcpt)
        self.assertTrue(res["is_cryptographically_verified"])
        self.assertEqual(res["verification_status"], "SIGNATURE_VALID")
        self.assertEqual(res["algorithm"], "Ed25519")

    def test_s2_path_a_honest_labeling(self):
        c0 = self.sandbox["concepts"][0]
        res = self.server.verify_attestation(concept_id="VS-PHIL-001", canon_sha256=c0["canon_anchor"]["canon_sha256"])
        self.assertEqual(res["method"], "local_hash_lookup")
        self.assertEqual(res["algorithm"], "SHA-256")
        self.assertTrue(res["hash_matched"])
        self.assertEqual(res["verification_status"], "HASH_MATCHED")

    def test_path_a_tampered_hash(self):
        res = self.server.verify_attestation(concept_id="VS-PHIL-001", canon_sha256="deadbeef" * 8)
        self.assertFalse(res["hash_matched"])
        self.assertEqual(res["verification_status"], "TAMPER_DETECTED")


if __name__ == "__main__":
    unittest.main()
