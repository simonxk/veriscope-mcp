# -*- coding: utf-8 -*-
"""
tests/test_citation_audit.py — Unit test for citation audit forensic logic in Python.
Directly tests published VeriScopeServer implementation to guarantee production fidelity.
"""

import unittest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from veriscope_mcp.server import VeriScopeMCPServer, VERISCOPE_PUBLIC_KEY_HEX


class TestCitationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = VeriScopeMCPServer()

    def test_rawls_author_name_space_preservation(self):
        """T-1 regression: clean_au must not strip space between John and Rawls."""
        txt = 'As argued in "A Theory of Justice" by John Rawls, the original position...'
        res = self.server.audit_citations(txt)
        self.assertEqual(res["total_citations_extracted"], 1)
        cite = res["citations"][0]
        self.assertEqual(cite["extracted_author"], "John Rawls")
        self.assertEqual(cite["canonical_author"], "John Rawls")
        self.assertEqual(cite["verdict"], "SUPPORTS")

    def test_author_in_book_exact_match(self):
        """Test standard author in book citation."""
        res = self.server.audit_citations("正如亚当·斯密在《国富论》中指出，每个人都在追求自身的利益...")
        self.assertEqual(res["total_citations_extracted"], 1)
        self.assertEqual(res["citations"][0]["verdict"], "SUPPORTS")
        self.assertEqual(res["citations"][0]["canonical_author"], "Adam Smith")

    def test_attribution_mismatch_attack(self):
        """Test suspect author mismatch detection."""
        res = self.server.audit_citations("正如著名经济学家凯恩斯在《国富论》中所强调...")
        self.assertEqual(res["total_citations_extracted"], 1)
        self.assertEqual(res["citations"][0]["verdict"], "ATTRIBUTION_SUSPECT")
        self.assertEqual(res["suspect_count"], 1)

    def test_unindexed_real_literature_honest_labeling(self):
        """A-1 regression: Unindexed real book (Fei Xiaotong) must be UNINDEXED, not AI hallucination."""
        res = self.server.audit_citations("根据费孝通在《乡土中国》中的差序格局理论...")
        self.assertEqual(res["total_citations_extracted"], 1)
        cite = res["citations"][0]
        self.assertEqual(cite["verdict"], "UNINDEXED")
        self.assertNotIn("AI 幻觉", cite["verdict_zh"])

    def test_s4_attacker_custom_public_key_rejected(self):
        """S-4 regression: Caller-supplied custom public key must be strictly rejected as ISSUER_UNTRUSTED."""
        fake_pub = "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff"
        res = self.server.verify_attestation(attestation={
            "signature": "vsk_sig:" + "0" * 128,
            "signed_message": "ATTACK: arbitrary statement",
            "public_key": fake_pub
        })
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertEqual(res["verification_status"], "ISSUER_UNTRUSTED")

    def test_s2_path_a_honest_crypto_flag(self):
        """S-2 regression: Local hash lookup must set is_cryptographically_verified to False."""
        c = self.server.sandbox_map.get("VS-PHIL-001")
        target_sha = c["canon_anchor"]["canon_sha256"]
        res = self.server.verify_attestation(
            concept_id="VS-PHIL-001",
            canon_sha256=target_sha
        )
        self.assertEqual(res["method"], "local_hash_lookup")
        self.assertTrue(res["hash_matched"])
        self.assertFalse(res["is_cryptographically_verified"])
        self.assertNotIn("public_key", res)

    def test_western_prefix_stripping(self):
        """Test stripping of prefixes like 'As noted by Kant'."""
        txt = 'As noted by Kant in "Critique of Pure Reason", space and time are pure forms of intuition...'
        res = self.server.audit_citations(txt)
        self.assertEqual(res["total_citations_extracted"], 1)
        self.assertEqual(res["citations"][0]["extracted_author"], "Kant")
        self.assertEqual(res["citations"][0]["verdict"], "SUPPORTS")

    def test_chinese_pronoun_reference(self):
        """Test that pronouns like '他在《...》' do not trigger false ATTRIBUTION_SUSPECT."""
        txt = "他在《纯粹理性批判》中探讨了先验感性论与范畴演绎..."
        res = self.server.audit_citations(txt)
        self.assertEqual(res["total_citations_extracted"], 1)
        self.assertEqual(res["citations"][0]["verdict"], "SUPPORTS")
        self.assertEqual(res["suspect_count"], 0)

    def test_reverse_proposition_discrimination(self):
        """Test that unquoted text gets SUPPORTS (0.85), not EXACT_MATCH (0.99)."""
        txt_unquoted = "在《纯粹理性批判》中，有人声称物自体不可知并主张怀疑论..."
        res_unquoted = self.server.audit_citations(txt_unquoted)
        self.assertEqual(res_unquoted["citations"][0]["verdict"], "SUPPORTS")
        self.assertEqual(res_unquoted["citations"][0]["confidence_score"], 0.85)

        c = self.server.sandbox_map.get("VS-PHIL-001")
        excerpt = c["canon_anchor"]["verbatim_excerpt"]
        slice_str = excerpt[:20]
        txt_quoted = f'在《纯粹理性批判》中，康德写道：“{slice_str}”'
        res_quoted = self.server.audit_citations(txt_quoted)
        self.assertEqual(res_quoted["citations"][0]["verdict"], "EXACT_MATCH")
        self.assertEqual(res_quoted["citations"][0]["confidence_score"], 0.99)

    def test_zero_citations_fail_open_remediation(self):
        """Test that 0 citations returns verdict='NO_CITATIONS_FOUND' and citation_health_score=None."""
        txt = "今天天气很好，这是一篇随笔，完全不涉及任何学术引文。"
        res = self.server.audit_citations(txt)
        self.assertEqual(res["total_citations_extracted"], 0)
        self.assertEqual(res["verdict"], "NO_CITATIONS_FOUND")
        self.assertIsNone(res["citation_health_score"])


if __name__ == "__main__":
    unittest.main()
