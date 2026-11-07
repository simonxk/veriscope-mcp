# 真镜 v3.0 MCP Server

> **真镜** = 知识证据溯源系统。素书楼馆藏实体原本与全量学术文献 (FTS5+INSTR 段落级定位) · 7.5万张卡片 (22学科) · 2.1万条双链 · 27个学术社区 · 476万共现对。核心动作：输入命题 → 输出可信等级 + 支持/反对证据 + 谱系 + 盲区 + 原文锚点。

---

## 这是什么？

**MCP Server** 是真镜的 **Model Context Protocol (MCP)** 服务端实现，把真镜的 5 个核心 Skill（三态取证 / 概念地形图 / 书目深挖 / 验证 / 学者谱系）暴露为标准化的 MCP Tools。

**为什么需要？**
- 40+ AI Agent（Claude Code / Cursor / Codex / Gemini / 等）可通过 MCP 协议**直接调用真镜能力**，无需浏览器插件
- 这是真镜 v3.0 **L4 生态与入口层**的关键一环（见架构文档 §二·四层架构模型 L4）
- **不是 Chrome 插件的替代**——插件入口思维不变（§七-4 不变量），MCP Server 是**额外的入口**，服务于 AI Agent 生态

---

## 核心能力（5 个 MCP Tools）

| Tool 名称 | 对应 Skill | 端点 | 说明 |
|-----------|------------|------|------|
| `three-state-evidence` | 三态取证 | `/api/collision/duel` | 相关/对立/缺口 三态证据验证 |
| `concept-terrain` | 概念地形图 | `/api/concept/terrain` | 概念的层位、谱系、盲区全景 |
| `book-deep-dive` | 书目深挖 | `/api/topology/evidence-concept` | 单本书的论点、谱系、关联卡片、盲区 |
| `verify` | 验证模式 | `/api/collision/en` | 英文入口：声明溯源 + 对立证据 |
| `scholar-lineage` | 学者谱系 | `/api/thinker/biography` | 学者的影响、代表作、关联思想家 |

---

## 安装

```bash
cd F:\翰林院AI总账本
pip install mcp  # 可选，mock 模式不需要
```

> **零额外依赖**：核心逻辑仅用标准库。`mcp` 包仅在真实 MCP 连接时需要；mock 模式（`--list-tools`）零依赖。

---

## 启动方式

### 1. MCP stdio 模式（供 AI Agent 连接）
```bash
python -m mcp_server.veriscope_mcp_server
```

### 2. Mock 模式（无 MCP SDK 时验证）
```bash
python -m mcp_server.veriscope_mcp_server --list-tools
python -m mcp_server.veriscope_mcp_server --call-tool three-state-evidence --args '{"lens_card_id":"abc","opponent_card_id":"def"}'
```

---

## 与 AI Agent 集成示例

### Claude Code / Cursor / Codex / Gemini
```json
{
  "mcpServers": {
    "veriscope": {
      "command": "python",
      "args": ["-m", "mcp_server.veriscope_mcp_server"],
      "cwd": "F:/翰林院AI总账本"
    }
  }
}
```

---

## 架构定位：与 v3.0 §七-4 不变量的关系

> **不变量 4：插件入口思维不变** —— 所有外部入口（MCP / Skill Registry）最终汇聚到 Chrome 插件这一人类入口

```
L4: Chrome插件(人类) / MCP Server(AI Agent) / Skill Registry / K-Dense互导流
  ↓ 统一路由（建议1）
L2: archive_server.py 统一路由技能
  ↓
L3: 三态取证 / Evidence Object 9字段 / 行级锚定
  ↓
L1: 素书楼学术原典实物物证库 + FTS5 + INSTR + SHA256
```

**关键点**：
- MCP Server **不绕过** archive_server.py，通过 `skills_adapter.py` **直接 import 调用** view function
- 所有证据产出遵循 **Evidence Object 9 字段 schema**（`evidence_object_schema.json`）
- 三态取证（相关/对立/缺口）哲学核心 **不变**（§七-3）

---

## 与 K-Dense plugin.json 的关系

参考 `decisions/_refs/k_dense_scientific_agent_skills_v2.64.0/plugin.json`（23 行标准模板）。真镜 MCP Server 遵循同一 **Agent Plugins 1.0.0 标准**：
- `name`/`version`/`description`/`author`/`license`/`keywords` 字段对齐
- Skill 目录结构遵循 K-Dense 硬规范：`SKILL.md` + `references/` + `scripts/` + `assets/`
- `metadata.version` 必须引号包字符串（如 `"0.1"`）
- `allowed-tools` 为空格分隔字符串

---

## 内部实现要点

| 文件 | 职责 | 行数 |
|------|------|------|
| `veriscope_mcp_server.py` | MCP Server 核心，优雅降级，stdio transport | ~160 |
| `skills_adapter.py` | registry.json → MCP Tool 定义 + 本地调用 archive_server | ~180 |
| `__init__.py` | 包元信息 | ~15 |

**关键设计**：
1. **不强依赖 mcp SDK**：`try/except ImportError` 优雅降级，mock 模式可独立运行
2. **本地调用而非 HTTP**：Flask `test_request_context` 直接调用 view function，零网络开销
3. **param_mapping 自动生成 schema**：registry.json → JSON Schema（inputSchema）
4. **stdio transport**：标准 MCP 协议，兼容所有 MCP Client

---

## 验证

```bash
python -c "import ast; ast.parse(open('mcp_server/veriscope_mcp_server.py', encoding='utf-8').read())"
python -c "import ast; ast.parse(open('mcp_server/skills_adapter.py', encoding='utf-8').read())"
python -m mcp_server.veriscope_mcp_server --list-tools  # 应显示 5 个 tool
python -m mcp_server.skills_adapter
```

---

## 回归风险控制

| 风险 | 对策 |
|------|------|
| 改动现有文件 | **严禁**改动 `archive_server.py` / `prompts.toml` / `sidebar.*` 等 |
| 强依赖 mcp SDK | `try/except` 优雅降级，mock 模式完整可用 |
| 引入额外依赖 | 仅标准库 + `mcp`（可选） |
| 暴露 secrets | 无 API key / secret 硬编码 |
| 破坏插件入口 | MCP Server 只是**额外入口**，插件主入口不受影响 |

---

## 后续规划（P2 阶段）

- [ ] 真实 MCP SDK 集成测试
- [ ] Evidence Object 9 字段在 tool 返回中透传
- [ ] 支持 `/skill/<name>` 统一路由技能（建议 1）
- [ ] K-Dense 互导流：双向路由 + 数据交换
- [ ] 安全扫描集成（Cisco AI Defense Skill Scanner）

---

## 许可证

MIT License — 与真镜主项目一致。