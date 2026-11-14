# Changelog — VeriScope MCP

All notable changes to `veriscope-mcp` will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.10] - 2026-11-14

### Tool Schema & Runtime Output Precision Alignment
- **Runtime JSON Schema Precision**: Completely synchronized tool Returns documentation across `bin/index.js`, `glama.json`, and runtime responses. Replaced misnomers ("64-bit SHA-256" -> "256-bit SHA-256 (64 hex characters)", "physical volume" -> "canonical digital archive editions", removed "constant-time").
- **Anti-Bypass Error Precedence**: Enforced upfront format inspection in `veriscope_verify_attestation` for queries with `concept_id` / `canon_sha256`. Malformed or non-canonical payloads immediately trigger `MALFORMED_ATTESTATION` prior to cryptographic signature evaluation, preventing any verification short-circuiting.
- **Server Version Synchronization**: Aligned MCP initialization `serverInfo.version` and client `User-Agent` headers to `1.1.10`.
- **Security & Attestation Scope Disclosure**: Added dedicated cryptographic attestation scope, nonce semantics, and replay boundary disclosures to `SECURITY.md`.

## [1.1.9] - 2026-11-13

### Glama TDQS 5.0 Alignment & Protocol Governance
- **Glama TDQS 5.0 Tier-A Certification (4.7/5)**: Aligned all MCP tool definitions with Glama's official 5.0 rubric, implementing structured returns, detailed error semantics, and clean parameter schemas.
- **Verb-Noun Canonical Tool Naming**: Promoted `veriscope_audit_citations` as the canonical tool declaration while maintaining backward-compatible transparent aliasing for `veriscope_citation_audit`.
- **Cryptographic Release Attestation (RFC 8785 / JCS)**: Formally transitioned release attestation manifests (`VERISCOPE_RELEASE_ATTESTATION_1.1.9.json`) to strict RFC 8785 JSON Canonicalization Scheme (JCS) for cross-platform deterministic hashing and Ed25519 signature verification.
- **Supply Chain LF Line-Ending Normalization**: Enforced `.gitattributes` (`* text=auto eol=lf`) to permanently prevent platform-dependent CRLF vs LF tarball byte divergence during npm packaging.

## [1.1.8] - 2026-11-13

### Manifest & Ecosystem Registry Alignment
- **Glama Tool Registry Alignment**: Updated `glama.json` and `server.json` metadata to match Glama Server Manifest v1 specifications.
- **Tool Description Refinement**: Enhanced tool descriptions with comprehensive input/output semantics and operational boundary constraints.

## [1.1.7] - 2026-11-13

### Security & Protocol Engineering
- **N-3 Protocol Alignment & Payload Parsing Fix**: Corrected protocol array slicing when validating `v2` receipts (`VERISCOPE_ATTESTATION:v2:<key_id>:<concept_id>:<canon_sha256>:<doc_sha256>:<slice_sha16>:<timestamp>`). Resolves the critical offset bug where `parts[1]` was compared against `concept_id`, causing 50/50 authentic sandbox receipts to return `PAYLOAD_MISMATCH`. Parameter-bound attestation verification now succeeds 50/50.
- **N-3 Anti-Bypass Guard**: Enforced strict validation requiring that any verification call supplying `concept_id` or `canon_sha256` must accompany a canonical `VERISCOPE_ATTESTATION:` structured payload. Non-conforming arbitrary signed messages are strictly rejected with `MALFORMED_ATTESTATION`.
- **Path A Public Key Cleanliness**: Removed `public_key` field from Path A (`local_hash_lookup`) return dictionary, eliminating confusion between symmetric database hash matching and asymmetric digital signatures.
- **Gateway Transport Security**: Enforced HTTPS for remote gateway connections (`url.protocol === 'https:'`) to protect Bearer tokens from plaintext transport leakage.
- **Runtime Typo Fix**: Corrected JavaScript method call `cid.lower()` to `cid.toLowerCase()` in `bin/index.js`, preventing runtime `TypeError`.

### Citation Audit Engine Hardening
- **Author Normalization & Chinese Pronoun Handling**: Extended `cleanAuthorName` / `clean_au` with greedy prefix stripping (`as noted by`, `according to`, `written by`, `as stated by`) and Chinese pronoun filtering (`他`, `她`, `他们`, `该作者`, etc.), eliminating false-positive `ATTRIBUTION_SUSPECT` warnings.
- **Reverse Proposition Defense**: `EXACT_MATCH` (0.99) now strictly requires quotation marks with verbatim excerpt substring of length >= 15; general unquoted citations are labeled as `SUPPORTS` (0.85).
- **Fail-Open Remediation**: When 0 citations are detected, returns `verdict: "NO_CITATIONS_FOUND"` and `citation_health_score: null` instead of falsely returning 100% health.
- **Clean Academic Fallbacks**: Replaced commercial teaser pricing prompts in open-source fallback handlers with clean scholarly notifications.

