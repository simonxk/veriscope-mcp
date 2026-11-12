# VeriScope MCP Server (veriscope-mcp)

> **VeriScope** is a sovereign cryptographic bibliographic index and citation verification engine for AI Agents. It anchors AI Task Planners in verified scholarly editions across 24 disciplines with **exact chapter coordinates**, **verbatim fair-use excerpts (<=300 chars)**, **256-bit SHA-256 edition hashes**, and **Ed25519 tamper-proof digital receipts (`vsk_sig`)**.

[![MCP Standard](https://img.shields.io/badge/MCP-1.1.0-blue.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero-Config Sandbox](https://img.shields.io/badge/Sandbox-50_Canons_Offline-brightgreen.svg)](#zero-config-golden-sandbox)
[![Dual-Track Pricing](https://img.shields.io/badge/Pricing-Payoneer_%7C_WeChat_%7C_Alipay-orange.svg)](#dual-track-pricing--access-tiers)

---

> 🧩 **Looking for 100 Sovereign Cognitive Primitives (Pure Markdown)?**  
> If you want zero-dependency, copy-paste decision models, negative attention anchors (Anti-Cliches), and `.cursorrules` for Cursor / Claude Code without setting up an MCP server, check out our companion repository: [**simonxk/veriscope-the-idea-depot**](https://github.com/simonxk/veriscope-the-idea-depot).

---
## 🌟 Why VeriScope? Four High-Impact Scenarios (Academic & Executive Strategy)

When AI Agents conduct research or draft strategic memos, general-purpose LLMs generate plausible yet ungrounded citations, saturate drafts with generic corporate clichés ("AI slop"), or flatten vigorous intellectual conflicts into milquetoast compromises. VeriScope provides a **deterministic factual & dialectical anchor**:

### Scenario 1: Max Weber Citation Verification (*The Protestant Ethic*)
* **The Task**: "Cite Max Weber's precise German-to-English thesis on the spirit of capitalism and its ascetic calling."
* ❌ **Vanilla LLM (Hallucinated)**:
  > "Weber writes in Chapter 2, page 181: 'The modern capitalist spirit arose purely from Calvinist predestination.' (Weber, 1905, Scribner edition)."
  > *Audit*: Fabricated page number; inaccurate quotation; no cryptographic edition hash.
* ✅ **VeriScope MCP (`veriscope_locate_evidence`)**:
  > **Edition**: *The Protestant Ethic and the Spirit of Capitalism* (Archival ID: VeriScope Epistemic Substrate Verified Edition)  
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
  > **Formal Axiom**: Absolute liquidity preference under asymptotic flat LM-curve conditions where $\partial M / \partial r \to \infty$.  
  > **Primary Location**: *The General Theory of Employment, Interest and Money*, Chapter 15 ("The Psychological and Business Incentives to Liquidity"), Section II.  
  > **Verification Status**: `VERIFIED_AUTHENTIC` (SHA-256 matched with primary English edition).

---

### Scenario 4: Executive Briefing Elevation & Pre-Mortem Red-Teaming (De-Slop & Grounding)
* **The Task**: "De-slop this corporate proposal on organizational friction, elevate it to first-principles institutional economics, and run a pre-mortem red-team audit before the board review."
* ❌ **Vanilla LLM (Generic Corporate Slop)**:
  > "We must break down silos, leverage digital synergies, and align cross-functional stakeholders to drive end-to-end transformation."
* ✅ **VeriScope MCP (`veriscope_discover_concepts` / `veriscope_inspect_topography` / `veriscope_locate_evidence`)**:
  > **First-Principles Elevation**: Maps colloquial "silos and red tape" to Max Weber's **Iron Cage of Bureaucracy (`VS-SOC-001`)** and Coasean **Transaction Cost Economics (`VS-ECON-004`)**.  
  > **Pre-Mortem Red-Team Challenges**: Exposes 3 structural blind spots (e.g., why adding digital coordination layers without altering incentive compatibility increases internal transaction friction).  
  > **Attested Grounding**: Anchors the executive memo with a <=300-char primary excerpt and Ed25519 receipt (`vsk_sig`).

---

## 🛠️ The 4+1+1 Cognitive Funnel Tool Matrix (with Citation Audit) (with Business Routing Aliases)

| Tool Name ( & Business Alias) | Input Parameters | Primary Output | Use Case |
| :--- | :--- | :--- | :--- |
| `veriscope_discover_concepts`<br>*(Alias: `veriscope_business_frame`)* | `query: str`, `discipline_hint?: str` | Standardized canonical ontology, formal definition, Sino-Western comparative counterpart | Elevate colloquial concepts, workplace pain points, or news metaphors into formal academic & strategic frameworks |
| `veriscope_inspect_topography`<br>*(Alias: `veriscope_redteam_audit`)* | `concept_id: str` | `formal_kernel`, Wikidata QIDs, and 3+ structured `dialectical_disputes` | Pre-mortem red-teaming; prevent shallow syntheses; ground the agent in rival axioms and blind spots |
| `veriscope_locate_evidence`<br>*(Alias: `veriscope_deslop_and_ground`)* | `concept_id: str`, `proposition?: str` | Verbatim fair-use slice (**<=300 chars**), chapter coordinate, 256-bit SHA-256, Ed25519 receipt | Replace synthetic AI filler with attested primary editions and peer-reviewable cryptographic proof |
| `veriscope_verify_attestation` | `concept_id: str`, `claimed_sha256: str`, `verbatim_slice?: str` | `is_valid: bool`, `verification_status: "SIGNATURE_VALID" \| "SIGNATURE_INVALID"` | Cryptographic Ed25519 signature & SHA-256 edition hash check for citations, peer review, and compliance auditing |
| `veriscope_probe_radar` | `concept_id: str` | Cross-disciplinary synaptic radar links, epistemological blind spots | Interdisciplinary research, cognitive blind spot alerts, and synthetic conceptual discovery |
| `veriscope_citation_audit` | `text: str`, `discipline_hint?: str` | Extracted citations, author alignment, SHA-256 grounding, health score (0-100), hallucination detection | **AI Citation Health Check**: Fast-scan drafts to detect fabricated AI citations and misattributions |

---

## ⚡ Zero-Config Golden Sandbox

VeriScope ships with a **built-in 50-Canon Golden Sandbox** (`golden_sandbox_50.json`, ~126 KB). 

* **Instant Offline Exploration**: Reviewers and developers can inspect, locate, and verify citations immediately upon installation **without signing up or providing any API key**.
* **10 Disciplines x 5 Canons**: Covers Philosophy (Kant, Plato, Descartes, Nietzsche, Spinoza), Sociology (Weber, Durkheim, Marx, Simmel, Parsons), Political Theory (Schmitt, Hobbes, Locke, Machiavelli, Rawls), Economics (Keynes, Smith, Hayek, Schumpeter, Ricardo), Law (Kelsen, Hart, Dworkin, Fuller, Savigny), History, Literature, Psychology, Communication, and Philosophy of Science (Kuhn, Popper, Lakatos, Feyerabend, Merton).
* **Teaser Mode for Long-Tail Canons**: When querying concepts beyond the 50 sandbox canons without an API key, VeriScope **does not crash with a 401 error**. Instead, it returns a **Cryptographic Teaser Preview** containing the matched canon title, chapter coordinate, and a non-empty `canon_sha256_prefix`, keeping the Agent's reasoning workflow alive.

---

## 💳 Dual-Track Pricing & Access Tiers

VeriScope utilizes a **hybrid subscription and credit-pack model** designed to eliminate per-call micro-payment anxiety for automated research pipelines:

| Plan / Tier | Target Audience | Domestic Pricing (CNY) | Global Pricing (USD) | Included Quota / Benefits |
| :--- | :--- | :--- | :--- | :--- |
| **Community Sandbox** | Developers & Evaluators | **Free (¥0)** | **Free ($0)** | 50 Golden Canons full access + Teaser previews for long-tail concepts |
| **Scholar Pro** | Researchers & PhD Candidates | **¥98 / mo (¥880/yr)** | **$19 / mo** | Unlimited standard queries, 5,000 evidence slices/mo, full Ed25519 attestation receipts |
| **Enterprise / Institution** | Academic Labs & Institutions | **¥9,800 / year** | **$1,500 / year** | High-concurrency dedicated rate limits, IP whitelist, institutional keys, SLA guarantee |

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
      "args": ["-y", "veriscope-mcp"],
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
- **Arguments**: `-y veriscope-mcp`

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
