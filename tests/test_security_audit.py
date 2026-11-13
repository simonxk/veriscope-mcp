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
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertEqual(res["verification_status"], "HASH_MATCHED")
        self.assertNotIn("public_key", res, "Path A must cleanly omit public_key")

    def test_path_a_tampered_hash(self):
        res = self.server.verify_attestation(concept_id="VS-PHIL-001", canon_sha256="deadbeef" * 8)
        self.assertFalse(res["hash_matched"])
        self.assertEqual(res["verification_status"], "TAMPER_DETECTED")

    def test_n3_payload_mismatch_concept(self):
        c0 = self.sandbox["concepts"][0]
        res = self.server.verify_attestation(
            concept_id="VS-PHIL-002",  # Mismatch!
            canon_sha256=c0["canon_anchor"]["canon_sha256"],
            attestation=c0["cryptographic_receipt"]
        )
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertEqual(res["verification_status"], "PAYLOAD_MISMATCH")

    def test_n3_payload_mismatch_sha(self):
        c0 = self.sandbox["concepts"][0]
        res = self.server.verify_attestation(
            concept_id="VS-PHIL-001",
            canon_sha256="deadbeef" * 8,  # Mismatch!
            attestation=c0["cryptographic_receipt"]
        )
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertEqual(res["verification_status"], "PAYLOAD_MISMATCH")

    def test_anti_bypass_guard(self):
        res = self.server.verify_attestation(
            concept_id="VS-PHIL-001",
            attestation={
                "signature": "vsk_sig:" + "0" * 128,
                "signed_message": "NOT_AN_ATTESTATION: arbitrary text",
                "public_key": "be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93"
            }
        )
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertIn(res["verification_status"], ("SIGNATURE_INVALID", "MALFORMED_ATTESTATION"))

    def test_n3_full_50_sandbox_loop(self):
        passed = 0
        for c in self.sandbox["concepts"]:
            res = self.server.verify_attestation(
                concept_id=c["concept_id"],
                canon_sha256=c["canon_anchor"]["canon_sha256"],
                attestation=c["cryptographic_receipt"]
            )
            self.assertTrue(res["is_cryptographically_verified"], f"{c['concept_id']} failed verify")
            self.assertEqual(res["verification_status"], "SIGNATURE_VALID")
            self.assertEqual(res["signed_payload"]["concept_id"], c["concept_id"])
            self.assertEqual(res["signed_payload"]["canon_sha256"], c["canon_anchor"]["canon_sha256"].lower())
            passed += 1
        self.assertEqual(passed, 50)


if __name__ == "__main__":
    unittest.main()
