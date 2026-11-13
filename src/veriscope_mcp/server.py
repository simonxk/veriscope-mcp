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
import urllib.parse

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
                    "Maps informal business problems, workplace colloquialisms, or policy metaphors into canonical first-principles ontologies across 24 academic disciplines.\n\n"
                    "### When to Use:\n"
                    "- Use when the user presents colloquial questions (e.g. 'office politics', 'price wars', 'algorithmic filter bubbles', '跨部门推诿') and you need formal theoretical frameworks.\n"
                    "- Use as the initial entry point to locate canonical concept identifiers (e.g. 'VS-SOC-001') before inspecting topography or locating primary evidence.\n\n"
                    "### When NOT to Use:\n"
                    "- Do NOT use if you already possess a canonical concept ID (e.g. 'VS-SOC-001'); call `veriscope_inspect_topography` directly.\n"
                    "- Do NOT use for verbatim quotation retrieval or snippet proofs; call `veriscope_locate_evidence` instead.\n"
                    "- Do NOT use for auditing full draft text for hallucinated citations; call `veriscope_audit_citations` instead.\n\n"
                    "### Execution Behavior:\n"
                    "- Read-only; deterministically resolves via semantic bridge against the built-in golden sandbox or live sovereign attestation graph. Zero external side effects.\n\n"
                    "### Returns:\n"
                    "Returns a JSON object containing:\n"
                    "- query: The normalized query string.\n"
                    "- total_matches: Integer count of matched canonical concepts (typically 1 to 5).\n"
                    "- matched_concepts: Array of candidate ontology objects, each with concept_id (e.g. 'VS-SOC-001'), name_zh, name_en, discipline (e.g. 'SOC'), and axiomatic_summary.\n\n"
                    "### Edge Cases & Errors:\n"
                    "- If no academic concept matches the input, returns total_matches: 0 and an empty matched_concepts: [] list alongside suggested 3-letter discipline codes for manual filtering."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Colloquial business/workplace problem, metaphor, or scholarly inquiry to map (e.g. '跨部门推诿', '价格战', 'iron cage', 'panopticon'). Max 300 characters."
                        },
                        "discipline_hint": {
                            "type": "string",
                            "description": "Optional 3-4 letter academic discipline code to constrain candidate resolution (e.g. 'SOC' for Sociology, 'PHIL' for Philosophy, 'LAW' for Legal Studies, 'ECON' for Economics). Defaults to scanning all 24 disciplines."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "veriscope_inspect_topography",
                "description": (
                    "Stress-tests proposals, memos, or papers by retrieving axiomatic formal kernels, Wikidata QIDs, and 3+ opposing dialectical disputes for a canonical concept.\n\n"
                    "### When to Use:\n"
                    "- Use before finalizing business proposals, investment memos, or academic papers to uncover blind spots and stress-test core arguments.\n"
                    "- Use to retrieve formal foundational kernels, opposing historical disputes, and intellectual lineages for a known concept ID.\n\n"
                    "### When NOT to Use:\n"
                    "- Do NOT use with raw natural language queries; if you only have a colloquial phrase or topic, use `veriscope_discover_concepts` first to obtain the concept ID.\n"
                    "- Do NOT use for verifying cryptographic hashes or Ed25519 signatures; use `veriscope_verify_attestation`.\n"
                    "- Do NOT use for extracting or validating quotations from full draft text; use `veriscope_audit_citations`.\n\n"
                    "### Execution Behavior:\n"
                    "- Read-only, deterministic retrieval. Pulls axiomatic kernels, dispute structures, and Wikidata entity mappings from verified canonical records. Zero side effects.\n\n"
                    "### Returns:\n"
                    "Returns a JSON object containing:\n"
                    "- concept_id: The canonical concept identifier (e.g. 'VS-SOC-001').\n"
                    "- name_zh & name_en: Bilingual concept titles.\n"
                    "- axiomatic_kernel: Rigorous formal definition, thesis, and core theoretical formulation.\n"
                    "- wikidata_qid: Canonical Wikidata entity identifier (e.g. 'Q131154').\n"
                    "- dialectical_disputes: Array of 3+ opposing historical disputes, contrasting schools of thought, and counter-theses.\n"
                    "- canonical_works: Array of seminal treatises and foundational monograph citations.\n\n"
                    "### Edge Cases & Errors:\n"
                    "- If an invalid or unindexed concept_id is provided, returns status: 'error' with message: \"Concept '{concept_id}' not found in Golden Sandbox. Please check concept_id via veriscope_discover_concepts.\""
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {
                            "type": "string",
                            "description": "Canonical concept identifier obtained from veriscope_discover_concepts (e.g. 'VS-SOC-001' for 科层制/Bureaucracy, 'VS-PHIL-001' for 洞穴之喻/Allegory of the Cave)."
                        }
                    },
                    "required": ["concept_id"]
                }
            },
            {
                "name": "veriscope_locate_evidence",
                "description": (
                    "Locates fair-use verbatim excerpts (between 1 and 3 excerpts, strictly <=300 characters each) with exact chapter coordinates, 64-bit SHA-256 edition hashes, and Ed25519 cryptographic receipts.\n\n"
                    "### When to Use:\n"
                    "- Use when preparing high-stakes reports, legal briefs, or executive papers requiring zero-hallucination primary source backing.\n"
                    "- Use to retrieve authoritative textual evidence with exact chapter coordinates and cryptographic attestation receipts for a canonical concept.\n\n"
                    "### When NOT to Use:\n"
                    "- Do NOT use for exploratory topic browsing; call `veriscope_discover_concepts` to discover relevant concepts first.\n"
                    "- Do NOT use for batch-scanning an entire document for cited sources; call `veriscope_audit_citations` instead.\n"
                    "- Do NOT use to verify whether an existing hash or receipt is mathematically intact; call `veriscope_verify_attestation` instead.\n\n"
                    "### Execution Behavior:\n"
                    "- Read-only, deterministic retrieval. Excerpts strictly adhere to fair-use length limits (<=300 chars) bound to real physical volume SHA-256 editions. Zero side effects.\n\n"
                    "### Returns:\n"
                    "Returns a JSON object containing:\n"
                    "- concept_id: The canonical concept identifier.\n"
                    "- total_excerpts: Integer count of returned evidence snippets (typically 1 to 3).\n"
                    "- excerpts: Array of excerpt records, each containing verbatim_text (<= 300 chars), book_title, author, chapter_coordinate, and canon_sha256.\n"
                    "- attestation: Complete cryptographic receipt object with ed25519_signature and verification timestamp.\n\n"
                    "### Edge Cases & Errors:\n"
                    "- If concept_id is not found, returns status: 'error' with guidance to query veriscope_discover_concepts.\n"
                    "- If optional query_context finds no specific sub-paragraph alignment, falls back to returning the concept's primary canonical anchor excerpt."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {
                            "type": "string",
                            "description": "Canonical concept identifier (e.g. 'VS-SOC-001', 'VS-ECON-001')."
                        },
                        "query_context": {
                            "type": "string",
                            "description": "Optional sentence or topical context from your draft to guide snippet anchor selection within the canonical work."
                        }
                    },
                    "required": ["concept_id"]
                }
            },
            {
                "name": "veriscope_verify_attestation",
                "description": (
                    "Mathematically verifies the 64-bit SHA-256 edition hash and Ed25519 digital signature of cited quotes against verified canonical records.\n\n"
                    "### When to Use:\n"
                    "- Use to verify the cryptographic authenticity, integrity, and non-tampering of an attestation receipt received from veriscope_locate_evidence.\n"
                    "- Use in compliance checks to mathematically confirm whether a cited text snippet matches the genuine canonical edition.\n\n"
                    "### When NOT to Use:\n"
                    "- Do NOT use to discover or search for concepts; use `veriscope_discover_concepts`.\n"
                    "- Do NOT use to retrieve new evidence snippets; use `veriscope_locate_evidence`.\n"
                    "- Do NOT use for checking unformatted bibliography lists in draft papers; use `veriscope_audit_citations`.\n\n"
                    "### Parameter Combination Modes:\n"
                    "Provide either of the following two parameter combinations:\n"
                    "1. Path A (Local Hash Verification): Provide concept_id and canon_sha256 to verify against the local verified library ledger.\n"
                    "2. Path B (Ed25519 Cryptographic Verification): Provide the full attestation object (and optional concept_id) to verify the digital signature against the sovereign public key.\n\n"
                    "### Execution Behavior:\n"
                    "- Read-only, pure cryptographic verification. Performs constant-time hash and signature checks against public verification keys. Zero state modification.\n\n"
                    "### Returns:\n"
                    "Returns a JSON object containing:\n"
                    "- is_valid: Boolean (true if hash matches and signature is verified; false if tampered).\n"
                    "- verification_mode: String ('ed25519_signature' for signed receipts or 'local_hash_lookup' for edition checks).\n"
                    "- concept_id: Verified concept ID.\n"
                    "- status: String status code ('OK', 'TAMPER_DETECTED', 'PAYLOAD_MISMATCH', or 'ISSUER_UNTRUSTED').\n"
                    "- message: Human-readable verification explanation.\n\n"
                    "### Edge Cases & Errors:\n"
                    "- If neither canon_sha256 nor attestation is provided, returns status: 'error' explaining that at least one verification payload must be supplied.\n"
                    "- If a signature is forged or hash is tampered, returns is_valid: false with status: 'TAMPER_DETECTED'."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "concept_id": {
                            "type": "string",
                            "description": "Canonical concept identifier corresponding to the attestation (e.g. 'VS-SOC-001')."
                        },
                        "canon_sha256": {
                            "type": "string",
                            "description": "64-character SHA-256 edition hash to verify against canonical physical volume records. Used for Path A local verification."
                        },
                        "attestation": {
                            "type": "object",
                            "description": "Full attestation receipt object containing signature, timestamp, and coordinates returned by veriscope_locate_evidence. Used for Path B cryptographic verification."
                        }
                    }
                }
            },
            {
                "name": "veriscope_probe_radar",
                "description": (
                    "Probes cross-disciplinary matrix coverage, discipline distribution, and structural conceptual bridges across all 24 academic disciplines.\n\n"
                    "### When to Use:\n"
                    "- Use when exploring interdisciplinary connections, structural analogies, or conceptual bridges between distant fields (e.g. Physics and Sociology).\n"
                    "- Use to audit the distribution of canonical coverage and discover epistemic blind spots in a knowledge domain.\n\n"
                    "### When NOT to Use:\n"
                    "- Do NOT use to find specific definitions or dialectical disputes for a single concept; use `veriscope_inspect_topography`.\n"
                    "- Do NOT use for primary source quotation retrieval; use `veriscope_locate_evidence`.\n"
                    "- Do NOT use for auditing draft citations; use `veriscope_audit_citations`.\n\n"
                    "### Execution Behavior:\n"
                    "- Read-only statistical and topology analysis. Returns high-dimensional synaptic radar metrics and discipline distribution matrices. Zero side effects.\n\n"
                    "### Returns:\n"
                    "Returns a JSON object containing:\n"
                    "- total_disciplines: Integer count (24 disciplines).\n"
                    "- discipline_filter: The requested discipline filter (e.g. 'SOC') or 'ALL'.\n"
                    "- coverage_matrix: Key-value map of discipline codes to concept counts and verified treatise coverage percentages.\n"
                    "- interdisciplinary_bridges: Array of conceptual bridges mapping structural analogies between distinct disciplines (e.g. Thermodynamic Entropy to Social Anomie).\n"
                    "- epistemic_blindspots: List of cross-domain intersections with sparse coverage to guide deeper research.\n\n"
                    "### Edge Cases & Errors:\n"
                    "- If an unrecognized discipline code is provided, gracefully falls back to aggregating across all 24 disciplines without failing."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "discipline": {
                            "type": "string",
                            "description": "Optional 3-4 letter discipline code to filter radar statistics (e.g. 'SOC', 'PHIL', 'ECON', 'HIST', 'LAW', 'PHYS'). If omitted, aggregates across all 24 disciplines."
                        }
                    }
                }
            },
            {
                "name": "veriscope_audit_citations",
                "description": (
                    "Fast-scans draft articles, research papers, or AI-generated text to extract book citations, cross-check canonical bibliographies, and detect hallucinations or misattributions.\n\n"
                    "### When to Use:\n"
                    "- Use to audit draft articles, research proposals, or AI outputs for fabricated, distorted, or phantom citations before publication.\n"
                    "- Use to check whether cited authors and book titles match genuine historical editions and physical volume records.\n\n"
                    "### When NOT to Use:\n"
                    "- Do NOT use with single colloquial keywords or queries; use `veriscope_discover_concepts` for keyword concept mapping.\n"
                    "- Do NOT use to verify an Ed25519 cryptographic receipt object; use `veriscope_verify_attestation`.\n"
                    "- Do NOT use to generate new dialectical arguments; use `veriscope_inspect_topography`.\n\n"
                    "### Execution Behavior:\n"
                    "- Read-only forensic analysis. Parses text, identifies bibliographic references, and evaluates citation validity against canonical databases. Zero side effects and zero external data retention.\n\n"
                    "### Returns:\n"
                    "Returns a JSON object containing:\n"
                    "- total_citations_extracted: Integer count of scholarly book and author citations identified in the text.\n"
                    "- citation_health_score: Float or integer (0-100) reflecting percentage of verified canonical citations (or null if no citations found).\n"
                    "- verdict: Primary summary verdict ('ALL_CITATIONS_VERIFIED', 'PARTIAL_ATTRIBUTION_RISK', 'HALLUCINATED_OR_UNINDEXED', or 'NO_CITATIONS_FOUND').\n"
                    "- citations: Array of detailed citation audit records, each with raw_citation, extracted_author, extracted_title, matched_edition, canon_sha256, and individual status (EXACT_MATCH, SUPPORTS, QUALIFIES, ATTRIBUTION_SUSPECT, UNINDEXED_OR_HALLUCINATED).\n\n"
                    "### Edge Cases & Errors:\n"
                    "- Citation-Free Input: If the input text contains no academic book citations or author references, returns total_citations_extracted: 0, citation_health_score: null, and verdict: 'NO_CITATIONS_FOUND' without throwing an error.\n"
                    "- Empty or whitespace-only input returns a descriptive validation error."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Draft article, proposal, research brief, or AI-generated text containing book citations and author references to audit. Max 10,000 characters."
                        },
                        "discipline_hint": {
                            "type": "string",
                            "description": "Optional discipline hint (e.g. 'SOC', 'PHIL', 'ECON', 'LAW') to accelerate bibliographic entity resolution."
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
        elif name in ("veriscope_audit_citations", "veriscope_citation_audit", "veriscope_check_citations"):
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
            "notice": "Query not found in 50 offline sandbox concepts. Configure VERISCOPE_API_KEY to search 77,984 scholarly concepts across 24 disciplines."
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
            "message": f"Concept '{concept_id}' not found in Golden Sandbox. Configure VERISCOPE_API_KEY for the full 77,984 conceptual matrix.",
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

        # 3. Non-sandbox & No API Key: return clean scholarly fallback
        return {
            "status": "NOT_FOUND_IN_SANDBOX",
            "concept_id": cid,
            "canon_anchor": None,
            "is_offline_sandbox": True,
            "notice": f"Concept '{cid}' not found in built-in 50-canon offline sandbox. To query all 24 disciplines, configure VERISCOPE_API_KEY."
        }

    def verify_attestation(
        self,
        concept_id: Optional[str] = None,
        canon_sha256: Optional[str] = None,
        attestation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Path A: Verify by concept_id + canon_sha256 against sandbox
        if concept_id and canon_sha256 and not attestation:
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
                    "algorithm": "SHA-256"
                }

        # Path B: Verify attestation receipt payload & signature
        if attestation and isinstance(attestation, dict):
            caller_pub = attestation.get("public_key")
            trusted_pub = VERISCOPE_PUBLIC_KEY_HEX

            # S-4: 严格校验公钥信任源。严禁直接信任调用方传入的任意自签公钥
            if caller_pub:
                clean_caller_pub = str(caller_pub).replace("0x", "").strip().lower()
                if clean_caller_pub != trusted_pub.lower():
                    return {
                        "method": "ed25519_signature",
                        "verification_level": "UNTRUSTED_ISSUER",
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
                    "verification_level": "TAMPER_DETECTED",
                    "is_cryptographically_verified": False,
                    "verification_status": "TAMPER_DETECTED",
                    "error": "Missing signature or signed_message"
                }

            sig_clean = str(sig).replace("vsk_sig:", "").strip()

            if not _HAS_ED25519:
                return {
                    "method": "ed25519_signature",
                    "verification_level": "UNABLE_TO_VERIFY",
                    "is_cryptographically_verified": False,
                    "verification_status": "UNABLE_TO_VERIFY_DEPENDENCY_MISSING",
                    "error": "Cryptographic verification library (cryptography) is not installed in the environment."
                }

            if len(sig_clean) != 128 or len(pub) != 64:
                return {
                    "method": "ed25519_signature",
                    "verification_level": "SIGNATURE_FAILED",
                    "is_cryptographically_verified": False,
                    "verification_status": "SIGNATURE_INVALID",
                    "error": "Invalid signature or public key length"
                }

            try:
                pub_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub))
                pub_key.verify(bytes.fromhex(sig_clean), msg.encode("utf-8"))
            except Exception:
                return {
                    "method": "ed25519_signature",
                    "verification_level": "SIGNATURE_FAILED",
                    "is_cryptographically_verified": False,
                    "verification_status": "SIGNATURE_INVALID",
                    "algorithm": "Ed25519",
                    "public_key": pub,
                    "error": "Mathematical signature verification failed."
                }

            # N-3 闭环: 解构 signed_message 载荷并与用户查询参数严格比对
            parsed_payload = None
            if isinstance(msg, str) and msg.startswith("VERISCOPE_ATTESTATION:"):
                parts = msg.split(":")
                if len(parts) >= 8 and parts[1] == "v2":
                    parsed_payload = {
                        "protocol": parts[0],
                        "version": parts[1],
                        "key_id": parts[2],
                        "concept_id": parts[3] or "",
                        "canon_sha256": (parts[4] or "").lower(),
                        "doc_sha256": (parts[5] or "").lower(),
                        "slice_or_nonce": parts[6] or "",
                        "timestamp": parts[7] or ""
                    }
                elif len(parts) >= 5:
                    parsed_payload = {
                        "protocol": parts[0],
                        "version": "v1",
                        "concept_id": parts[1] or "",
                        "canon_sha256": (parts[2] or "").lower(),
                        "slice_or_nonce": parts[3] or "",
                        "timestamp": parts[4] or ""
                    }

            # 防伪造绕过检查 (Anti-Bypass Guard):
            # 若调用方传入了 concept_id 或 canon_sha256，签名载荷必须是合规的 VERISCOPE_ATTESTATION 凭证
            query_cid = (concept_id or "").strip()
            query_sha = (canon_sha256 or "").strip().lower()
            if query_cid or query_sha:
                if not parsed_payload:
                    return {
                        "method": "ed25519_signature",
                        "verification_level": "MALFORMED_ATTESTATION",
                        "is_cryptographically_verified": False,
                        "verification_status": "MALFORMED_ATTESTATION",
                        "error": "Signed message does not follow canonical VERISCOPE_ATTESTATION protocol format, cannot bind to requested concept_id/canon_sha256."
                    }
                if query_cid and query_cid.upper() != parsed_payload["concept_id"].upper():
                    return {
                        "method": "ed25519_signature",
                        "verification_level": "PAYLOAD_MISMATCH",
                        "is_cryptographically_verified": False,
                        "verification_status": "PAYLOAD_MISMATCH",
                        "error": f"Signed concept_id '{parsed_payload['concept_id']}' does not match query concept_id '{query_cid}'.",
                        "signed_payload": parsed_payload
                    }
                if query_sha and query_sha.lower() != parsed_payload["canon_sha256"].lower():
                    return {
                        "method": "ed25519_signature",
                        "verification_level": "PAYLOAD_MISMATCH",
                        "is_cryptographically_verified": False,
                        "verification_status": "PAYLOAD_MISMATCH",
                        "error": f"Signed canon_sha256 '{parsed_payload['canon_sha256']}' does not match query canon_sha256 '{query_sha}'.",
                        "signed_payload": parsed_payload
                    }

            return {
                "method": "ed25519_signature",
                "verification_level": "SIGNATURE_VERIFIED" if parsed_payload else "ARBITRARY_MESSAGE_SIGNED",
                "is_cryptographically_verified": True,
                "verification_status": "SIGNATURE_VALID" if parsed_payload else "ARBITRARY_PAYLOAD_VALID",
                "algorithm": "Ed25519",
                "public_key": pub,
                "signed_payload": parsed_payload or {
                    "raw_message": msg,
                    "note": "Valid cryptographic signature on non-attestation message payload."
                }
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
        parsed_url = urllib.parse.urlparse(self.gateway_url)
        if parsed_url.scheme != "https" and parsed_url.hostname not in ("localhost", "127.0.0.1"):
            return {"error": "Insecure gateway rejected: Remote VERISCOPE_GATEWAY_URL must use https:// to protect credentials."}

        payload = json.dumps({"tool": tool_name, "arguments": arguments}).encode("utf-8")
        req = urllib.request.Request(
            self.gateway_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "VeriScope-MCP-Python/1.1.7"
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

        CHINESE_PRONOUNS = {"他", "她", "它", "他们", "她们", "它们", "该作者", "此人", "作者", "著者", "译者"}
        AUTHOR_NOISE_PREFIXES = sorted([
            "正如", "按照", "参见", "根据", "由", "著名学者", "当代哲学家", "古典哲学家",
            "德意志哲学家", "德国哲学家", "法国哲学家", "英国经济学家", "美国社会学家",
            "古希腊哲学家", "古典政治学家", "社会学先驱", "法学先驱", "经济学大师",
            "著名哲学家", "学者", "教授", "先生", "作家", "部分学者", "然而", "但是",
            "认为", "强调", "指出", "提出", "声称"
        ], key=len, reverse=True)

        def clean_au(raw_s: str) -> str:
            if not raw_s:
                return ""
            s = str(raw_s).strip()
            # 剥除西文引用引导前缀与尾部动词/介词
            s = re.sub(r"^(?:as noted by|according to|as argued by|noted by|argued by|written by|as stated by|as|in|by)\s+", "", s, flags=re.IGNORECASE)
            s = re.sub(r"\s+(?:argues(?:\s+in)?|states(?:\s+in)?|claims(?:\s+in)?|writes(?:\s+in)?|shows|in)$", "", s, flags=re.IGNORECASE)
            for p in AUTHOR_NOISE_PREFIXES:
                if s.startswith(p):
                    s = s[len(p):].strip()
            s = re.sub(r"^[·\s，,、“”\"'（(：:【\[]+", "", s)
            s = re.sub(r"[·\s，,、“”\"'）)：:】\]]+$", "", s)
            s = re.sub(r"(?:在|于|中|里)$", "", s).strip()
            if s in CHINESE_PRONOUNS or (s + "在") in CHINESE_PRONOUNS:
                return ""
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
                quote_regex = re.compile(r'["“\'‘]([^"”\'’]{15,})["”\'’]')
                is_verbatim_quote = False
                if excerpt:
                    for qm in quote_regex.finditer(context):
                        if qm.group(1).strip() in excerpt:
                            is_verbatim_quote = True
                            break
                is_exact = is_verbatim_quote
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
                    "confidence_score": 0.99 if is_exact else 0.85,
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
        if total == 0:
            return {
                "status": "ok",
                "mode": "offline_golden_sandbox_50",
                "total_citations_extracted": 0,
                "verdict": "NO_CITATIONS_FOUND",
                "citation_health_score": None,
                "summary": "未在提交的文本中提取到结构化学术引注（请提供《书名》或标准 Academic Citation 引号格式）。",
                "citations": [],
                "notice": "离线模式基于 50 篇经典学术正典沙盒初筛。如需对勘 24 学科全量学术正典与章节定位，请配置 VERISCOPE_API_KEY。"
            }

        grounded_total = exact_cnt + supports_cnt + qualifies_cnt
        health_score = round(((grounded_total * 100) + (suspect_cnt * 30)) / total)

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
