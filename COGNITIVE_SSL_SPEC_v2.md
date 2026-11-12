# 🛡️ Cognitive SSL v2.0 规范：人机信任交接防伪标准与双轨存证草案
# (Cognitive SSL v2.0: Dual Attestation, Document Seal & Transparency Log Specification)

> **标准版本**：v2.0 (2026-11)  
> **发布机构**：VeriScope Sovereign Harbor & Open Community  
> **开源协议**：MIT License  
> **参考实现**：`dist_public/veriscope-mcp-oss` / `mcp_server/gateway_ledger.py`

---

## 一、 诞生背景与威胁模型 (Threat Model)

在生成式 AI (AIGC) 渗透公文撰写、投研立项、招投标答辩与学术出版的背景下，传统数字证书（如 X.509 SSL/TLS）仅能证明“通信管道的安全”，无法证明**“AI 生成物内容的真实性、出处与不可篡改性”**。

当前大模型生成内容面临三大刚性信任危机：
1. **重放冒用攻击（Citation Replay Attack）**：恶意作者将一段真实的原典引证收据直接复制粘贴到一篇毫无学术渊源甚至充满捏造幻觉的汇报中，冒充“通过防伪核验”；
2. **正文静默篡改（Silent Tampering）**：报告出具后，中间人修改了核心数据、结论或制度条款，原有的原典引证仍然存在，导致依赖方被误导；
3. **幻觉编造引文（Hallucinated Citation Fraud）**：大模型信口开河虚构书名、卷次与著者，导致全篇论据崩塌。

**Cognitive SSL v2.0** 将**「权威原典引证回执（Citation Receipt）」**与**「文档正文内容指纹（Document Seal）」**进行密码学二分绑定，实现**全流程 Ed25519 密码学签名验真与单字篡改即刻报警**。

---

## 二、 协议载荷格式 (Wire Format)

### 2.1 规范化验真载荷字符串 (Signed Message Schema)

Cognitive SSL v2 签名载荷采用冒号分隔的标准文本格式：

```text
VERISCOPE_ATTESTATION:v2:{kid}:{concept_id}:{canon_sha256}:{doc_sha256}:{slice_sha16}:{timestamp}
```

各字段严格定义如下：

| 字段 | 类型 | 说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `prefix` | 字符串常量 | 协议标识与主版本号 | `VERISCOPE_ATTESTATION:v2` |
| `kid` | 字符串 | 签名密钥标识符（支持轮换与吊销） | `ed25519-v1` |
| `concept_id` | 字符串 | 24 学科标准概念编号 | `VS-SOC-001` |
| `canon_sha256` | 64 位十六进制 | 馆藏实体学术原本的 64 位物理散列（真实原典） | `9b12d591c28cbb1d3ec1a1e4839cf9e52c8091ecb9b94092b781ecaa06f90112` |
| `doc_sha256` | 64 位十六进制 | 规范化文档正文内容的 SHA-256 指纹（文档钢印） | `a4b2c1...` |
| `slice_sha16` | 16 位十六进制 | 原典切片（$\le 300$ 字）哈希前 16 位（原典防掉包） | `4f3e2d1c0b9a8f7e` |
| `timestamp` | ISO 8601 UTC | 签发时间戳（精确至秒，Z 时区） | `2026-11-08T18:00:00Z` |

---

## 三、 正文规范化算法 (Document Canonicalization Algorithm)

为防止因跨操作系统换行符差异（`\r\n` vs `\n`）或复制粘贴引入的末尾空格导致误报篡改，在计算 `doc_sha256` 前必须对文档正文执行**幂等规范化**：

```python
def canonicalize_document_text(text: str) -> str:
    if not text:
        return ""
    # 1. 统一换行符
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    # 2. 剥离每行行末空白符
    lines = [line.rstrip() for line in normalized.split("\n")]
    # 3. 去除首尾连续空行
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    # 4. 返回规范化 UTF-8 文本
    return "\n".join(lines).strip()
```

---

## 四、 密码学算法与公钥登记 (Cryptographic Specifications)

- **签名算法**：Ed25519 (EdDSA over Curve25519，RFC 8032)
- **哈希算法**：SHA-256 (FIPS 180-4)
- **主权创世公钥 (Genesis Public Key)**：
  ```text
  be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93
  ```
- **纯前端零依赖验证**：支持浏览器端通过 `window.crypto.subtle` 原生 API 执行验真，无需向后端发送正文，零泄密风险。

---

## 五、 只追加哈希链透明日志结构 (Append-only Hash Chain Transparency Log)

为防止签发者事后伪造凭证或单方面抵赖，每一张签发的 Cognitive SSL v2 凭证均自动登记入**只追加哈希链透明日志（Append-only Hash Chain Transparency Log）**：

1. **单项哈希（Entry Hash）**：  
   $$\text{entry\_hash} = \text{SHA-256}(\text{signed\_message} \parallel \text{"|"} \parallel \text{signature})$$
2. **链哈希递推（Running Chain Hash）**：  
   $$H_n = \text{SHA-256}(H_{n-1} \parallel \text{"|"} \parallel \text{entry\_hash}_n)$$
3. **公开展布接口**：  
   第三方审稿人、合规机构或企业客户可通过 `GET /api/copilot/transparency-log?limit=50` 随时导出与对账整条追加式哈希链，确证凭证的存在性与时间序列不可篡改性。后续进阶版本规划升级为支持 Merkle Inclusion Proof 的 Merkle Tree 结构。

---

## 六、 依赖方与验证准则 (Relying Party Guidance)

| 验证场景 | 输入项 | 核验动作 | 判定结论 |
| :--- | :--- | :--- | :--- |
| **场景 A：仅核验证书真伪** | 凭证收据文本 | 提取公钥、载荷与 Ed25519 签名比对 | `CITATION_VERIFIED`（原典回执无伪） |
| **场景 B：全文防篡改双重核验** | 凭证收据 + 申报正文 | 规范化正文并计算 `doc_sha256`，与凭证锁定的哈希比对 | `DUAL_VERIFIED_AUTHENTIC`（双重验真通过，原典真实且正文未修改） |
| **正文被篡改警报** | 凭证收据 + 篡改后正文 | 计算得出的正文哈希与凭证不符 | `DOCUMENT_TAMPER_DETECTED`（篡改报警，精确识别单字变动） |
| **凭证签名被篡改** | 伪造凭证 | 公钥验签失败 | `SIGNATURE_TAMPER_DETECTED`（签名伪造拦截） |
