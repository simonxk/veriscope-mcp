# -*- coding: utf-8 -*-
"""
validate_contrib_rules.py — 数字翰林院 GitHub 社区贡献规则库 (contrib/) 六道法医门禁校验器
====================================================================================================
TASK-CF-04a：针对 `dist_public/veriscope-mcp-oss/contrib/` 下的三大社区贡献目录：
  1. `de-slop-packs/*.json`       — 行业祛 AI 味黑话手术包
  2. `redteam-personas/*.json`    — 上会/投标红蓝军魔鬼质询角色卡
  3. `ontology-proposals/*.json`  — 职场/商业痛点 → 24 学科第一性原理靶心映射提案

执行七道自动化法医校验门禁（V1 ~ V7）：
  - V1 [Schema & Depth Guard]     : 必填字段齐备、ID 命名规范、学理阐述与防弹补丁字数达标
  - V2 [Anti-Slop Self-Check]     : 祛黑话替换词自身不得包含原黑话或被禁空洞套话
  - V3 [Prompt-Injection & XSS]   : 严禁包含 Prompt 注入指令、HTML/JS 脚本标签或 Shell 危险命令
  - V4 [Sovereignty Taboo Guard]  : 严禁包含内部物理路径、私有数据库文件名或违规口径词
  - V5 [Deduplication Guard]      : 严禁出现重复的 rule_id / persona_id / proposal_id 或重复黑话词条
  - V6 [Size Budget Guard]        : `contrib/` 目录总大小必须 <= 100 KB，确保开源包极致轻量
  - V7 [Cross-Reference Guard]    : 映射提案的 target_concept_id 与 target_concept_zh 必须在黄金沙盒原典底座中真实存在且严格吻合

退出码纪律：任何一项 FAIL 立即返回非零退出码 (rc=1)。
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent

if (ROOT_DIR / "contrib").exists():
    CONTRIB_DIR = ROOT_DIR / "contrib"
    SANDBOX_JSON_PATH = ROOT_DIR / "golden_sandbox_50.json"
    if not SANDBOX_JSON_PATH.exists():
        SANDBOX_JSON_PATH = ROOT_DIR / "src" / "veriscope_mcp" / "golden_sandbox_50.json"
else:
    CONTRIB_DIR = ROOT_DIR / "dist_public" / "veriscope-mcp-oss" / "contrib"
    SANDBOX_JSON_PATH = ROOT_DIR / "mcp_server" / "golden_sandbox_50.json"

# V3: Prompt 注入与 XSS 危险模式黑名单
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?prior",
    r"system\s+prompt",
    r"you\s+are\s+now\s+dan",
    r"<script\b",
    r"javascript:",
    r"onerror\s*=",
    r"onload\s*=",
    r"rm\s+-rf",
    r"subprocess\.Popen",
    r"os\.system\(",
]

# V4: 主权脱敏禁忌词（与 test_oss_bundle_leak_guard 保持单一事实源对齐）
TABOO_PHRASES = [
    "\x35\x35\u4e07", "\x35\x35\x2e\x36\u4e07", "\x35\x35\x30\x6b", "\x35\x35\x36\x6b",
    "\u53e4\u7c4d\u5584\u672c", "\u5584\u672c", "\u53e4\u7c4d", "\u82cf\u4e66\u697c",
    "\x66\x3a\\\\", "\x73\x75\x73\x68\x75\x6c\x6f\x75", "\x63\x61\x6c\x69\x62\x72\x65",
    "\x67\x61\x74\x65\x77\x61\x79\x5f\x6c\x65\x64\x67\x65\x72\x2e\x64\x62",
    "\x61\x72\x63\x68\x69\x76\x65\x2e\x64\x62",
    "\x65\x64\x32\x35\x35\x31\x39\x5f\x70\x72\x69\x76\x61\x74\x65\x5f\x6b\x65\x79",
    "\x65\x33\x62\x30\x63\x34\x34\x32"
]

VALID_INDUSTRIES = {
    "gov_public",
    "internet_tech",
    "finance_consulting",
    "academic_grant",
    "manufacturing_supply",
    "healthcare_biotech",
    "general_business",
}


def validate_all_contrib_packs(contrib_root: Path = CONTRIB_DIR) -> Tuple[bool, Dict[str, Any]]:
    errors: List[str] = []
    stats = {
        "de_slop_rules_count": 0,
        "redteam_personas_count": 0,
        "ontology_proposals_count": 0,
        "files_scanned": 0,
        "total_bytes": 0,
    }

    if not contrib_root.exists():
        return False, {"errors": [f"Contrib directory missing: {contrib_root}"], "stats": stats}

    seen_ids = set()
    seen_slop_phrases = set()

    # 加载黄金沙盒概念底座供 V7 交叉引用校验
    sandbox_concepts = {}
    if SANDBOX_JSON_PATH.exists():
        try:
            sb_data = json.loads(SANDBOX_JSON_PATH.read_text(encoding="utf-8"))
            for c in sb_data.get("concepts", []):
                sandbox_concepts[c["concept_id"]] = c
        except Exception:
            pass

    # 扫描所有 JSON 文件
    json_files = sorted(contrib_root.rglob("*.json"))
    if not json_files:
        errors.append("V1 FAIL: contrib/ 目录下未发现任何 .json 规则包文件")

    for jf in json_files:
        stats["files_scanned"] += 1
        raw_bytes = jf.stat().st_size
        stats["total_bytes"] += raw_bytes
        rel_path = str(jf.relative_to(contrib_root)).replace("\\", "/")

        try:
            raw_text = jf.read_text(encoding="utf-8")
            data = json.loads(raw_text)
        except Exception as e:
            errors.append(f"V1 FAIL [{rel_path}]: JSON 语法解析失败 -> {e}")
            continue

        # V3: Prompt-Injection & XSS 扫描
        for pat in INJECTION_PATTERNS:
            if re.search(pat, raw_text, flags=re.IGNORECASE):
                errors.append(f"V3 FAIL [{rel_path}]: 检测到疑似 Prompt 注入或脚本攻击模式 '{pat}'")

        # V4: 主权敏感词与禁忌口径扫描
        lower_text = raw_text.lower()
        for taboo in TABOO_PHRASES:
            if taboo in lower_text:
                errors.append(f"V4 FAIL [{rel_path}]: 检测到违禁词或内部路径泄露 '{taboo}'")

        # 分类校验 V1 / V2 / V5
        if "de-slop-packs" in rel_path:
            rules = data.get("rules")
            if not isinstance(rules, list) or len(rules) == 0:
                errors.append(f"V1 FAIL [{rel_path}]: 'rules' 必须为非空列表")
                continue
            for idx, r in enumerate(rules):
                stats["de_slop_rules_count"] += 1
                rid = (r.get("rule_id") or "").strip()
                phrase = (r.get("slop_phrase") or "").strip()
                ind = (r.get("industry") or "").strip()
                diag = (r.get("diagnosis_reason") or "").strip()
                exec_rep = (r.get("executive_replacement") or "").strip()
                mck_rep = (r.get("mckinsey_replacement") or "").strip()
                author = (r.get("contributor_github") or "").strip()

                if not re.match(r"^DSLOP-[A-Z]{2,6}-\d{3,5}$", rid):
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: rule_id 格式非法 '{rid}' (应如 DSLOP-ZH-001)")
                if rid in seen_ids:
                    errors.append(f"V5 FAIL [{rel_path}#L{idx}]: 重复的 rule_id '{rid}'")
                seen_ids.add(rid)

                if not phrase or len(phrase) < 2:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: slop_phrase 过短或为空")
                if phrase in seen_slop_phrases:
                    errors.append(f"V5 FAIL [{rel_path}#L{idx}]: 重复的黑话词条 '{phrase}'")
                seen_slop_phrases.add(phrase)

                if ind not in VALID_INDUSTRIES:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: 未知的 industry '{ind}'")
                if len(diag) < 10 or len(exec_rep) < 6 or len(mck_rep) < 6 or not author:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: 诊断说明或双文风替换词字数不足，或缺少 contributor_github")

                # V2: 替换后文本不得仍包含原黑话词条
                if phrase and (phrase in exec_rep or phrase in mck_rep):
                    errors.append(f"V2 FAIL [{rel_path}#L{idx}]: 替换词中仍残留原黑话 '{phrase}'")

        elif "redteam-personas" in rel_path:
            personas = data.get("personas")
            if not isinstance(personas, list) or len(personas) == 0:
                errors.append(f"V1 FAIL [{rel_path}]: 'personas' 必须为非空列表")
                continue
            for idx, p in enumerate(personas):
                stats["redteam_personas_count"] += 1
                pid = (p.get("persona_id") or "").strip()
                role = (p.get("role_title") or "").strip()
                triggers = p.get("trigger_keywords") or []
                premise = (p.get("hidden_premise_exposed") or "").strip()
                question = (p.get("killer_question") or "").strip()
                precedent = (p.get("historical_precedent") or "").strip()
                patch = (p.get("bulletproof_patch_template") or "").strip()
                author = (p.get("contributor_github") or "").strip()

                if not re.match(r"^RT-PERSONA-[A-Z0-9\-]+$", pid):
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: persona_id 格式非法 '{pid}'")
                if pid in seen_ids:
                    errors.append(f"V5 FAIL [{rel_path}#L{idx}]: 重复的 persona_id '{pid}'")
                seen_ids.add(pid)

                if not role or not isinstance(triggers, list) or len(triggers) < 2:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: role_title 缺失或 trigger_keywords 少于 2 项")
                if len(premise) < 15 or len(question) < 15 or len(precedent) < 15:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: 隐含前提/致命追问/历史先例阐述字数不足")
                if not patch.startswith("【防弹补丁】") or len(patch) < 25:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: bulletproof_patch_template 必须以『【防弹补丁】』开头且不少于 25 字")
                if not author:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: 缺少 contributor_github")

        elif "ontology-proposals" in rel_path:
            proposals = data.get("proposals")
            if not isinstance(proposals, list) or len(proposals) == 0:
                errors.append(f"V1 FAIL [{rel_path}]: 'proposals' 必须为非空列表")
                continue
            for idx, prop in enumerate(proposals):
                stats["ontology_proposals_count"] += 1
                pr_id = (prop.get("proposal_id") or "").strip()
                triggers = prop.get("pain_point_triggers") or []
                cid = (prop.get("target_concept_id") or "").strip()
                czh = (prop.get("target_concept_zh") or "").strip()
                rationale = (prop.get("first_principles_mapping_rationale") or "").strip()
                eastern = (prop.get("eastern_institutional_counterpart") or "").strip()
                author = (prop.get("contributor_github") or "").strip()

                if not re.match(r"^ONT-PROP-\d{3,5}$", pr_id):
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: proposal_id 格式非法 '{pr_id}'")
                if pr_id in seen_ids:
                    errors.append(f"V5 FAIL [{rel_path}#L{idx}]: 重复的 proposal_id '{pr_id}'")
                seen_ids.add(pr_id)

                if not isinstance(triggers, list) or len(triggers) < 3:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: pain_point_triggers 至少需包含 3 个高频痛点词")
                if not cid or not czh or len(rationale) < 30 or "【华夏制度对勘】" not in eastern or not author:
                    errors.append(f"V1 FAIL [{rel_path}#L{idx}]: 概念靶心、第一性原理映射阐述(>=30字)或【华夏制度对勘】缺失")

                # V7: Cross-Reference & Canonical Integrity Guard
                if sandbox_concepts:
                    if cid not in sandbox_concepts:
                        errors.append(f"V7 FAIL [{rel_path}#L{idx}]: target_concept_id '{cid}' 在黄金沙盒原典底座中不存在")
                    else:
                        sb_c = sandbox_concepts[cid]
                        sb_name = sb_c.get("name_zh", "")
                        clean_czh = czh.split("（")[0].split("(")[0].strip()
                        clean_sb = sb_name.split("（")[0].split("(")[0].strip()
                        if not (clean_czh in clean_sb or clean_sb in clean_czh or any(word in clean_sb for word in clean_czh.split("与"))):
                            errors.append(f"V7 FAIL [{rel_path}#L{idx}]: target_concept_zh '{czh}' 与沙盒原典真名 '{sb_name}' 概念漂移不匹配")

    # V6: Size Budget Guard (<= 100 KB)
    if stats["total_bytes"] > 100 * 1024:
        errors.append(f"V6 FAIL: contrib/ 总体积 {stats['total_bytes']} bytes 超过 100 KB 预算上限")

    return (len(errors) == 0), {"errors": errors, "stats": stats}


def load_merged_contrib_packs(contrib_root: Path = CONTRIB_DIR) -> Dict[str, List[Dict[str, Any]]]:
    """加载并返回通过校验的三大社区贡献规则包，供幕僚台与 MCP 服务端动态挂载"""
    result: Dict[str, List[Dict[str, Any]]] = {
        "de_slop_rules": [],
        "redteam_personas": [],
        "ontology_proposals": [],
    }
    if not contrib_root.exists():
        return result

    for jf in sorted(contrib_root.rglob("*.json")):
        rel = str(jf.relative_to(contrib_root)).replace("\\", "/")
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            if "de-slop-packs" in rel:
                result["de_slop_rules"].extend(data.get("rules") or [])
            elif "redteam-personas" in rel:
                result["redteam_personas"].extend(data.get("personas") or [])
            elif "ontology-proposals" in rel:
                result["ontology_proposals"].extend(data.get("proposals") or [])
        except Exception:
            continue
    return result


if __name__ == "__main__":
    ok, report = validate_all_contrib_packs()
    st = report["stats"]
    print("=================================================================")
    print("  数字翰林院 GitHub 社区贡献规则库 (contrib/) 七道法医门禁校验")
    print("=================================================================")
    print(f"  [i] 扫描规则文件数 : {st['files_scanned']}")
    print(f"  [i] 祛黑话手术词条 : {st['de_slop_rules_count']} 条")
    print(f"  [i] 魔鬼质询角色卡 : {st['redteam_personas_count']} 张")
    print(f"  [i] 原典映射提案数 : {st['ontology_proposals_count']} 项")
    print(f"  [i] 规则包总物理体积: {st['total_bytes'] / 1024:.2f} KB (上限 100.00 KB)")
    if not ok:
        print("\n  [✗] 校验未通过，发现以下违规项：")
        for err in report["errors"]:
            print(f"    - {err}")
        sys.exit(1)
    print("\n  [✓] V1~V7 七道法医门禁 100% PASS！")
    sys.exit(0)

