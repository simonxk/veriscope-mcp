# 🛡️ VeriScope (真镜 · 数字翰林院) — 全球开源贡献者宪章与悬赏激励规则 (v1.0)

> 📌 **当前状态：规则宪章与六道自动化门禁已定稿就绪（待指挥部确认后正式对外开启悬赏通道）**  
> **Status: Rules & Automated Gatekeepers Established — Pending Official Bounty Launch Confirmation**

欢迎加入 **VeriScope (真镜)** 开源认知基建生态！

我们的核心使命是打造 AI 时代的 **「人机信任交接防伪标准（Cognitive SSL）」** 与 **「第一性原理幕僚军火库」**：让任何个人、学者、政企幕僚或 AI Agent 在面对平庸的 AIGC 塑料套话与同质化内卷时，都能零门槛完成 **「🔪 祛 AI 味重铸 + 🧠 24 学科第一性原理升维 + 🛡️ 红蓝军魔鬼质询 + 🔒 64 位 SHA-256 密码学防伪验真」**。

---

## 一、 开源共建与主权闭源的物理边界（Open-Core Sovereignty Boundary）

为确保社区贡献的高复用度与后端证据母港的绝对安全，VeriScope 严格实行 **「外围规则库 100% 开源共建，后端证据母港 100% 物理隔离闭源」** 的双轨宪章：

| 层次 | 资产范围 | 开放属性 | 说明 |
| :--- | :--- | :--- | :--- |
| **外围规则与客户端层** | `contrib/de-slop-packs/`（行业祛黑话字典）<br>`contrib/redteam-personas/`（魔鬼质询角色卡）<br>`contrib/ontology-proposals/`（痛点 $\to$ 原典映射提案）<br>`bin/` & `src/`（零依赖 MCP 客户端与防伪核验器） | **100% MIT 开源共建** | 欢迎全球开发者、咨询顾问、学者、行业专家提交 PR 共建，共享算力与荣衔激励 |
| **核心证据母港层** | 74,800+ 跨学科五联核专论大典库<br>189,000+ 权威馆藏原典全文 FTS5 索引<br>Ed25519 主权签名私钥与网关风控引擎 | **100% 主权闭源隔离** | 严禁任何形式的底层库导出或私钥接触；仅通过受控 API 按配额提供密码学签名收据 |

---

## 二、 三大社区贡献赛道与硬性准入规则（Contribution Tracks & Quality Rules）

所有社区提交的 Pull Request 均统一存放于 `contrib/` 目录下，分为三大标准化赛道：

### 赛道 A：🔪 行业祛 AI 味黑话手术包（`contrib/de-slop-packs/*.json`）
针对特定垂直行业（政务公文、互联网大厂、金融投研、学术基金申报、制造业供应链、医疗合规等）中泛滥的 AIGC 塑料套话与正确的废话，提供精准手术刀规则。
- **准入硬规则**：
  1. 单个 PR 至少新增或完善 **$\ge 5$ 条** 真实高频行业黑话（`rules` 数组）；
  2. 每条规则必须包含：
     - `rule_id`：全局唯一编号（格式：`DSLOP-<LANG/SECTOR>-<NNN>`，如 `DSLOP-ZH-007`）；
     - `industry`：所属行业枚举（`gov_public` / `internet_tech` / `finance_consulting` / `academic_grant` / `manufacturing_supply` / `healthcare_biotech` / `general_business`）；
     - `slop_phrase`：待拦截的黑话原词（$\ge 2$ 字，且不得与现有词条重复）；
     - `diagnosis_reason`：一针见血指出该黑话掩盖了什么实质问题（$\ge 10$ 字）；
     - `executive_replacement`：幕僚极简定稿替换方案（$\ge 6$ 字，**严禁在替换词中再次包含原黑话**）；
     - `mckinsey_replacement`：战略公理化替换方案（$\ge 6$ 字）；
     - `contributor_github`：贡献者 GitHub ID。

