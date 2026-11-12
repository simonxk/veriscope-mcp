# -*- coding: utf-8 -*-
"""
tests/test_citation_audit.py — Unit test for citation audit forensic logic in Python.
"""

import unittest
import json
import re
from pathlib import Path

SANDBOX_PATH = Path(__file__).resolve().parent.parent / "golden_sandbox_50.json"
if not SANDBOX_PATH.exists():
    SANDBOX_PATH = Path(__file__).resolve().parent.parent / "src" / "veriscope_mcp" / "golden_sandbox_50.json"

AUTHOR_NOISE_WORDS = [
    "德意志哲学家", "德国哲学家", "法国哲学家", "英国经济学家", "美国社会学家",
    "古希腊哲学家", "古典政治学家", "社会学先驱", "法学先驱", "经济学大师",
    "著名哲学家", "学者", "教授", "先生", "作家", "部分学者", "然而", "但是",
    "认为", "强调", "指出", "提出", "声称", "根据", "按照"
]


def clean_author(raw: str) -> str:
    s = (raw or "").strip()
    for w in AUTHOR_NOISE_WORDS:
        s = s.replace(w, "").strip()
    s = re.sub(r"^[\s，,、“”\"'（(：:【\[]+", "", s)
    s = re.sub(r"[\s，,、“”\"'）)：:】\]]+", "", s)
    if "·" in s:
        parts = s.split("·")
        if len(parts) >= 2:
            s = parts[-2].strip()[-3:] + "·" + parts[-1].strip()[:6]
    return s.strip()


def clean_title(raw: str) -> str:
    s = (raw or "").strip()
    s = re.sub(r"^(?:关于|论)\s*", "", s)
    s = re.sub(r"\s*(?:（[^）]+）|\([^)]+\))$", "", s)
    return s.strip()


class TestCitationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SANDBOX_PATH, "r", encoding="utf-8") as f:
            cls.sandbox_concepts = json.load(f)["concepts"]

    def extract_citations(self, text: str):
        content = text or ""
        found = []
        seen_titles = set()

        re_author_book = re.compile(
            r"(?:由|据|正如|如|在|根据)?\s*([·\u4e00-\u9fa5A-Za-z\s]{2,20}?)\s*(?:先生|教授|学者)?\s*(?:所著(?:的)?|在|于|的)?\s*《([^》\n]{2,60})》"
        )
        for m in re_author_book.finditer(content):
            author = clean_author(m.group(1))
            title = clean_title(m.group(2))
            if len(author) >= 2 and len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "pattern": "AUTHOR_IN_BOOK",
                    "index": m.start()
                })

        re_book_author_year = re.compile(
            r"《([^》\n]{2,60})》\s*(?:（|\()\s*([·\u4e00-\u9fa5A-Za-z\s]{2,20}?)\s*(?:[，,]\s*(\d{3,4}(?:\s*BC)?))?\s*(?:）|\))"
        )
        for m in re_book_author_year.finditer(content):
            title = clean_title(m.group(1))
            author = clean_author(m.group(2))
            if len(author) >= 2 and len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "year": (m.group(3) or "").strip(),
                    "pattern": "BOOK_WITH_META",
                    "index": m.start()
                })

        re_book = re.compile(r"《([^》\n]{2,60})》")
        for m in re_book.finditer(content):
            title = clean_title(m.group(1))
            if len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                start = max(0, m.start() - 30)
                pre = content[start:m.start()]
                m_pre = re.search(r"(?:由|在|据)?\s*([·\u4e00-\u9fa5]{2,6})\s*(?:在|的|于|所著)?$", pre)
                author = clean_author(m_pre.group(1)) if m_pre else ""
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "pattern": "BARE_BOOK",
                    "index": m.start()
                })

        re_eng = re.compile(r'["“]([^"”\n]{2,60})["”]\s*(?:\(\s*([A-Za-z\s]{2,25})\s*(?:,\s*(\d{4}))?\s*\)|by\s+([A-Za-z\s]{2,25}))', re.IGNORECASE)
        for m in re_eng.finditer(content):
            title = clean_title(m.group(1))
            author = clean_author(m.group(2) or m.group(4) or "")
            if len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "year": m.group(3) or "",
                    "pattern": "ENGLISH_QUOTE",
                    "index": m.start()
                })

        return found

    def match_concept(self, title: str):
        q = title.lower()
        for c in self.sandbox_concepts:
            ca = c.get("canon_anchor") or {}
            at = (ca.get("title") or "").lower()
            cz = (c.get("name_zh") or "").lower()
            ce = (c.get("name_en") or "").lower()
            if q in at or at in q or q in cz or q in ce:
                return c
            if q == "国富论" and "wealth of nations" in at:
                return c
            if q == "资本论" and "das kapital" in at:
                return c
            if q == "纯粹理性批判" and "reinen vernunft" in at:
                return c
            if q == "正义论" and "theory of justice" in at:
                return c
            if q == "利维坦" and "leviathan" in at:
                return c
            if q == "经济与社会" and "wirtschaft und gesellschaft" in at:
                return c
        return None

    def audit_citations(self, text: str):
        cites = self.extract_citations(text)
        results = []
        exact_cnt = 0
        supports_cnt = 0
        qualifies_cnt = 0
        contradicts_cnt = 0
        suspect_cnt = 0
        unindexed_cnt = 0

        for item in cites:
            c = self.match_concept(item["title"])
            if not c:
                unindexed_cnt += 1
                results.append({
                    "raw_citation": item["raw_citation"],
                    "extracted_title": item["title"],
                    "extracted_author": item["author"],
                    "verdict": "UNINDEXED_OR_HALLUCINATED",
                    "verdict_zh": "⚪ 离线沙盒未收录（疑似 AI 幻觉编造引文或需全库检索）",
                    "confidence_score": 0.20,
                    "notes": f"未在内置的 50 篇离线正典沙盒中检索到《{item['title']}》。"
                })
                continue

            ca = c.get("canon_anchor") or {}
            true_author = ((ca.get("author") or "") + " " + (c.get("primary_thinker") or "")).lower()

            if item["author"]:
                a_norm = item["author"].lower()
                parts = re.split(r"[·•\s]+", a_norm)
                author_hit = any(len(p) > 1 and p in true_author for p in parts)
                if not author_hit:
                    suspect_cnt += 1
                    results.append({
                        "raw_citation": item["raw_citation"],
                        "extracted_title": item["title"],
                        "extracted_author": item["author"],
                        "verdict": "ATTRIBUTION_SUSPECT",
                        "verdict_zh": f"🟡 疑似张冠李戴（著作真实，但著录著者不符）：《{ca.get('title')}》实际著者为『{ca.get('author') or c.get('primary_thinker')}』，而非『{item['author']}』！",
                        "confidence_score": 0.95,
                        "matched_concept_id": c.get("concept_id"),
                        "canonical_title": ca.get("title"),
                        "canonical_author": ca.get("author") or c.get("primary_thinker"),
                        "canon_sha256": ca.get("canon_sha256")
                    })
                    continue

            # Context check
            w_start = max(0, item.get("index", 0) - 100)
            w_end = min(len(text), item.get("index", 0) + 150)
            context = text[w_start:w_end]

            matched_dispute = None
            for d in c.get("dialectical_disputes") or []:
                d_kw = re.split(r"[\s·]", re.split(r"[：:‘'“\"]", d[:15])[0])
                if any(len(kw) >= 2 and kw in context for kw in d_kw):
                    matched_dispute = d
                    break

            if matched_dispute:
                qualifies_cnt += 1
                results.append({
                    "raw_citation": item["raw_citation"],
                    "extracted_title": item["title"],
                    "extracted_author": item["author"],
                    "verdict": "QUALIFIES",
                    "verdict_zh": "⚖️ 学派辩证张力（正典包含对应限定或交锋论述）",
                    "confidence_score": 0.92,
                    "matched_concept_id": c.get("concept_id"),
                    "canonical_title": ca.get("title"),
                    "canonical_author": ca.get("author") or c.get("primary_thinker"),
                    "canon_sha256": ca.get("canon_sha256"),
                    "chapter_anchor": ca.get("chapter_anchor"),
                    "dialectical_dispute": matched_dispute
                })
            else:
                excerpt = ca.get("verbatim_excerpt") or ""
                is_exact = bool(excerpt and any(len(seg) >= 6 and seg in excerpt for seg in re.split(r"[,，。；;]", context)))
                if is_exact:
                    exact_cnt += 1
                else:
                    supports_cnt += 1

                results.append({
                    "raw_citation": item["raw_citation"],
                    "extracted_title": item["title"],
                    "extracted_author": item["author"],
                    "verdict": "EXACT_MATCH" if is_exact else "SUPPORTS",
                    "verdict_zh": "🟢 权威原典字句确证（256 位 SHA-256 版本存证）" if is_exact else "🟢 权威学术正典思想支持",
                    "confidence_score": 0.99 if is_exact else 0.95,
                    "matched_concept_id": c.get("concept_id"),
                    "canonical_title": ca.get("title"),
                    "canonical_author": ca.get("author") or c.get("primary_thinker"),
                    "canon_year": ca.get("year"),
                    "canon_sha256": ca.get("canon_sha256"),
                    "chapter_anchor": ca.get("chapter_anchor"),
                    "verbatim_excerpt": ca.get("verbatim_excerpt")
                })

        total = len(results)
        grounded_total = exact_cnt + supports_cnt + qualifies_cnt
        health_score = round(((grounded_total * 100) + (suspect_cnt * 30)) / total) if total > 0 else 100

        return {
            "status": "ok",
            "mode": "offline_golden_sandbox_50",
            "total_citations_extracted": total,
            "exact_matches_count": exact_cnt,
            "supports_count": supports_cnt,
            "qualifies_count": qualifies_cnt,
            "contradicts_count": contradicts_cnt,
            "suspect_count": suspect_cnt,
            "unindexed_count": unindexed_cnt,
            "citation_health_score": health_score,
            "citations": results
        }

    def test_citation_checks(self):
        t1 = self.audit_citations("正如亚当·斯密在《国富论》中指出分工能极大提高生产率...")
        self.assertEqual(t1["total_citations_extracted"], 1)
        self.assertEqual(t1["citations"][0]["verdict"], "SUPPORTS")
        self.assertEqual(t1["citations"][0]["canonical_author"], "Adam Smith")

        t2 = self.audit_citations("正如著名经济学家凯恩斯在《国富论》中所强调...")
        self.assertEqual(t2["total_citations_extracted"], 1)
        self.assertEqual(t2["citations"][0]["verdict"], "ATTRIBUTION_SUSPECT")
        self.assertEqual(t2["suspect_count"], 1)

        t3 = self.audit_citations("在《纯粹理性批判》中，先验感性论探讨了时空形式...")
        self.assertEqual(t3["total_citations_extracted"], 1)
        self.assertEqual(t3["citations"][0]["matched_concept_id"], "VS-PHIL-001")

        t4 = self.audit_citations("在《纯粹理性批判》中探讨物自体，然而黑格尔绝对唯心主义批判物自体为抽象贫乏之物...")
        self.assertEqual(t4["total_citations_extracted"], 1)
        self.assertEqual(t4["citations"][0]["verdict"], "QUALIFIES")

        t5 = self.audit_citations("根据张三教授在《量子区块链元宇宙心智哲学导论》中的惊人论证...")
        self.assertEqual(t5["total_citations_extracted"], 1)
        self.assertEqual(t5["citations"][0]["verdict"], "UNINDEXED_OR_HALLUCINATED")
        self.assertEqual(t5["unindexed_count"], 1)


if __name__ == "__main__":
    unittest.main()
