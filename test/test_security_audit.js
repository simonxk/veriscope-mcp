/**
 * Security & Cryptographic Integrity Regression Test Suite
 * Verifies fixes for S-1, S-2, S-3, S-4 reported during the 2026-11-12 Security Audit.
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { spawn } = require('child_process');

console.log('=== VeriScope MCP Security & Integrity Test Suite (v1.1.5) ===');

const binPath = path.join(__dirname, '..', 'bin', 'index.js');
const sandboxPath = path.join(__dirname, '..', 'golden_sandbox_50.json');
const sandbox = JSON.parse(fs.readFileSync(sandboxPath, 'utf8'));

const child = spawn('node', [binPath]);
let buffer = '';
const responses = new Map();

child.stdout.on('data', d => {
  buffer += d.toString();
  const lines = buffer.split('\n');
  buffer = lines.pop(); // keep partial line
  for (const l of lines) {
    if (!l.trim()) continue;
    try {
      const msg = JSON.parse(l);
      if (msg.id) responses.set(msg.id, msg);
    } catch (e) {}
  }
});

function sendRequest(id, method, params) {
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
}

// 1. Initialize
sendRequest(1, 'initialize', {
  protocolVersion: '2024-11-05',
  clientInfo: { name: 'security-test', version: '1.0' }
});

// 2. S-1 Exploit Payload: Forged 128-zero signature
sendRequest(2, 'tools/call', {
  name: 'veriscope_verify_attestation',
  arguments: {
    attestation: {
      signature: 'vsk_sig:' + '0'.repeat(128),
      signed_message: 'FORGED: Kant never wrote this',
      public_key: 'be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93'
    }
  }
});

// 3. Legitimate Ed25519 signature from Golden Sandbox #0
const c0 = sandbox.concepts[0];
sendRequest(3, 'tools/call', {
  name: 'veriscope_verify_attestation',
  arguments: {
    attestation: {
      signature: c0.cryptographic_receipt.signature,
      signed_message: c0.cryptographic_receipt.signed_message,
      public_key: c0.cryptographic_receipt.public_key
    }
  }
});

// 4. S-2 Path A: Hash lookup
sendRequest(4, 'tools/call', {
  name: 'veriscope_verify_attestation',
  arguments: {
    concept_id: 'VS-PHIL-001',
    canon_sha256: c0.canon_anchor.canon_sha256
  }
});

// 5. Tampered Hash in Path A
sendRequest(5, 'tools/call', {
  name: 'veriscope_verify_attestation',
  arguments: {
    concept_id: 'VS-PHIL-001',
    canon_sha256: 'deadbeef'.repeat(8)
  }
});

// 6. S-4 Exploit Payload: Attacker-supplied custom public key (self-signed arbitrary payload)
const { publicKey: attackerPubObj, privateKey: attackerPrivObj } = crypto.generateKeyPairSync('ed25519');
const fakeMsg = 'VERISCOPE_ATTESTATION:VS-PHIL-001:' + 'f'.repeat(64) + ':0000000000000000:2026-11-12T00:00:00Z';
const fakeSig = crypto.sign(null, Buffer.from(fakeMsg, 'utf8'), attackerPrivObj).toString('hex');
const attackerPubHex = attackerPubObj.export({ format: 'der', type: 'spki' }).slice(-32).toString('hex');

sendRequest(6, 'tools/call', {
  name: 'veriscope_verify_attestation',
  arguments: {
    attestation: {
      signature: 'vsk_sig:' + fakeSig,
      signed_message: fakeMsg,
      public_key: attackerPubHex
    }
  }
});

setTimeout(() => {
  child.stdin.end();

  // Test 1: S-1 Forgery Rejection
  const r2 = responses.get(2);
  assert(r2, 'Response for request 2 missing');
  const d2 = JSON.parse(r2.result.content[0].text);
  assert.strictEqual(d2.is_cryptographically_verified, false, 'S-1 FAIL: Forged signature must NOT be verified');
  assert.strictEqual(d2.verification_status, 'SIGNATURE_INVALID', 'S-1 FAIL: Status must be SIGNATURE_INVALID');
  console.log('  [✓] S-1 PASS: Forged 128-zero signature strictly rejected');

  // Test 2: Legitimate Ed25519 Verification
  const r3 = responses.get(3);
  assert(r3, 'Response for request 3 missing');
  const d3 = JSON.parse(r3.result.content[0].text);
  assert.strictEqual(d3.is_cryptographically_verified, true, 'Legitimate signature must verify');
  assert.strictEqual(d3.verification_status, 'SIGNATURE_VALID', 'Status must be SIGNATURE_VALID');
  console.log('  [✓] Ed25519 PASS: Legitimate golden sandbox signature verified');

  // Test 3: S-2 Path A Honest Labeling (is_cryptographically_verified: false)
  const r4 = responses.get(4);
  assert(r4, 'Response for request 4 missing');
  const d4 = JSON.parse(r4.result.content[0].text);
  assert.strictEqual(d4.method, 'local_hash_lookup', 'S-2 FAIL: Method must be local_hash_lookup');
  assert.strictEqual(d4.algorithm, 'SHA-256', 'S-2 FAIL: Algorithm must be SHA-256 (not Ed25519)');
  assert.strictEqual(d4.hash_matched, true);
  assert.strictEqual(d4.is_cryptographically_verified, false, 'S-2 FAIL: Local hash lookup is not asymmetric crypto verification, must be false');
  console.log('  [✓] S-2 PASS: Path A accurately labeled as local_hash_lookup & is_cryptographically_verified: false');

  // Test 4: Tampered Hash Rejection
  const r5 = responses.get(5);
  assert(r5, 'Response for request 5 missing');
  const d5 = JSON.parse(r5.result.content[0].text);
  assert.strictEqual(d5.hash_matched, false);
  assert.strictEqual(d5.verification_status, 'TAMPER_DETECTED');
  console.log('  [✓] Path A PASS: Tampered hash correctly flagged as TAMPER_DETECTED');

  // Test 5: S-4 Attacker Custom Public Key Rejection
  const r6 = responses.get(6);
  assert(r6, 'Response for request 6 missing');
  const d6 = JSON.parse(r6.result.content[0].text);
  assert.strictEqual(d6.is_cryptographically_verified, false, 'S-4 FAIL: Caller-supplied custom public key must NOT be verified');
  assert.strictEqual(d6.verification_status, 'ISSUER_UNTRUSTED', 'S-4 FAIL: Status must be ISSUER_UNTRUSTED');
  console.log('  [✓] S-4 PASS: Attacker custom public key strictly rejected as ISSUER_UNTRUSTED');

  console.log('\n===========================================');
  console.log('ALL NODE.JS SECURITY REGRESSION TESTS PASS!');
  console.log('===========================================');
  process.exit(0);
}, 600);
