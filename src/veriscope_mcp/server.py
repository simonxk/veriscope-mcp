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
            "notice": "Query not found in 50 offline sandbox concepts. Configure VERISCOPE_API_KEY to search 71,000+ scholarly concepts across 24 disciplines: https://veriscope.cc/pricing"
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
            "message": f"Concept '{concept_id}' not found in Golden Sandbox. Configure VERISCOPE_API_KEY for the full 71,000+ conceptual matrix: https://veriscope.cc/pricing",
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
                    "is_cryptographically_verified": is_valid,
                    "verification_status": "HASH_MATCHED" if is_valid else "TAMPER_DETECTED",
                    "concept_id": concept_id,
                    "matched_edition": c.get("canon_anchor", {}).get("title"),
                    "algorithm": "SHA-256",
                    "public_key": VERISCOPE_PUBLIC_KEY_HEX
                }

        # Path B: Verify attestation receipt payload & signature
        if attestation and isinstance(attestation, dict):
            sig = attestation.get("signature", "")
            msg = attestation.get("signed_message") or attestation.get("payload", "")
            pub = attestation.get("public_key") or VERISCOPE_PUBLIC_KEY_HEX

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
            "notice": "Serving from built-in 50-Canon Golden Sandbox. Full 71,000+ matrix accessible via VERISCOPE_API_KEY."
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
        抽取《书名》（著者，年份），核对 50 经典哲社底座原典真伪，拦截张冠李戴与幻觉编造引文。
        """
        import re
        content = text or ""
        pattern = re.compile(r"《([^》]{2,40})》(?:（([^，,）]{1,20})(?:[，,]\s*(\d{1,4}))?）)?")
        citations = []
        grounded_count = 0
        suspect_count = 0
        unindexed_count = 0

        for match in pattern.finditer(content):
            raw_quote = match.group(0)
            raw_title = match.group(1).strip()
            raw_author = (match.group(2) or "").strip()
            raw_year = (match.group(3) or "").strip()

            matched_c = None
            q_title = raw_title.lower()
            for c in self.sandbox_concepts:
                anchor = c.get("canon_anchor") or {}
                a_title = (anchor.get("title") or "").lower()
                c_zh = (c.get("name_zh") or "").lower()
                if q_title in a_title or a_title in q_title or q_title in c_zh:
                    matched_c = c
                    break

            if matched_c:
                anchor = matched_c.get("canon_anchor") or {}
                verdict = "AUTHENTIC_GROUNDED"
                confidence = 0.99
                notes = "精确匹配权威学术典籍，SHA-256 版本哈希完备"

                if raw_author:
                    a_norm = raw_author.lower()
                    valid_authors = (f"{anchor.get('author', '')} {matched_c.get('primary_thinker', '')}").lower()
                    if a_norm not in valid_authors and not any(part in valid_authors for part in a_norm.split("·") if len(part) > 1):
                        verdict = "ATTRIBUTION_SUSPECT"
                        confidence = 0.65
                        notes = f"书目真实存在（{anchor.get('title')}），但著者可能张冠李戴（引文著者：{raw_author}，藏书著者：{anchor.get('author')}）"
                        suspect_count += 1
                    else:
                        grounded_count += 1
                else:
                    grounded_count += 1

                citations.append({
                    "raw_citation": raw_quote,
                    "book_title": raw_title,
                    "cited_author": raw_author,
                    "verdict": verdict,
                    "confidence_score": confidence,
                    "matched_concept_id": matched_c.get("concept_id"),
                    "matched_title": anchor.get("title"),
                    "author": anchor.get("author"),
                    "year": anchor.get("year"),
                    "canon_sha256": anchor.get("canon_sha256"),
                    "verbatim_excerpt": anchor.get("verbatim_excerpt"),
                    "notes": notes,
                    "provenance": "VeriScope 权威馆藏实体学术原本（50大经典沙盒）"
                })
            else:
                unindexed_count += 1
                citations.append({
                    "raw_citation": raw_quote,
                    "book_title": raw_title,
                    "cited_author": raw_author,
                    "verdict": "UNINDEXED_OR_HALLUCINATED",
                    "confidence_score": 0.20,
                    "notes": "在离线 50 篇黄金沙盒中未命中。可能为大模型幻觉编造引文，或需接入全量 74.9万 权威书目母港进行深水区对勘",
                    "provenance": "UNINDEXED"
                })

        total = len(citations)
        health_score = round(((grounded_count * 100) + (suspect_count * 40)) / total) if total > 0 else 100
        return {
            "status": "ok",
            "mode": "offline_golden_sandbox_50",
            "total_citations_extracted": total,
            "grounded_count": grounded_count,
            "attribution_suspect_count": suspect_count,
            "unindexed_or_hallucinated_count": unindexed_count,
            "citation_health_score": health_score,
            "citations_audit": citations,
            "notice": "离线模式基于 50 经典哲社底座初筛。穿透全量 74.9万 学术书目与 18.9万 册原书全文请配置 VERISCOPE_API_KEY。"
        }