### Distribution & Supply Chain Alignment
- **Ed25519 SPKI Encoding Fix**: Corrected SPKI Base64 representation in `.well-known/veriscope-keys.json` to `MCowBQYDK2VwAyEAvlXZhdcl7DZZSzLtnYEib824vhKm2gL73yMcOqOPH5M=`, establishing mathematical consistency with public key hex `be55d985d7...`.
- **Tarball Testability**: Included `"test"` in `package.json`'s `"files"` array, enabling `npm test` to run out of the box inside unpacked npm tarballs.
- **Manifest Synchronization**: Aligned version numbers to `1.1.7` across `package.json`, `server.json`, `glama.json`, `smithery.yaml`, `pyproject.toml`, `cli.py`, and `__init__.py`.
- **Glama Tool Registry**: Added missing `veriscope_citation_audit` tool declaration in `glama.json`.

## [1.1.6] - 2026-11-13

### Security & Architecture Hardening
- **N-3 (Attestation Payload Binding)**: `veriscope_verify_attestation` now inspects the structured payload of `signed_message`. Embedded fields (`concept_id`, `canon_sha256`, `slice_hash`, `timestamp`) are parsed and validated against caller arguments, preventing cross-concept attestation reuse (`PAYLOAD_MISMATCH`).
- **N-5 (Library Import Isolation)**: Wrapped server stdio execution in `if (require.main === module)` to prevent unprompted stream interception when `bin/index.js` is imported as an npm library or unit test subject.
- **S-2 & S-4 Semantic Refinements**: Introduced `verification_level: "HASH_ONLY" | "SIGNATURE_VERIFIED"` and explicit `is_hash_match` / `hash_matched` flags per auditor recommendations.

### Citation Audit Engine Enhancements
- **N-2 (Substring Attribution Disambiguation)**: Introduced `GENERIC_STOPWORDS` protection and token-level phrase matching, preventing generic terms like "Capital" from erroneously binding to secondary sociology concepts when referencing classical works.
- **N-4 (Author Extraction Normalization)**: Extended author name cleaning regex to strip trailing verbs and prepositions (`argues in`, `noted by`, `according to`), and added standard APA citation pattern support (`Author, A. (Year). Title.`).
- **Sandbox Hash Physical Verification**: Refreshed Golden Sandbox 50 SHA-256 hashes against actual physical files in the sovereign catalog repository (`cyclopedia_canon_files`), removing lingering test mock entries.

## [1.1.5] - 2026-11-12

### Security & Cryptographic Fixes
- **S-4 (High Severity Key Substitution)**: `veriscope_verify_attestation` now enforces strict public key authorization. Caller-supplied public keys that do not match the official VeriScope public key (`be55d985d7...`) are rejected with `verification_status: "ISSUER_UNTRUSTED"` and `is_cryptographically_verified: false`.
- **S-2 (Crypto Flag Accuracy)**: Path A local database hash lookup now returns `is_cryptographically_verified: false` to distinguish database lookups from asymmetric Ed25519 digital signatures.

### Citation Audit Engine Enhancements
- **T-1 (Author Whitespace Preservation)**: Fixed regular expression in `cleanAuthorName` / `clean_au` which previously stripped spaces inside western author names (e.g., turning "John Rawls" into "JohnRawls").
- **A-1 (State Splitting & Unindexed Literature)**: Split `UNINDEXED_OR_HALLUCINATED` into `UNINDEXED`. Unindexed works (e.g. 费孝通《乡土中国》) are marked as `UNINDEXED` (馆藏未收录) rather than false-positive AI hallucinations.
- **A-2 (Honest Semantic Attribution Labeling)**: Renamed `SUPPORTS` description to `🟢 权威正典出处吻合（著录与篇章坐标确证，命题语义待研读）` and clarified in notes that semantic proposition verification requires deep reading.
- **A-3 (Expanded English Citation Regex)**: Added support for APA/Chicago-style English citations such as `Kant, Critique of Pure Reason (1781)` and `As Author argues in "Title"`.

### Testing & Quality
- `test/test_citation_audit.js` now directly imports the published `bin/index.js` module instead of standalone helper duplicates.
- Added comprehensive regression tests in `test/test_security_audit.js` and `tests/test_citation_audit.py` for S-4, S-2, T-1, and A-1.
- Synchronized concept counts across all notices to 77,984.

## [1.1.4] - 2026-11-12
- Added `veriscope_citation_audit` tool with offline golden sandbox verification.
- Implemented dialectical qualification (`QUALIFIES`) and attribution mismatch (`ATTRIBUTION_SUSPECT`) detection.

## [1.1.3] - 2026-11-12
- Fixed S-1: Enforced native Ed25519 cryptographic curve point verification in Node.js.
- Fixed S-2: Explicitly labeled Path A as `local_hash_lookup` / `SHA-256`.
- Fixed S-3: Enforced hard block in Python when `cryptography` dependency is absent.
- Purged JEL classification codes and duplicate templates from `golden_sandbox_50.json`.
