# Security Policy — VeriScope MCP

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.10  | :white_check_mark: |
| 1.1.9   | :white_check_mark: |
| 1.1.8   | :white_check_mark: |
| 1.1.7   | :white_check_mark: |
| < 1.1.7 | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within VeriScope MCP or Cognitive SSL attestation protocol, please report it privately:

- **Security Team Email**: `security@veriscope.cc` / `core@veriscope.cc`
- **PGP / Ed25519 Inquiries**: Official public keys are published at `https://veriscope.cc/.well-known/veriscope-keys.json`.

Please do NOT file public GitHub issues for undisclosed vulnerabilities. We adhere to responsible disclosure and typically acknowledge reports within 24 hours.

## Cryptographic Attestation Scope, Nonce Semantics & Limitations

- **Attestation Scope**: A VeriScope Ed25519 attestation receipt deterministically binds a canonical concept (`concept_id`), the authoritative archival edition hash (`canon_sha256`), document excerpt hash (`doc_sha256`), and excerpt slice (`slice16`) to the VeriScope Sovereign Root Trust Anchor (`veriscope-ed25519-v2-2026`).
- **Nonce Semantics**: The receipt includes a timestamp and slice hash token (`slice_or_nonce`) that establishes the cryptographic existence and integrity of the cited excerpt at issuance time. 
- **Limitations & Replay Boundaries**: The attestation receipts are deterministic proofs of archival authenticity; they do NOT provide real-time interactive session nonces or replay freshness guarantees. Applications requiring replay mitigation across interactive client-server sessions should pair the receipt with application-level challenge nonces or TLS transport timestamps.

## Security Advisories

### VSK-SEC-2026-007: Anti-Bypass Error Precedence & Schema Precision Alignment
- **Affected Versions**: `<= 1.1.9`
- **Fixed In**: `1.1.10`
- **Severity**: Low-Medium
- **Description**: 
  1. In version 1.1.9, if a non-canonical payload was supplied with `concept_id` or `canon_sha256` alongside a forged or broken signature, `SIGNATURE_INVALID` could take precedence over `MALFORMED_ATTESTATION`.
  2. MCP initialization `serverInfo.version` was aligned to 1.1.10.
  3. Tool parameter and return schemas were strictly aligned between implementation, `glama.json`, and runtime responses.
- **Remediation**: Version 1.1.10 enforces upfront format validation for targeted attestation queries before cryptographic execution, immediately terminating non-canonical attempts with `MALFORMED_ATTESTATION`.

### VSK-SEC-2026-006: Protocol Array Offset, Anti-Bypass Guard & Citation Engine Hardening
- **Affected Versions**: `<= 1.1.6`
- **Fixed In**: `1.1.7`
- **Severity**: High
- **Description**: 
  1. In version 1.1.6, the N-3 payload parser checked array index 1 instead of index 3 for concept_id in v2 attestation tokens, causing authentic receipts to fail parameter binding with `PAYLOAD_MISMATCH`.
  2. Non-attestation arbitrary signed messages paired with concept_id bypassed format enforcement.
  3. SPKI Base64 representation in key registry contained a transcription error.
  4. Citation engine awarded `EXACT_MATCH` on short unquoted substrings and failed open when 0 citations were detected.
- **Remediation**: 
  1. Version 1.1.7 correctly maps `parts[3]` to concept_id and `parts[4]` to canon_sha256 in v2 protocol tokens; 50/50 official receipts verify successfully.
  2. Enforced strict `VERISCOPE_ATTESTATION` envelope validation (`MALFORMED_ATTESTATION` on bypass attempt).
  3. Corrected SPKI Base64 encoding to `MCowBQYDK2VwAyEAvlXZhdcl7DZZSzLtnYEib824vhKm2gL73yMcOqOPH5M=`.
  4. Enforced quotes and >= 15 chars verbatim excerpt requirement for `EXACT_MATCH`, and set `verdict: "NO_CITATIONS_FOUND"` with null health score when 0 citations are detected.

### VSK-SEC-2026-005: Attestation Payload Semantic Binding & Isolation (N-3 & N-5)
- **Affected Versions**: `<= 1.1.5`
- **Fixed In**: `1.1.6`
- **Severity**: Medium-High
- **Description**: 
  1. In version 1.1.5, `veriscope_verify_attestation` verified the digital signature over `signed_message`, but did not parse and cross-validate whether the concept ID, canon SHA-256, or caller parameters matched the signed payload.
  2. Importing `bin/index.js` via `require()` inadvertently attached readline listeners to `process.stdin`.
- **Remediation**: 
  1. Version 1.1.6 parses the signed attestation token (`VERISCOPE_ATTESTATION:v2:...`), extracts the embedded `concept_id`, `canon_sha256`, and `slice_hash`, and strictly asserts matching against query arguments, returning `PAYLOAD_MISMATCH` if inconsistent.
  2. Wrapped stdin/stdout server execution in `if (require.main === module)` to prevent side effects when imported as a library.

### VSK-SEC-2026-004: Caller Public Key Substitution in Attestation Verifier (S-4)
- **Affected Versions**: `<= 1.1.4`
- **Fixed In**: `1.1.5`
- **Severity**: High
- **Description**: In versions 1.1.4 and prior, `veriscope_verify_attestation` allowed callers to provide an arbitrary `attestation.public_key`. The verifier would verify the signature against the caller-supplied key without verifying that the key belongs to the authorized VeriScope trust anchor.
- **Remediation**: Version 1.1.5 introduces strict public key authorization. If `attestation.public_key` is supplied and does not match the official VeriScope public key (`be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93`), verification immediately fails with `verification_status: "ISSUER_UNTRUSTED"` and `is_cryptographically_verified: false`.

### VSK-SEC-2026-002: Path A Local Hash Lookup Crypto Flag Correction (S-2)
- **Affected Versions**: `<= 1.1.4`
- **Fixed In**: `1.1.5`
- **Severity**: Medium
- **Description**: Path A database hash lookups previously set `is_cryptographically_verified: true`. Version 1.1.5 sets this strictly to `false` (only genuine Ed25519 digital signatures return true).

### VSK-SEC-2026-001: Forged 128-zero Signature Bypass (S-1)
- **Affected Versions**: `<= 1.1.2`
- **Fixed In**: `1.1.3`
- **Severity**: Critical
- **Description**: Node.js verifier previously accepted arbitrary 128-char hex strings without Ed25519 cryptographic curve point validation.
- **Remediation**: Version 1.1.3 enforced native `crypto.verify` Ed25519 signature checks.

### VSK-SEC-2026-003: Python Dependency Degradation (S-3)
- **Affected Versions**: `<= 1.1.2`
- **Fixed In**: `1.1.3`
- **Severity**: High
- **Description**: Python server degraded to key comparison when `cryptography` was missing. Version 1.1.3 returns `UNABLE_TO_VERIFY_DEPENDENCY_MISSING` and rejects verification.