### 赛道 B：🛡️ 上会/投标红蓝军魔鬼质询角色卡（`contrib/redteam-personas/*.json`）
模拟最挑剔的审视者（如集团 CFO、投委会合伙人、纪检审计主任、政企评标专家、期刊主编），在方案上会或投标前剥离脆弱隐含前提并给出防弹补丁。
- **准入硬规则**：
  1. 单个 PR 至少新增 **$\ge 2$ 张** 完整的高仿真质询角色卡（`personas` 数组）；
  2. 每张角色卡必须包含：
     - `persona_id`：唯一编号（格式：`RT-PERSONA-<ROLE>-<NN>`）；
     - `role_title` 与 `scenario`：审视者身份与适用场景；
     - `trigger_keywords`：至少 $\ge 2$ 个触发关键词；
     - `hidden_premise_exposed`：剥离出的脆弱隐含前提（$\ge 15$ 字）；
     - `killer_question`：模拟审视者最毒辣的一针见血追问（$\ge 15$ 字）；
     - `historical_precedent`：真实商业败局、法学判例或思想史先例（$\ge 15$ 字，拒绝虚构）；
     - `bulletproof_patch_template`：**必须以 `【防弹补丁】` 开头**，给出可直接复制进方案的具体制度/条款修补动作（$\ge 25$ 字）。

### 赛道 C：🧠 世俗痛点 $\to$ 24 学科第一性原理映射提案（`contrib/ontology-proposals/*.json`）
将高频职场、管理或商业痛点词群，映射至 24 学科第一性原理概念与华夏制度史对勘。
- **准入硬规则**：
  1. `proposal_id` 格式须为 `ONT-PROP-<NNN>`；
  2. `pain_point_triggers` 至少包含 **$\ge 3$ 个** 真实高频痛点词；
  3. `first_principles_mapping_rationale` 须清晰阐述从表象痛点到第一性原理公理的推演链条（$\ge 30$ 字）；
  4. `eastern_institutional_counterpart` **必须包含 `【华夏制度对勘】` 标签**，并引用真实可考的中国历代制度史或经典文献对勘。

---

## 三、 七道自动化法医门禁与反刷单铁律（Automated Gatekeepers & Anti-Spam Charter）

为杜绝低质 AI 批量水贴、Prompt 注入攻击与刷单套利，任何 PR 必须首先 100% 通过自动化校验脚本（GitHub Actions CI 将在每次提交时自动执行）：

```bash
python scripts/validate_contrib_rules.py
```

1. **V1 [Schema & Depth Guard]**：必填字段完整性、ID 正则规范与最低学理阐述/防弹补丁字数强制核验；
2. **V2 [Anti-Slop Self-Contradiction]**：祛黑话替换词自身不得包含原黑话或空泛套话；
3. **V3 [Prompt-Injection & XSS Guard]**：零容忍拦截任何包含 `ignore previous instructions`、`system prompt`、`<script>` 或 Shell 危险命令的恶意规则；
4. **V4 [Clean-Room Sovereignty Guard]**：零容忍拦截任何内部物理路径、私有数据库文件名或违规宣传词；
5. **V5 [Deduplication Guard]**：严禁出现重复的 `rule_id` / `persona_id` / `proposal_id` 或重复黑话词条；
6. **V6 [Lightweight Budget Guard]**：`contrib/` 目录总物理体积严格控制在 `100 KB` 预算以内，确保开源包极速加载；
7. **V7 [Cross-Reference & Canonical Integrity Guard]**：映射提案的 `target_concept_id` 与 `target_concept_zh` 必须在黄金沙盒原典底座中真实存在且严格吻合，拒绝虚构概念映射。

### 🚫 反刷单与风控红线（Anti-Gaming Rules）
- **仅限 Merged PR 计奖**：仅提交 PR 但未通过法医校验与维护者人工学理复核（未 Merged）者，不计入奖励；
- **严禁拆分凑数**：将同一行业的 5 条黑话恶意拆分为 5 个独立 PR 提交者，合并按 1 次计算，情节严重者取消资格；
- **账号与月度封顶**：申领算力奖励的 GitHub 账号注册时间须满 **30 天**，同一自然人/账号每月最高申领上限为 **2,000 Pro Credits**。

---

## 四、 贡献者三级算力悬赏与「数字翰林院」荣衔体系（Reward & Honor System）

> *(注：以下悬赏额度为拟定标准，待指挥部正式发布上线公告后开始计发)*

