# 真镜 VeriScope MCP Server (`veriscope-mcp` / `@veriscope/mcp-server`)

> **真镜（VeriScope）** 是面向 AI Agents、高阶幕僚与学术研究者的**密码学文献索引与引文验真引擎（Cryptographic Bibliographic Index & Fair-Use Citation Verification Engine）**。覆盖 24 门学科大典，通过**精确章节坐标**、**合理使用原文切片（≤300 字）**、**64 位 SHA-256 版本哈希**以及 **Ed25519 防篡改数字凭证（`vsk_sig`）**，彻底消除大模型幻觉、黑话空话（AI Slop）与和稀泥式平庸综述。

[![MCP Standard](https://img.shields.io/badge/MCP-1.1.0-blue.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero-Config Sandbox](https://img.shields.io/badge/Sandbox-50_Canons_Offline-brightgreen.svg)](#零配置黄金离线沙盒)
[![Dual-Track Pricing](https://img.shields.io/badge/Pricing-Payoneer_%7C_WeChat_%7C_Alipay-orange.svg)](#双轨接入与定价体系)

---

> 🧩 **正在寻找 100 篇开箱即用的第一性原理决策标准件（纯 Markdown 实体）？**  
> 如果您希望在无需安装任何 Node.js/Python 环境的前提下，直接复制带有 64 位 SHA-256 原本散列的决策模型、反陈词滥调禁区（Anti-Cliches）以及适配 Cursor / Claude Code 的 `.cursorrules`，请直接访问我们的孪生知识库仓库：[**simonxk/veriscope-the-idea-depot**](https://github.com/simonxk/veriscope-the-idea-depot)。

---
## 🌟 为什么需要真镜？四大核心赋能场景（学术研究 + 商业幕僚双栖）

通用大模型在起草报告、提案或论文时，极易产生两类致命缺陷：**① 满篇“赋能/抓手/闭环”的同质化 AI 塑料味（AI Slop）與虚构引文**；**② 缺乏反方压力测试的盲目乐观**。真镜提供确定性的事实与思想底座：

### 场景 1：政企内参 / 商业立项报告 ——「祛 AI 味 + 立意升维 + 魔鬼质询」
* **任务指令**：“把这段关于‘部门协同内耗、数字化转型推不动’的汇报初稿祛除 AI 味，升维到制度经济学与组织社会学高度，并在上会前做一次魔鬼质询（Pre-Mortem）。”
* ❌ **普通大模型（空洞套话）**：
  > “我们需要打破部门墙，强化顶层设计，通过数字化抓手赋能业务闭环，实现降本增效与生态共赢。”
* ✅ **真镜 MCP（`veriscope_discover_concepts` → `veriscope_inspect_topography` → `veriscope_locate_evidence`）**：
  > **【立意升维】**：将“部门推诿与流程空转”锚定为马克斯·韦伯**「科层制铁笼（Iron Cage of Bureaucracy）」**与科斯/威廉姆森**「内部交易成本（Transaction Cost）与资产专用性摩擦」**——当跨部门协调的边际组织成本高于外部市场契约时，单纯增加审批节点只会引发帕金森定律式的行政自殖。  
  > **【魔鬼质询（会前防怼压力测试）】**：  
  > 1. *制度动力学反诘*：若不重构考核激励相容机制，新增的数字化中台是否会沦为强化形式理性的第二道“数字铁笼”？  
  > 2. *原典定海神针（≤300字合理使用切片）*：《经济与社会》第 11 章第 6 节 | SHA-256: `f1a9c284e73b61...` | 凭证: `vsk_sig:ed25519_...`

---

### 场景 2：马克斯·韦伯原典核验（《新教伦理与资本主义精神》）
* **任务指令**：“引用韦伯关于资本主义精神与禁欲主义天职观的精确论述并核验版本真伪。”
* ❌ **普通大模型（幻觉捏造）**：虚构页码与并不存在的引文段落。
* ✅ **真镜 MCP（`veriscope_locate_evidence`）**：
  > **版本著录**：*The Protestant Ethic and the Spirit of Capitalism*  
  > **章节坐标**：Section 2: "The Spirit of Capitalism", Paragraph 12  
  > **版本 SHA-256**：`d7a8fbb5628549...3984e1`  
  > **数字凭证**：`vsk_sig:ed25519_8f0a2e...`（支持 Ed25519 密码学签名校验）

---

### 场景 3：凯尔森 vs. 施米特 —— 思想史两造交锋（拒绝和稀泥）
* **任务指令**：“对比汉斯·凯尔森纯粹法学与卡尔·施米特决断论关于‘例外状态’的主权之争。”
* ✅ **真镜 MCP（`veriscope_inspect_topography`）**：
  > 返回**形式核公理（`formal_kernel`）**、学者 Wikidata QID（`Q84322` vs `Q57476`）以及 **3 组结构化两造交锋（`dialectical_disputes`）**，完整还原规范主义基础规范与政治决断论的不可调和张力。

---

### 场景 4：凯恩斯流动性陷阱边界核查（《就业、利息和货币通论》）
* **任务指令**：“核查凯恩斯流动性陷阱的制度成立边界与原著对应章节。”
* ✅ **真镜 MCP（`veriscope_locate_evidence` & `veriscope_verify_attestation`）**：
  > 锁定《通论》第 15 章第 2 节，返回 `SIGNATURE_VALID` 256 位版本哈希与签名验真状态。

---

## 🛠️ 4+1+1 主权认知漏斗工具矩阵（新增：AI 引文体检与大模型幻觉查杀）（含商业幕僚语义路由别名）

| 主权标准工具名（商业场景路由别名） | 核心输入参数 | 核心输出载荷 | 典型唤醒场景 |
| :--- | :--- | :--- | :--- |
| `veriscope_discover_concepts`<br>*(别名: `veriscope_business_frame`)* | `query: str`, `discipline_hint?: str` | 24 学科标准概念本体、形式核定义、中西范畴互勘 | **立意升维 / 祛 AI 味**：将口语痛点、商业提案或新闻热词升维为第一性原理学术锚点 |
| `veriscope_inspect_topography`<br>*(别名: `veriscope_redteam_audit`)* | `concept_id: str` | `formal_kernel`、Wikidata QID、3+ 组正反学派 `dialectical_disputes` | **魔鬼质询 / 红蓝军压力测试**：暴露方案隐含假设盲区，获取正反两造交锋弹药 |
| `veriscope_locate_evidence`<br>*(别名: `veriscope_deslop_and_ground`)* | `concept_id: str`, `query_proposition?: str` | 合理使用原文切片（**≤300 字**）、章节坐标、256 位 SHA-256、Ed25519 签名 | **硬核引文坐实**：用规范的权威著作切片替换空洞套话，生成防篡改数字回执 |
| `veriscope_verify_attestation` | `concept_id: str`, `canon_sha256: str` | `is_cryptographically_verified: bool`, `SIGNATURE_VALID \| SIGNATURE_INVALID` | **合规与审稿验真**：Ed25519 签名与 256 位版本哈希密码学校验 |
| `veriscope_probe_radar` | `topic: str` | 跨学科突触连接（`babel_synapses`）、认知盲区诊断 | **跨界策展与盲区探测**：打通哲学、经济、法学、社会学等跨学科高维连接 |
| `veriscope_citation_audit` | `text: str`, `discipline_hint?: str` | 引用书目提取、著者对勘、版本 SHA-256 吻合度、五态法医对账判决、健康度评分（0-100） | **AI 引文真伪体检**：毫秒级查杀大模型幻觉虚构的书目引文与张冠李戴，杜绝学术伪证 |

### 🔬 五态引文法医对账判决体系（Citation Forensic Taxonomy）

`veriscope_citation_audit` 对输入文本中的学术引注进行深度对勘，输出 5 种结构化判决：

1. 🟢 **`EXACT_MATCH`（原典字句确证）**：引述命题或文字片段在权威原典中获得字句级证实，附带章节坐标与 256 位 SHA-256 版本哈希；
2. 🟢 **`SUPPORTS`（正典公理支持）**：权威正典核心范式支持该命题，思想源流与论断完全吻合；
3. ⚖️ **`QUALIFIES`（学派辩证限定）**：该命题在学术思想史中存在核心辩证争议或先决条件，工具自动提供正反两造交锋论据，防止单边断章取义；
4. 🟡 **`ATTRIBUTION_SUSPECT`（疑似张冠李戴）**：著作真实存在，但著录著者严重错位（例如大模型将亚当·斯密《国富论》挂在凯恩斯名下），精准拦截学术失真；
5. ⚪ **`UNINDEXED_OR_HALLUCINATED`（未收录/疑似虚构）**：未在正典索引库中检索到出版著录，警示用户谨防大模型伪造文献幻觉。

---

## ⚡ 零配置黄金离线沙盒（Zero-Config Golden Sandbox）

真镜内置 **50 篇跨学科经典概念离线沙盒**（`golden_sandbox_50.json`，仅约 126 KB）：
* **开箱即用**：无需注册、无需配置 API Key，安装后即可离线跑通“概念发现 → 两造交锋 → 原典定位 → 签名验真”完整闭环。
* **优雅预览模式（Teaser Mode）**：当未配置 API Key 查询沙盒外的长尾概念时，绝不粗暴报错中断 Agent 思考链，而是返回包含匹配书名、章节坐标与真实 16 位哈希前缀的 **Cryptographic Teaser Preview**。

---

## 💳 接入与服务体系

| 方案档位 | 适用人群与场景 | 国内标准费率 (CNY) | 国际标准费率 (USD) | 包含权益与额度 |
| :--- | :--- | :--- | :--- | :--- |
| **Community Sandbox** | 开发者评测与基础体验 | **免费 (¥0)** | **Free ($0)** | 50 篇黄金经典沙盒全量解锁 + 全库长尾概念 Teaser 预览 |
| **Scholar Pro** | 个人研究者 / 博士生 / 独立学者 | **¥98 / 月 (年付 ¥880)** | **$19 / month** | 标准检索不限次，每月 5,000 次原典切片锚定 + Ed25519 数字签名 |
| **Enterprise / 机构版** | 智库实验室 / 律所 / 高等院校研究组 | **¥9,800 / 年起** | **$1,500 / year起** | 独立高并发配额、IP 白名单、机构联署签名密钥与 SLA 保障 |

*获取与激活 API Key：[https://veriscope.cc/pricing](https://veriscope.cc/pricing)*

---

## 🚀 快速接入指南

### 1. Claude Desktop / Claude Code / Cursor (`npx` 零依赖启动)
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

### 2. Python / `uvx` 启动
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

## 🔒 学术合理使用（Fair-Use）与安全合规承诺

1. **纯只读架构**：严格工作于只读模式（`mode=ro`），绝不修改宿主环境文件。
2. **学术合理使用原则（≤300 字硬上限）**：本引擎定位为密码学书目索引与引文核验工具，绝不分发整本电子书文件；所有原文核验切片严格限制在命题锚点周边 **≤300 字符**。
3. **Ed25519 密码学防伪凭证**：每条引文回执均包含切片 16 位哈希摘要与 Ed25519 数字签名，改动哪怕一个标点符号均会触发 `TAMPER_DETECTED`。
4. **F8 跨学科高熵防掏空护盾**：针对短时间内高频跨越 $\ge 6$ 个学科的异常批量抓取行为，自动降级为**零文本证明模式（Zero-Text Proof Mode）**，仅输出坐标与哈希前缀。

---

## 📄 开源协议

MIT License. 详见 [LICENSE](LICENSE)。
