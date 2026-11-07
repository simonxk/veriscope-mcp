# VeriScope MCP Server (@veriscope/mcp-server)

> **VeriScope** is a sovereign cryptographic bibliographic index and citation verification engine for AI Agents. It anchors AI Task Planners in verified scholarly editions across 24 disciplines with **exact chapter coordinates**, **verbatim fair-use excerpts (<=300 chars)**, **64-bit SHA-256 edition hashes**, and **Ed25519 tamper-proof digital receipts (`vsk_sig`)**.

[![MCP Standard](https://img.shields.io/badge/MCP-1.0.0-blue.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero-Config Sandbox](https://img.shields.io/badge/Sandbox-50_Canons_Offline-brightgreen.svg)](#zero-config-golden-sandbox)
[![Dual-Track Pricing](https://img.shields.io/badge/Pricing-Payoneer_%7C_WeChat_%7C_Alipay-orange.svg)](#dual-track-pricing--access-tiers)

---

## 🌟 Why VeriScope? Three A/B Scenarios

When AI Agents conduct research, general-purpose LLMs generate plausible yet ungrounded citations, fabricate page numbers, or flatten vigorous intellectual conflicts into milquetoast compromises. VeriScope provides a **deterministic factual anchor**:

### Scenario 1: Max Weber Citation Verification (*The Protestant Ethic*)
* **The Task**: "Cite Max Weber's precise German-to-English thesis on the spirit of capitalism and its ascetic calling."
* ❌ **Vanilla LLM (Hallucinated)**:
  > "Weber writes in Chapter 2, page 181: 'The modern capitalist spirit arose purely from Calvinist predestination.' (Weber, 1905, Scribner edition)."
  > *Audit*: Fabricated page number; inaccurate quotation; no cryptographic edition hash.
* ✅ **VeriScope MCP (`veriscope_locate_evidence`)**:
  > **Edition**: *The Protestant Ethic and the Spirit of Capitalism* (Archival ID: Sovereign Harbor Verified Edition)  
  > **Coordinate**: Section 2: "The Spirit of Capitalism", Paragraph 12  
  > **Verbatim Excerpt (<=300 chars)**: *"Man is dominated by the making of money, by acquisition as the ultimate purpose of his life. Economic acquisition is no longer subordinated to man as the means for the satisfaction of his material needs."*  
  > **Edition SHA-256**: `d7a8fbb5628549...3984e1`  
  > **Receipt**: `vsk_sig:ed25519_8f0a2e...` (Cryptographically verified against tamper-lock)

---

### Scenario 2: Hans Kelsen vs. Carl Schmitt on Legal Sovereignty
* **The Task**: "Contrast Hans Kelsen's Pure Theory of Law with Carl Schmitt's Decisionism regarding the State of Exception."
* ❌ **Vanilla LLM (Flat Synthesis)**:
  > "Both scholars contributed to German legal theory. Kelsen believed in the rule of law and the Basic Norm, while Schmitt emphasized political authority during crises. They represent complementary aspects of jurisprudence."
  > *Audit*: Flattens an irreconcilable Weimar constitutional duel into false harmony.
* ✅ **VeriScope MCP (`veriscope_inspect_topography`)**:
  > **Formal Kernel**: Pure normativism (*Reine Rechtslehre*) vs. Political existential decisionism (*Dezisionismus*).  
  > **Lineages**: Hans Kelsen (Wikidata Q84322) vs. Carl Schmitt (Wikidata Q57476).  
  > **Dialectical Disputes (3 Core Theses)**:
  > 1. *Norm vs. Exception*: Kelsen posits law as a self-contained hierarchy deriving validity solely from the Grundnorm; Schmitt counters that the sovereign is "he who decides on the exception" (*Ausnahmezustand*), where norm yields to concrete order.
  > 2. *Guardian of the Constitution*: Kelsen's 1928 constitutional court doctrine vs. Schmitt's 1931 *Der Huter der Verfassung* asserting the Reich President as sole guardian.
  > 3. *Validity vs. Facticity*: Logical purity of legal norms versus existential political will.

---

### Scenario 3: Keynesian Liquidity Trap (*General Theory*)
* **The Task**: "Explain the exact institutional boundary of Keynes's liquidity trap and verify against primary economic texts."
* ❌ **Vanilla LLM (Secondary Paraphrase)**:
  > "Keynes explained that when interest rates are zero, monetary policy becomes ineffective because people hold cash."
* ✅ **VeriScope MCP (`veriscope_locate_evidence` & `veriscope_verify_attestation`)**:
  > **Formal Axiom**: Absolute liquidity preference under asymptotic flat LM-curve conditions where $\partial M / \partial r 	o \infty$.  
  > **Primary Location**: *The General Theory of Employment, Interest and Money*, Chapter 15 ("The Psychological and Business Incentives to Liquidity"), Section II.  
  > **Verification Status**: `VERIFIED_AUTHENTIC` (SHA-256 matched with primary English edition).

---

## 🛠️ The 4+1 Cognitive Funnel Tool Matrix

| Tool Name | Input Parameters | Primary Output | Use Case |
| :--- | :--- | :--- | :--- |
| `veriscope_discover_concepts` | `query: str`, `discipline_hint?: str` | Standardized canonical ontology, formal definition, Sino-Western comparative counterpart | Elevate colloquial concepts or news metaphors into formal academic disciplines |
| `veriscope_inspect_topography` | `concept_id: str` | `formal_kernel`, Wikidata QIDs, and 3+ structured `dialectical_disputes` | Prevent shallow syntheses; ground the agent in historical debates and rival axioms |
| `veriscope_locate_evidence` | `concept_id: str`, `proposition?: str` | Verbatim fair-use slice (**<=300 chars**), chapter coordinate, 64-bit SHA-256, Ed25519 receipt | Ground claims in physical verified editions with peer-reviewable cryptographic proof |
| `veriscope_verify_attestation` | `concept_id: str`, `claimed_sha256: str`, `verbatim_slice?: str` | `is_valid: bool`, `verification_status: "VERIFIED_AUTHENTIC" \| "TAMPER_DETECTED"` | Zero-knowledge cryptographic check for citations, journal peer review, and fact auditing |
| `veriscope_probe_radar` | `concept_id: str` | Cross-disciplinary synaptic radar links, epistemological blind spots | Interdisciplinary research, cognitive blind spot alerts, and synthetic conceptual discovery |

---

## ⚡ Zero-Config Golden Sandbox

VeriScope ships with a **built-in 50-Canon Golden Sandbox** (`golden_sandbox_50.json`, ~126 KB). 

* **Instant Offline Exploration**: Reviewers and developers can inspect, locate, and verify citations immediately upon installation **without signing up or providing any API key**.
* **10 Disciplines x 5 Canons**: Covers Philosophy (Kant, Plato, Descartes, Nietzsche, Spinoza), Sociology (Weber, Durkheim, Marx, Simmel, Parsons), Political Theory (Schmitt, Hobbes, Locke, Machiavelli, Rawls), Economics (Keynes, Smith, Hayek, Schumpeter, Ricardo), Law (Kelsen, Hart, Dworkin, Fuller, Savigny), History, Literature, Psychology, Communication, and Philosophy of Science (Kuhn, Popper, Lakatos, Feyerabend, Merton).
* **Teaser Mode for Long-Tail Canons**: When querying concepts beyond the 50 sandbox canons without an API key, VeriScope **does not crash with a 401 error**. Instead, it returns a **Cryptographic Teaser Preview** containing the matched canon title, chapter coordinate, and a non-empty `canon_sha256_prefix`, keeping the Agent's reasoning workflow alive.

---

## 💳 Dual-Track Pricing & Access Tiers

VeriScope utilizes a **hybrid subscription and credit-pack model** designed to eliminate per-call micro-payment anxiety for automated research pipelines:

| Plan / Tier | Target Audience | Domestic Pricing (WeChat / Alipay) | Global Pricing (Payoneer Checkout) | Included Quota / Benefits |
| :--- | :--- | :--- | :--- | :--- |
| **Community Sandbox** | Developers & Evaluators | **Free (¥0)** | **Free ($0)** | 50 Golden Canons full access + Teaser previews for all long-tail concepts |
| **Scholar Pro** | Researchers & PhD Candidates | **¥128 / month** | **$19 / month** | Unlimited standard queries, 5,000 evidence slices/mo, full Ed25519 attestation receipts |
| **Power Credit Pack** | Agent Builders & Automated Pipelines | **¥68 / 500 credits** | **$10 / 500 credits** | Flexible top-up for high-frequency automated batch synthesis |
| **Enterprise / Institution** | Academic Labs & Law Firms | **¥5,000 / year** | **$800 / year** | Dedicated rate limits, IP whitelist, institutional co-signing keys, SLA guarantee |

*To activate your key, visit [https://veriscope.cc/pricing](https://veriscope.cc/pricing) or configure `VERISCOPE_API_KEY`.*

---

## 🚀 Quick Start & Integration

### Claude Desktop / Claude Code
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "veriscope": {
      "command": "npx",
      "args": ["-y", "@veriscope/mcp-server"],
      "env": {
        "VERISCOPE_API_KEY": "vsk_live_optional_your_key_here"
      }
    }
  }
}
```

### Cursor & Windsurf
Add as a new stdio MCP server:
- **Command**: `npx`
- **Arguments**: `-y @veriscope/mcp-server`

### Python / uvx Alternative
```json
{
  "mcpServers": {
    "veriscope": {
      "command": "uvx",
      "args": ["veriscope-mcp"]
    }
  }
}
```

---

## 🔒 Security, Privacy & Scholarly Fair-Use Compliance

1. **Read-Only Engine**: VeriScope operates strictly in read-only mode (`mode=ro`). It never writes to the host filesystem.
2. **Scholarly Fair-Use Doctrine**: VeriScope is a cryptographic bibliographic index and citation verification engine. It never distributes or transmits full book copies; verbatim evidence excerpts are hard-capped at **strictly <=300 characters** around the proposition anchor.
3. **Cryptographic Ed25519 Receipts**: Every attested quote is signed with the slice's 16-hex hash (`slice_sha256_16`) in the payload `VERISCOPE_ATTESTATION:{concept_id}:{canon_sha256}:{slice_sha16}:{timestamp}`, providing tamper-evident authenticity for scholarly peer review.
4. **Entropy Rate Limiting (F8 Shield)**: High-entropy scraping attacks triggering cross-disciplinary jumps across $\ge 6$ disciplines in short bursts automatically drop into **Zero-Text Proof Mode** (yielding only coordinates and SHA-256 prefixes), protecting the sovereign archive while maintaining zero-hallucination factual integrity.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