### 1. 算力点数激励（VeriScope Pro Credits Bounty）
| 贡献类别 | 单次合入（Merged PR）奖励额度 | 等值权益说明 |
| :--- | :--- | :--- |
| **赛道 A：行业黑话手术包**（$\ge 5$ 条高质量规则） | **200 Pro Credits** | 可用于 200 次母港原典全文切片穿透定位（约合 ¥28） |
| **赛道 B：红蓝军魔鬼质询角色卡**（$\ge 2$ 张深度卡片） | **300 Pro Credits** | 可用于 300 次母港原典全文切片穿透定位（约合 ¥40） |
| **赛道 C：第一性原理与华夏制度对勘提案**（$\ge 2$ 项完整映射） | **500 Pro Credits** | 等同于 1 份标准点数包（¥68 / \$10 价值） |
| **旗舰行业全景包**（同一垂直行业黑话+质询+映射全套 $\ge 15$ 项） | **1,000 Pro Credits 或 1 个月 Scholar Pro** | 享全月高频深水区穿透与专属致谢（¥128 / \$19 价值） |

### 2. 数字翰林院学术荣衔（Academic Honor Roll）
- 🎖️ **数字翰林·庶吉士（VeriScope Contributor）**：累计合入 **1 个** 高质量 PR，荣登仓库 `README.md` 贡献者榜单；
- 🏅 **数字翰林·编修（VeriScope Senior Editor）**：累计合入 **5 个** 高质量 PR，在公网对应行业概念页（`https://veriscope.cc/c/...`）获得永久联合编修署名；
- 👑 **数字翰林·侍讲学士（VeriScope Distinguished Fellow）**：累计合入 **15 个** 高质量 PR，授予年度荣誉学士铭牌与机构级沙盒优先体验权。



---

## 五、 开发者原创证书（Developer Certificate of Origin, DCO 1.1）签署协议

为保障开源项目的知识产权合规性与全体用户的法律安全，VeriScope 遵循 Linux 基金会通行的 **DCO 1.1（开发者原创证书）** 协议：

1. **提交签署规范（Sign-off）**：  
   每一笔包含代码或规则的提交，贡献者必须使用 `git commit -s` 进行签署，在 commit message 末尾生成形如以下的署名行：
   ```text
   Signed-off-by: 真实姓名或法定代号 <your.email@example.com>
   ```
2. **开源授权确权（MIT License Confirmation）**：  
   签署即代表贡献者郑重声明并保证：提交的贡献内容为本人独立创作或拥有完整合法授权，且同意依据本仓库根目录下的 **MIT License** 向公众及 VeriScope 永久、免费、全球性地授予使用、复制、修改、合并、出版、发行及子许可之权利。
3. **主权基座集成授权**：  
   贡献者明确知悉并同意，通过法医校验并经维护者合并（Merged）的开源规则，将被索引并动态挂载至 VeriScope 的开放核心服务中，供全球个人学者与企业幕僚调用。

---

## 六、 平台研究算力点数权属与合规法律声明（Virtual Pro Credits Terms of Use）

为确保激励计划依法合规、公开透明，凡申领或获取 VeriScope Pro Credits 的贡献者须阅读并同意以下条款：

1. **非现金与虚拟研究权益性质（Non-Cash Scholarly Rights）**：  
   VeriScope Pro Credits 属于平台内虚拟学术研究调用凭证，**非任何形式的法定货币、预付代币、证券或虚拟资产**。点数严禁以任何形式兑换现金、转让、质押、继承或进行场外二次交易。
2. **权益有效期（Validity Period）**：  
   自发放合入之日起计，每次奖励之 Pro Credits 有效期为 **365 个自然日**。超期未使用的点数将自动归档注销，不予延期或补发。
3. **合规准入与主体资格（Eligibility & Age Limit）**：  
   贡献者须年满 **18 周岁** 且具备完全民事行为能力；未成年人须在法定监护人的指导与知情同意下参与。贡献者应自行确保提交行为符合所在司法管辖区的知识产权与劳动合规要求。
4. **自动化门禁与人工学理双重复核（Dual Audit Gate）**：  
   所有 PR 必须同时通过 GitHub Actions 七道法医门禁（V1~V7）与数字翰林院维护者学理复审方可合入。对于任何试图利用自动化脚本注水、刷单作弊、拆分恶意刷分或侵犯第三方合法权益的行为，VeriScope 保留不予合并、撤销已发放点数及封禁对应 GitHub 账号的权利。单自然人月度最高申领上限为 **2,000 Pro Credits**。
