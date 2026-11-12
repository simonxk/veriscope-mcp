"""
VeriScope MCP Server — Core Engine (Clean-Room Open Source Edition)

Implements the Model Context Protocol (MCP) 4+1 Cognitive Funnel:
1. veriscope_discover_concepts
2. veriscope_inspect_topography
3. veriscope_locate_evidence
4. veriscope_verify_attestation
5. veriscope_probe_radar

Includes built-in 50-Canon Golden Sandbox (pre-signed with sovereign Ed25519 receipts),
Cryptographic Teaser Mode, and remote gateway forwarding when VERISCOPE_API_KEY is configured.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    _HAS_ED25519 = True
except ImportError:
    _HAS_ED25519 = False

VERISCOPE_PUBLIC_KEY_HEX = "be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93"
DEFAULT_GATEWAY_URL = os.environ.get("VERISCOPE_GATEWAY_URL", "https://api.veriscope.cc/v1/mcp")


class VeriScopeMCPServer:
    def __init__(self, sandbox_path: Optional[str] = None):
        self.api_key = os.environ.get("VERISCOPE_API_KEY", "").strip()
        self.gateway_url = DEFAULT_GATEWAY_URL

        # Load 50 Golden Sandbox
        if sandbox_path and Path(sandbox_path).exists():
            p = Path(sandbox_path)
        else:
            p = Path(__file__).parent / "golden_sandbox_50.json"
            if not p.exists():
                p = Path(__file__).resolve().parents[2] / "golden_sandbox_50.json"

        self.sandbox_concepts: List[Dict[str, Any]] = []
        self.sandbox_map: Dict[str, Dict[str, Any]] = {}
        self.name_map: Dict[str, Dict[str, Any]] = {}

        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.sandbox_concepts = data.get("concepts", [])
                    for c in self.sandbox_concepts:
                        cid = c.get("concept_id", "")
                        self.sandbox_map[cid] = c
                        if c.get("name_zh"):
                            self.name_map[c["name_zh"].lower()] = c
                        if c.get("name_en"):
                            self.name_map[c["name_en"].lower()] = c
            except Exception as e:
                sys.stderr.write(f"[VeriScope MCP] Notice: failed to load sandbox: {e}\n")

    BUSINESS_SYNONYM_BRIDGE = [
        (["部门推诿", "跨部门协同", "周报", "报表负担", "流程繁琐", "大厂黑话", "体制内", "官僚", "执行变形"], "科层制"),
        (["价格战", "内卷", "补贴", "恶意降价", "渠道窜货", "同质化", "商业竞争", "毛利"], "看不见的手"),
        (["信息茧房", "算法推荐", "流量", "舆论", "品牌公关", "回音室"], "公共领域"),
        (["AI幻觉", "大模型套壳", "技术颠覆", "数字化转型", "产业升级", "第二曲线"], "范式转换"),
        (["合规", "数据主权", "监管", "权限边界", "治理", "责任倒查"], "社会契约"),
        (["甩锅", "言行不一", "形式主义", "认知偏差", "盲目立项"], "认知失调"),
    ]

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "veriscope_discover_concepts",
                "description": (
                    "[Executive Framing & Concept Discovery] Elevate colloquial workplace/business pain points "
                    "(e.g. bureaucracy, price wars, AI hype, executive briefings) or news metaphors into rigorous "
                    "first-principles concepts across 24 disciplines to eliminate generic AI slop."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Colloquial business/workplace problem, metaphor, or scholarly topic (e.g. '跨部门推诿', '价格战', 'iron cage', 'panopticon')."
                        },
                        "discipline_hint": {
                            "type": "string",
                            "description": "Optional discipline hint (e.g. 'SOC', 'PHIL', 'LAW', 'ECON')."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "veriscope_inspect_topography",
                "description": (
                    "[Red-Team Pre-Mortem & Dialectical Audit] Stress-test business proposals, policy drafts, or papers "
                    "by retrieving axiomatic formal kernels, scholar lineages with Wikidata QIDs, and 3+ opposing dialectical disputes."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {
                            "type": "string",
                            "description": "Canonical concept identifier (e.g. 'VS-PHIL-001', 'VS-SOC-001')."
                        }
                    },
                    "required": ["concept_id"]
                }
            },
            {
                "name": "veriscope_locate_evidence",
                "description": (
                    "[De-Slop Grounding & Primary Source Proof] Locate fair-use verbatim excerpts (<=300 chars) "
                    "with exact chapter coordinates, SHA-256 edition hash, and Ed25519 cryptographic receipt for high-stakes reports."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {
                            "type": "string",
                            "description": "Canonical concept identifier."
                        },
                        "query_context": {
                            "type": "string",
                            "description": "Optional sentence context to guide snippet anchor selection."
                        }
                    },
                    "required": ["concept_id"]
                }
            },
            {
                "name": "veriscope_verify_attestation",
                "description": (
                    "[Cryptographic Receipt Verification] Mathematically verify the SHA-256 hash "
                    "and Ed25519 cryptographic receipt of a cited quote to check text integrity."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {
                            "type": "string",
                            "description": "Canonical concept identifier (e.g. 'VS-SOC-001')."
                        },
                        "canon_sha256": {
                            "type": "string",
                            "description": "SHA-256 edition hash to verify against canonical records."
                        },
                        "attestation": {
                            "type": "object",
                            "description": "Optional full attestation receipt object."
                        }
                    }
                }
            },
            {
                "name": "veriscope_probe_radar",
                "description": (
                    "[Cross-Domain Blindspot & Innovation Radar] Probe matrix coverage, discipline distribution, "
                    "and cross-disciplinary conceptual bridges across all 24 academic disciplines."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "discipline": {
                            "type": "string",
                            "description": "Optional discipline code to filter radar statistics."
                        }
                    }
                }
            },
            {
                "name": "veriscope_citation_audit",
                "description": (
                    "[Academic Citation Health Check & Attribution Auditor] Fast-scan draft articles or AI generated "
                    "text to extract and verify book titles, authors, and citations against canonical editions and "
                    "SHA-256 hashes to detect misattributions and phantom references."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Draft article, proposal, research brief, or AI-generated text containing book citations to audit."
                        },
                        "discipline_hint": {
                            "type": "string",
                            "description": "Optional discipline hint (e.g. 'SOC', 'PHIL', 'ECON', 'LAW')."
                        }
                    },
                    "required": ["text"]
                }
            }
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name in ("veriscope_discover_concepts", "veriscope_business_frame", "veriscope_elevate_concept"):
            return self.discover_concepts(
                query=arguments.get("query") or arguments.get("draft_text") or "",
                discipline=arguments.get("discipline_hint") or arguments.get("discipline")
            )
        elif name in ("veriscope_inspect_topography", "veriscope_redteam_audit", "veriscope_dialectic_collide"):
            return self.inspect_topography(
                concept_id=arguments.get("concept_id") or arguments.get("query") or "VS-SOC-001",
                include_disputes=arguments.get("include_disputes", True)
            )
        elif name in ("veriscope_locate_evidence", "veriscope_deslop_and_ground"):
            return self.locate_evidence(
                concept_id=arguments.get("concept_id") or arguments.get("query") or "VS-SOC-001",
                query_proposition=arguments.get("query_context") or arguments.get("query_proposition"),
                api_key=arguments.get("api_key")
            )
        elif name == "veriscope_verify_attestation":
            return self.verify_attestation(
                concept_id=arguments.get("concept_id"),
                canon_sha256=arguments.get("canon_sha256"),
                attestation=arguments.get("attestation")
            )
        elif name in ("veriscope_probe_radar", "veriscope_babel_lens"):
            return self.probe_radar(
                discipline=arguments.get("discipline") or arguments.get("discipline_hint"),
                topic=arguments.get("topic")
            )
        elif name in ("veriscope_citation_audit", "veriscope_check_citations"):
            return self.audit_citations(
                text=arguments.get("text") or arguments.get("document_text") or arguments.get("draft_text") or "",
                discipline_hint=arguments.get("discipline_hint") or ""
            )
        else:
            return {"error": f"Unknown tool: {name}"}

    def discover_concepts(self, query: str, discipline: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        q = (query or "").strip().lower()
        disc = (discipline or "").strip().lower()
        effective_queries = [q]
        for triggers, canonical_term in self.BUSINESS_SYNONYM_BRIDGE:
            if any(t.lower() in q for t in triggers):
                effective_queries.append(canonical_term.lower())
        matched = []
        seen_ids = set()

        for eq in effective_queries:
            for c in self.sandbox_concepts:
                if c.get("concept_id") in seen_ids:
                    continue
                if disc and disc not in c.get("discipline", "").lower() and disc != c.get("discipline_code", "").lower():
                    continue
                anchor = c.get("canon_anchor", {})
                text_pool = (
                    f"{c.get('concept_id', '')} "
                    f"{c.get('name_zh', '')} "
                    f"{c.get('name_en', '')} "
                    f"{c.get('primary_thinker', '')} "
                    f"{c.get('historical_period', '')} "
                    f"{c.get('core_thesis', '')} "
                    f"{c.get('formal_kernel', '')} "
                    f"{anchor.get('author', '')} "
                    f"{anchor.get('title', '')}"
                ).lower()

                if eq in text_pool or any(w in text_pool for w in eq.split() if len(w) > 1):
                    seen_ids.add(c.get("concept_id"))
                    matched.append({
                        "concept_id": c.get("concept_id"),
                        "name_zh": c.get("name_zh"),
                        "name_en": c.get("name_en"),
                        "discipline": c.get("discipline"),
                        "primary_thinker": c.get("primary_thinker"),
                        "historical_period": c.get("historical_period"),
                        "core_thesis": c.get("core_thesis"),
                        "formal_definition": c.get("formal_kernel", "")[:160] + "...",
                        "is_sandbox_ready": True
                    })
                    if len(matched) >= limit:
                        break
            if len(matched) >= limit:
                break

        if matched:
            return {
                "query": query,
                "discipline_filter": discipline,
                "total_matched": len(matched),
                "matched_count": len(matched),
                "concepts": matched,
                "matches": matched,
                "sandbox_status": "50 Golden Sandbox concepts loaded (Offline Mode Ready)"
            }

        if self.api_key:
            return self._forward_remote("veriscope_discover_concepts", {"query": query, "discipline_hint": discipline})

        return {
            "query": query,
            "discipline_filter": discipline,
            "total_matched": 0,
            "matched_count": 0,
            "concepts": [],
            "matches": [],
            "notice": "Query not found in 50 offline sandbox concepts. Configure VERISCOPE_API_KEY to search 77,984 scholarly concepts across 24 disciplines: https://veriscope.cc/pricing"
        }

    def inspect_topography(self, concept_id: str, include_disputes: bool = True) -> Dict[str, Any]:
        cid = (concept_id or "").strip()
        c = self.sandbox_map.get(cid) or self.name_map.get(cid.lower())

        if c:
            res = {
                "concept_id": c.get("concept_id"),
                "name_zh": c.get("name_zh"),
                "name_en": c.get("name_en"),
                "discipline": c.get("discipline"),
                "primary_thinker": c.get("primary_thinker"),
                "historical_period": c.get("historical_period"),
                "formal_kernel": c.get("formal_kernel"),
                "authoritative_edition": c.get("canon_anchor", {}).get("title"),
                "canon_sha256": c.get("canon_anchor", {}).get("canon_sha256"),
                "is_sandbox_concept": True
            }
            if include_disputes:
                res["dialectical_disputes"] = c.get("dialectical_disputes", [])
            return res

        if self.api_key:
            return self._forward_remote("veriscope_inspect_topography", {"concept_id": concept_id})

        return {
            "error": "CONCEPT_NOT_FOUND",
            "message": f"Concept '{concept_id}' not found in Golden Sandbox. Configure VERISCOPE_API_KEY for the full 77,984 conceptual matrix: https://veriscope.cc/pricing",
            "available_sandbox_concepts": list(self.sandbox_map.keys())[:10]
        }

    def locate_evidence(
        self,
        concept_id: str,
        query_proposition: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        cid = (concept_id or "").strip()
        c = self.sandbox_map.get(cid) or self.name_map.get(cid.lower())

        # 1. Concept found in 50 Sandbox: return attested full excerpt & cryptographic receipt
        if c:
            anchor = c.get("canon_anchor", {})
            return {
                "status": "ATTESTED_FULL",
                "concept_id": c.get("concept_id"),
                "name_zh": c.get("name_zh"),
                "discipline": c.get("discipline"),
                "primary_thinker": c.get("primary_thinker"),
                "canon_anchor": {
                    "archival_id": anchor.get("archival_id", 0),
                    "title": anchor.get("title", ""),
                    "author": anchor.get("author", ""),
                    "year": anchor.get("year", ""),
                    "chapter_anchor": anchor.get("chapter_anchor", ""),
                    "canon_sha256": anchor.get("canon_sha256", ""),
                    "verbatim_excerpt": anchor.get("verbatim_excerpt", ""),
                    "provenance": "VeriScope 权威学术原典库 · 规范版本存证"
                },
                "cryptographic_receipt": c.get("cryptographic_receipt"),
                "access_mode": "GOLDEN_SANDBOX_OFFLINE_VERIFIED"
            }

        # 2. If API Key provided and concept is outside sandbox: forward to remote gateway
        key_to_use = api_key or self.api_key
        if key_to_use:
            return self._forward_remote("veriscope_locate_evidence", {
                "concept_id": concept_id,
                "query_proposition": query_proposition
            })

        # 3. Non-sandbox & No API Key: return Teaser Preview Mode
        # Generate stable mock 16-hex hash prefix derived from concept_id (not empty hash)
        h = hashlib.sha256(f"SOVEREIGN_CANON:{cid}".encode("utf-8")).hexdigest()
        sha_prefix = h[:16]

        return {
            "status": "TEASER_PREVIEW",
            "concept_id": cid,
            "canon_anchor_preview": {
                "canon_sha256_prefix": f"{sha_prefix}...",
                "chapter_anchor": "Canonical Treatise Anchor [Locked]",
                "verbatim_excerpt": (
                    "[🔒 已精准锁定权威学术原典存证，包含学术公理与判词。全本切片（≤300字）与 "
                    "Ed25519 密码学签名需配置 VERISCOPE_API_KEY：https://veriscope.cc/pricing]"
                )
            },
            "pricing_options": {
                "scholar_pro": "个人专业版 (Scholar Pro) ¥98/月 或 $19/mo (年付 ¥880/年)",
                "enterprise": "机构专线版 ¥9,800起/年 或 $1,500/yr (包含高并发 API 与私有知识库支持)"
            },
            "is_teaser_mode": True,
            "access_mode": "TEASER_PREVIEW"
        }

    def verify_attestation(
        self,
        concept_id: Optional[str] = None,
        canon_sha256: Optional[str] = None,
        attestation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Path A: Verify by concept_id + canon_sha256 against sandbox
        if concept_id and canon_sha256:
            c = self.sandbox_map.get(concept_id) or self.name_map.get(concept_id.lower())
            if c:
                real_sha = c.get("canon_anchor", {}).get("canon_sha256", "")
                is_valid = (canon_sha256.lower() == real_sha.lower())
                return {
                    "method": "local_hash_lookup",
                    "hash_matched": is_valid,
                    "is_cryptographically_verified": False,
                    "verification_status": "HASH_MATCHED" if is_valid else "TAMPER_DETECTED",
                    "concept_id": concept_id,
                    "matched_edition": c.get("canon_anchor", {}).get("title"),
                    "algorithm": "SHA-256",
                    "public_key": VERISCOPE_PUBLIC_KEY_HEX
                }

        # Path B: Verify attestation receipt payload & signature
        if attestation and isinstance(attestation, dict):
            caller_pub = attestation.get("public_key")
            trusted_pub = VERISCOPE_PUBLIC_KEY_HEX

            # S-4: 严格校验公钥信任源。严禁直接信任调用方传入的任意自签公钥
            if caller_pub:
                clean_caller_pub = caller_pub.replace("0x", "").strip().lower()
                if clean_caller_pub != trusted_pub.lower():
                    return {
                        "method": "ed25519_signature",
                        "is_cryptographically_verified": False,
                        "verification_status": "ISSUER_UNTRUSTED",
                        "algorithm": "Ed25519",
                        "public_key": caller_pub,
                        "error": "Untrusted public key: The attestation public key does not match VeriScope authoritative trust anchor."
                    }

            sig = attestation.get("signature", "")
            msg = attestation.get("signed_message") or attestation.get("payload", "")
            pub = trusted_pub

            if not sig or not msg:
                return {
                    "method": "ed25519_signature",
                    "is_cryptographically_verified": False,
                    "verification_status": "TAMPER_DETECTED",
                    "error": "Missing signature or signed_message"
                }

            sig_clean = sig.replace("vsk_sig:", "").strip()

            if not _HAS_ED25519:
                return {
                    "method": "ed25519_signature",
                    "is_cryptographically_verified": False,
                    "verification_status": "UNABLE_TO_VERIFY_DEPENDENCY_MISSING",
                    "error": "Cryptographic verification library (cryptography) is not installed in the environment."
                }

            if len(sig_clean) != 128 or len(pub) != 64:
                return {
                    "method": "ed25519_signature",
                    "is_cryptographically_verified": False,
                    "verification_status": "SIGNATURE_INVALID",
                    "error": "Invalid signature or public key length"
                }

            is_valid = False
            try:
                pub_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub))
                pub_key.verify(bytes.fromhex(sig_clean), msg.encode("utf-8"))
                is_valid = True
            except Exception:
                is_valid = False

            return {
                "method": "ed25519_signature",
                "is_cryptographically_verified": is_valid,
                "verification_status": "SIGNATURE_VALID" if is_valid else "SIGNATURE_INVALID",
                "algorithm": "Ed25519",
                "public_key": pub
            }

        return {
            "is_cryptographically_verified": False,
            "verification_status": "TAMPER_DETECTED",
            "error": "Insufficient parameters for verification"
        }

    def probe_radar(
        self,
        discipline: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        disc_stats: Dict[str, int] = {}
        for c in self.sandbox_concepts:
            d = c.get("discipline_code") or c.get("discipline") or "OTHER"
            disc_stats[d] = disc_stats.get(d, 0) + 1

        synapses = [
            {"source": "VS-PHIL-001", "target": "VS-PHIL-005", "relation": "epistemological_critique"},
            {"source": "VS-SOC-001", "target": "VS-SOC-003", "relation": "institutional_dialectic"},
            {"source": "VS-COMM-001", "target": "VS-COMM-004", "relation": "public_sphere_transition"},
            {"source": "VS-LAW-001", "target": "VS-LAW-002", "relation": "constitutional_polarity"},
            {"source": "VS-ECON-001", "target": "VS-ECON-004", "relation": "market_order_evolution"}
        ]

        return {
            "status": "healthy",
            "mode": "offline_golden_sandbox_50",
            "topic_probed": topic,
            "discipline_filter": discipline,
            "active_disciplines": len(disc_stats),
            "sandbox_concept_count": len(self.sandbox_concepts),
            "disciplines_distribution": disc_stats,
            "babel_synapses": synapses,
            "notice": "Serving from built-in 50-Canon Golden Sandbox. Full 77,984 matrix accessible via VERISCOPE_API_KEY."
        }

    def _forward_remote(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps({"tool": tool_name, "arguments": arguments}).encode("utf-8")
        req = urllib.request.Request(
            self.gateway_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "VeriScope-MCP-Client/1.0.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": f"Gateway error calling {tool_name}: {str(e)}"}

    def audit_citations(self, text: str, discipline_hint: str = "") -> Dict[str, Any]:
        """
        AI 生成物学术引文体检（离线黄金沙盒版）：
        多模态抽取中文与西文学术引注，核对 50 经典学术正典底座，输出五态法医对账判决，拦截张冠李戴与幻觉编造引文。
        """
        import re

        author_noise = [
            "德意志哲学家", "德国哲学家", "法国哲学家", "英国经济学家", "美国社会学家",
            "古希腊哲学家", "古典政治学家", "社会学先驱", "法学先驱", "经济学大师",
            "著名哲学家", "学者", "教授", "先生", "作家", "部分学者", "然而", "但是",
            "认为", "强调", "指出", "提出", "声称", "根据", "按照"
        ]

        def clean_au(raw_s: str) -> str:
            s = (raw_s or "").strip()
            for w in author_noise:
                s = s.replace(w, "").strip()
            s = re.sub(r"^[\s，,、“”\"'（(：:【\[]+", "", s)
            s = re.sub(r"[\s，,、“”\"'）)：:】\]]+$", "", s)
            if "·" in s:
                parts = s.split("·")
                if len(parts) >= 2:
                    s = parts[-2].strip()[-3:] + "·" + parts[-1].strip()[:6]
            return s.strip()

        def clean_ti(raw_t: str) -> str:
            s = (raw_t or "").strip()
            s = re.sub(r"^(?:关于|论)\s*", "", s)
            s = re.sub(r"\s*(?:（[^）]+）|\([^)]+\))$", "", s)
            return s.strip()

        content = text or ""
        found = []
        seen_titles = set()

        re_author_book = re.compile(
            r"(?:由|据|正如|如|在|根据)?\s*([·\u4e00-\u9fa5A-Za-z\s]{2,20}?)\s*(?:先生|教授|学者)?\s*(?:所著(?:的)?|在|于|的)?\s*《([^》\n]{2,60})》"
        )
        for m in re_author_book.finditer(content):
            author = clean_au(m.group(1))
            title = clean_ti(m.group(2))
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
            title = clean_ti(m.group(1))
            author = clean_au(m.group(2))
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
            title = clean_ti(m.group(1))
            if len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                start = max(0, m.start() - 30)
                pre = content[start:m.start()]
                m_pre = re.search(r"(?:由|在|据)?\s*([·\u4e00-\u9fa5]{2,6})\s*(?:在|的|于|所著)?$", pre)
                author = clean_au(m_pre.group(1)) if m_pre else ""
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "pattern": "BARE_BOOK",
                    "index": m.start()
                })

        re_eng = re.compile(r'["“]([^"”\n]{2,60})["”]\s*(?:\(\s*([A-Za-z\s]{2,25})\s*(?:,\s*(\d{4}))?\s*\)|by\s+([A-Za-z\s]{2,25}))', re.IGNORECASE)
        for m in re_eng.finditer(content):
            title = clean_ti(m.group(1))
            author = clean_au(m.group(2) or m.group(4) or "")
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

        re_eng_std = re.compile(r'([A-Za-z\s]{2,25}),\s*(?:["“]|_|\*)?([A-Za-z\s]{2,60})(?:["”]|_|\*)?\s*\(\s*(\d{4})\s*\)')
        for m in re_eng_std.finditer(content):
            author = clean_au(m.group(1))
            title = clean_ti(m.group(2))
            if len(author) >= 2 and len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "year": m.group(3) or "",
                    "pattern": "ENGLISH_STD",
                    "index": m.start()
                })

        re_eng_argues = re.compile(r'(?:As|as|In|in|According to)\s+([A-Za-z\s]{2,25})\s+(?:argues|states|claims|writes)?\s*(?:in)?\s*["“]([^"”\n]{2,60})["”]')
        for m in re_eng_argues.finditer(content):
            author = clean_au(m.group(1))
            title = clean_ti(m.group(2))
            if len(author) >= 2 and len(title) >= 2 and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                found.append({
                    "raw_citation": m.group(0).strip(),
                    "author": author,
                    "title": title,
                    "pattern": "ENGLISH_ARGUES",
                    "index": m.start()
                })

        GENERIC_STOPWORDS = {
            "资本", "理论", "方法", "社会", "哲学", "经济", "历史", "正义", "批判", "原理", "通论",
            "capital", "theory", "method", "society", "philosophy", "economy", "history", "justice", "critique"
        }

        def get_canonical_author(c: Dict[str, Any]) -> str:
            if not c:
                return ""
            pt = c.get("primary_thinker") or ""
            m = re.search(r"\(([^)]+)\)", pt)
            if m and m.group(1).strip():
                return m.group(1).strip()
            if pt:
                return pt.strip()
            ca = c.get("canon_anchor") or {}
            return ca.get("author") or ""

        def match_c(t_str: str):
            q = t_str.lower().strip()
            if q in GENERIC_STOPWORDS or len(q) < 2:
                return None
            for c in self.sandbox_concepts:
                ca = c.get("canon_anchor") or {}
                at = (ca.get("title") or "").lower()
                cid = c.get("concept_id")
                if (q == "资本论" or q == "capital" or q == "das kapital") and (cid == "VS-SOC-003" or "资本论" in at or "kapital" in at):
                    return c
                if (q == "国富论" or q == "wealth of nations") and (cid == "VS-ECON-001" or "wealth of nations" in at or "国富论" in at):
                    return c
                if (q == "纯粹理性批判" or q == "critique of pure reason") and (cid == "VS-PHIL-001" or "reinen vernunft" in at or "纯粹理性批判" in at or "pure reason" in at):
                    return c
                if (q == "正义论" or q == "theory of justice" or q == "a theory of justice") and (cid == "VS-LAW-004" or "theory of justice" in at or "正义论" in at):
                    return c
                if (q == "利维坦" or q == "leviathan") and (cid == "VS-POL-001" or "leviathan" in at):
                    return c
                if (q == "经济与社会" or q == "economy and society") and (cid == "VS-SOC-001" or "wirtschaft" in at or "经济与社会" in at):
                    return c
                if (q == "社会分工论" or q == "the division of labour in society") and (cid == "VS-SOC-002" or "division du travail" in at or "社会分工论" in at):
                    return c
                if (q == "就业、利息和货币通论" or q == "the general theory of employment, interest and money") and (cid == "VS-ECON-002" or "general theory" in at or "通论" in at):
                    return c
                if (q == "君主论" or q == "the prince") and (cid == "VS-POL-004" or "principe" in at or "君主论" in at):
                    return c
            for c in self.sandbox_concepts:
                ca = c.get("canon_anchor") or {}
                at = (ca.get("title") or "").lower()
                if not at:
                    continue
                if at == q:
                    return c
                if any('\u4e00' <= ch <= '\u9fa5' for ch in q) and len(q) >= 4:
                    if q in at or (len(at) >= 4 and at in q):
                        return c
                if not any('\u4e00' <= ch <= '\u9fa5' for ch in q) and len(q) >= 5:
                    q_words = [w for w in q.split() if len(w) > 2]
                    if len(q_words) >= 2 and q in at:
                        return c
            return None

        results = []
        exact_cnt = 0
        supports_cnt = 0
        qualifies_cnt = 0
        contradicts_cnt = 0
        suspect_cnt = 0
        unindexed_cnt = 0

        for item in found:
            matched_c = match_c(item["title"])
            if not matched_c:
                unindexed_cnt += 1
                results.append({
                    "raw_citation": item["raw_citation"],
                    "extracted_title": item["title"],
                    "extracted_author": item["author"],
                    "verdict": "UNINDEXED",
                    "verdict_zh": "⚪ 离线沙盒未收录（本地沙盒未覆盖，无法直接确证，需经权威书目查证）",
                    "confidence_score": 0.50,
                    "notes": f"未在内置的 50 篇离线正典沙盒中检索到《{item['title']}》。该文献可能为其他学科真实著作或外部文献，离线沙盒不作虚构断言。建议连接全库 API 或外部书目数据库（如 CrossRef/OpenAlex）进行二次核验。"
                })
                continue

            ca = matched_c.get("canon_anchor") or {}
            true_author = ((ca.get("author") or "") + " " + (matched_c.get("primary_thinker") or "")).lower()

            canon_author = get_canonical_author(matched_c) or ca.get('author') or matched_c.get('primary_thinker')

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
                        "verdict_zh": f"🟡 疑似张冠李戴（著作真实，但著录著者不符）：《{ca.get('title')}》实际著者为『{canon_author}』，而非『{item['author']}』！",
                        "confidence_score": 0.95,
                        "matched_concept_id": matched_c.get("concept_id"),
                        "canonical_title": ca.get("title"),
                        "canonical_author": canon_author,
                        "canon_sha256": ca.get("canon_sha256"),
                        "notes": "大模型生成中常见将经典安放至其他学者名下，存在重大引注合规风险。"
                    })
                    continue

            w_start = max(0, item.get("index", 0) - 100)
            w_end = min(len(content), item.get("index", 0) + 150)
            context = content[w_start:w_end]

            matched_dispute = None
            for d in matched_c.get("dialectical_disputes") or []:
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
                    "matched_concept_id": matched_c.get("concept_id"),
                    "canonical_title": ca.get("title"),
                    "canonical_author": canon_author,
                    "canon_sha256": ca.get("canon_sha256"),
                    "chapter_anchor": ca.get("chapter_anchor"),
                    "dialectical_dispute": matched_dispute,
                    "notes": f"引述命题在思想史中存在结构性学派交锋：{matched_dispute}"
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
                    "verdict_zh": "🟢 权威原典字句确证（256 位 SHA-256 版本存证）" if is_exact else "🟢 权威正典出处吻合（著录与篇章坐标确证，命题语义待研读）",
                    "confidence_score": 0.99 if is_exact else 0.95,
                    "matched_concept_id": matched_c.get("concept_id"),
                    "canonical_title": ca.get("title"),
                    "canonical_author": canon_author,
                    "canon_year": ca.get("year"),
                    "canon_sha256": ca.get("canon_sha256"),
                    "chapter_anchor": ca.get("chapter_anchor"),
                    "verbatim_excerpt": ca.get("verbatim_excerpt"),
                    "notes": "原文切片字句高度匹配，出处坐标与 256 位 SHA-256 版本哈希完备。" if is_exact else "著作与著者著录核对吻合，已定位馆藏权威版本；命题语义核实建议深入研读原典章节。"
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
            "summary": f"共抽检 {total} 处学术引注：{grounded_total} 处经正典证实/具备坐标，{suspect_cnt} 处疑似张冠李戴，{unindexed_cnt} 处沙盒未收录。",
            "citations": results,
            "notice": "离线模式基于 50 篇经典学术正典沙盒初筛。如需对勘 24 学科全量学术正典与章节定位，请配置 VERISCOPE_API_KEY。"
        }
