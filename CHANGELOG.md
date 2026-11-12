# Changelog — VeriScope MCP

All notable changes to `veriscope-mcp` will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
