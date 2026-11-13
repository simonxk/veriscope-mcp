#!/usr/bin/env node
/**
 * VeriScope MCP Server — Node.js Implementation (Clean-Room Open Source Edition)
 * Zero-dependency stdio JSON-RPC 2.0 transport.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const https = require('https');
const http = require('http');
const crypto = require('crypto');

const VERISCOPE_PUBLIC_KEY_HEX = 'be55d985d725ec36594b32ed9d81226fcdb8be12a6da02fbdf231c3aa38f1f93';
const DEFAULT_GATEWAY_URL = process.env.VERISCOPE_GATEWAY_URL || 'https://api.veriscope.cc/v1/mcp';
const API_KEY = (process.env.VERISCOPE_API_KEY || '').trim();

let sandboxConcepts = [];
const sandboxMap = new Map();
const nameMap = new Map();

function loadSandbox() {
  const possiblePaths = [
    path.join(__dirname, '..', 'golden_sandbox_50.json'),
    path.join(__dirname, '..', 'src', 'veriscope_mcp', 'golden_sandbox_50.json'),
    path.join(__dirname, 'golden_sandbox_50.json')
  ];
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      try {
        const raw = fs.readFileSync(p, 'utf8');
        const data = JSON.parse(raw);
        sandboxConcepts = data.concepts || [];
        for (const c of sandboxConcepts) {
          if (c.concept_id) sandboxMap.set(c.concept_id, c);
          if (c.name_zh) nameMap.set(c.name_zh.toLowerCase(), c);
          if (c.name_en) nameMap.set(c.name_en.toLowerCase(), c);
        }
        return;
      } catch (err) {
        process.stderr.write(`[VeriScope MCP] Notice: failed to parse ${p}: ${err.message}\n`);
      }
    }
  }
}
loadSandbox();

function verifyEd25519Signature(pubHex, sigHex, msg) {
  try {
    if (!pubHex || !sigHex || !msg) return false;
    const cleanSig = String(sigHex).replace(/^vsk_sig:/, '').trim();
    if (cleanSig.length !== 128) return false;
    const cleanPub = String(pubHex).replace(/^0x/, '').trim();
    if (cleanPub.length !== 64) return false;

    const spkiPrefix = Buffer.from('302a300506032b6570032100', 'hex');
    const spkiDer = Buffer.concat([spkiPrefix, Buffer.from(cleanPub, 'hex')]);
    const keyObj = crypto.createPublicKey({ key: spkiDer, format: 'der', type: 'spki' });

    return crypto.verify(null, Buffer.from(msg, 'utf8'), keyObj, Buffer.from(cleanSig, 'hex'));
  } catch (err) {
    return false;
  }
}

const BUSINESS_SYNONYM_BRIDGE = [
  [['部门推诿', '跨部门协同', '周报', '报表负担', '流程繁琐', '大厂黑话', '体制内', '官僚', '执行变形'], '科层制'],
  [['价格战', '内卷', '补贴', '恶意降价', '渠道窜货', '同质化', '商业竞争', '毛利'], '看不见的手'],
  [['信息茧房', '算法推荐', '流量', '舆论', '品牌公关', '回音室'], '公共领域'],
  [['AI幻觉', '大模型套壳', '技术颠覆', '数字化转型', '产业升级', '第二曲线'], '范式转换'],
  [['合规', '数据主权', '监管', '权限边界', '治理', '责任倒查'], '社会契约'],
  [['甩锅', '言行不一', '形式主义', '认知偏差', '盲目立项'], '认知失调']
];

const TOOLS = [
  {
    name: 'veriscope_discover_concepts',
    description: '[Executive Framing & Concept Discovery] Elevate colloquial workplace/business pain points (e.g. bureaucracy, price wars, AI hype, executive briefings) or news metaphors into rigorous first-principles concepts across 24 disciplines to eliminate generic AI slop.',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Colloquial business/workplace problem, metaphor, or scholarly topic (e.g. \'跨部门推诿\', \'价格战\', \'iron cage\', \'panopticon\').'
        },
        discipline_hint: {
          type: 'string',
          description: 'Optional discipline hint (e.g. \'SOC\', \'PHIL\', \'LAW\', \'ECON\').'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'veriscope_inspect_topography',
    description: '[Red-Team Pre-Mortem & Dialectical Audit] Stress-test business proposals, policy drafts, or papers by retrieving axiomatic formal kernels, scholar lineages with Wikidata QIDs, and 3+ opposing dialectical disputes.',
    inputSchema: {
      type: 'object',
      properties: {
        concept_id: {
          type: 'string',
          description: 'Canonical concept identifier (e.g. \'VS-PHIL-001\', \'VS-SOC-001\').'
        }
      },
      required: ['concept_id']
    }
  },
  {
    name: 'veriscope_locate_evidence',
    description: '[De-Slop Grounding & Primary Source Proof] Locate fair-use verbatim excerpts (<=300 chars) with exact chapter coordinates, SHA-256 edition hash, and Ed25519 cryptographic receipt for high-stakes reports.',
    inputSchema: {
      type: 'object',
      properties: {
        concept_id: {
          type: 'string',
          description: 'Canonical concept identifier.'
        },
        query_context: {
          type: 'string',
          description: 'Optional sentence context to guide snippet anchor selection.'
        }
      },
      required: ['concept_id']
    }
  },
  {
    name: 'veriscope_verify_attestation',
    description: '[Cryptographic Receipt Verification] Mathematically verify the SHA-256 hash and Ed25519 cryptographic receipt of a cited quote to check text integrity.',
    inputSchema: {
      type: 'object',
      properties: {
        concept_id: {
          type: 'string',
          description: 'Canonical concept identifier.'
        },
        canon_sha256: {
          type: 'string',
          description: 'SHA-256 edition hash to verify against canonical records.'
        },
        attestation: {
          type: 'object',
          description: 'Optional full attestation receipt object.'
        }
      }
    }
  },
  {
    name: 'veriscope_probe_radar',
    description: '[Cross-Domain Blindspot & Innovation Radar] Probe matrix coverage, discipline distribution, and cross-disciplinary conceptual bridges across all 24 academic disciplines.',
    inputSchema: {
      type: 'object',
      properties: {
        discipline: {
          type: 'string',
          description: 'Optional discipline code to filter radar statistics.'
        }
      }
    }
  },
  {
    name: 'veriscope_citation_audit',
    description: '[Academic Citation Health Check & Attribution Auditor] Fast-scan draft articles or AI generated text to extract and verify book titles, authors, and citations against canonical editions and SHA-256 hashes to detect misattributions and phantom references.',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'Draft article, proposal, research brief, or AI-generated text containing book citations to audit.'
        },
        discipline_hint: {
          type: 'string',
          description: 'Optional discipline hint (e.g. \'SOC\', \'PHIL\', \'ECON\', \'LAW\').'
        }
      },
      required: ['text']
    }
  }
];


const AUTHOR_NOISE_WORDS = [
  '德意志哲学家', '德国哲学家', '法国哲学家', '英国经济学家', '美国社会学家',
  '古希腊哲学家', '古典政治学家', '社会学先驱', '法学先驱', '经济学大师',
  '著名哲学家', '学者', '教授', '先生', '作家', '部分学者', '然而', '但是',
  '认为', '强调', '指出', '提出', '声称', '根据', '按照'
];

const CHINESE_PRONOUNS = new Set([
  '他', '她在', '他在', '她', '它', '他们', '她们', '它们', '该作者', '此作者', '作者', '笔者', '本文', '在此', '其'
]);

function cleanAuthorName(raw) {
  let s = (raw || '').trim();
  for (const w of AUTHOR_NOISE_WORDS) {
    s = s.replace(w, '').trim();
  }
  // 清洗英文动词与引导介词（最长前缀优先匹配，避免 "as" 截断 "as noted by"）
  s = s.replace(/^(?:as noted by|according to|noted by|as|in|by)\s+/i, '');
  s = s.replace(/\s+(?:argues(?:\s+in)?|states(?:\s+in)?|claims(?:\s+in)?|writes(?:\s+in)?|shows|in)$/i, '');

  s = s.replace(/^[\s，,、“”"'（(：:【\[]+/, '').replace(/[\s，,、“”"'）)：:】\]]+$/, '');
  s = s.replace(/(?:在|于|中|里)$/, '').trim();
  if (s.includes('·')) {
    const parts = s.split('·');
    if (parts.length >= 2) {
      s = parts[parts.length - 2].trim().slice(-3) + '·' + parts[parts.length - 1].trim().slice(0, 6);
    }
  }
  s = s.trim();
  // 中文代词识别（如“他在《纯粹理性批判》中”）：不作为著者姓名比对，避免误报张冠李戴
  if (CHINESE_PRONOUNS.has(s) || CHINESE_PRONOUNS.has(s + '在')) {
    return '';
  }
  return s;
}

function cleanBookTitle(raw) {
  let s = (raw || '').trim();
  s = s.replace(/^(?:关于|论)\s*/, '');
  s = s.replace(/\s*(?:（[^）]+）|\([^)]+\))$/, '');
  return s.trim();
}

function extractCitationsFromText(text) {
  const content = text || '';
  const found = [];
  const seenTitles = new Set();

  // Pattern 1: 学者在《书名》 / 由学者所著《书名》
  const reAuthorBook = /(?:由|据|正如|如|在|根据)?\s*([·\u4e00-\u9fa5A-Za-z\s]{2,20}?)\s*(?:先生|教授|学者)?\s*(?:所著(?:的)?|在|于|的)?\s*《([^》\n]{2,60})》/g;
  let m;
  while ((m = reAuthorBook.exec(content)) !== null) {
    const author = cleanAuthorName(m[1]);
    const title = cleanBookTitle(m[2]);
    if (author.length >= 2 && title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        pattern: 'AUTHOR_IN_BOOK',
        index: m.index
      });
    }
  }

  // Pattern 2: 《书名》（著者，年份）
  const reBookAuthorYear = /《([^》\n]{2,60})》\s*(?:（|\()\s*([·\u4e00-\u9fa5A-Za-z\s]{2,20}?)\s*(?:[，,]\s*(\d{3,4}(?:\s*BC)?))?\s*(?:）|\))/g;
  while ((m = reBookAuthorYear.exec(content)) !== null) {
    const title = cleanBookTitle(m[1]);
    const author = cleanAuthorName(m[2]);
    if (author.length >= 2 && title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        year: (m[3] || '').trim(),
        pattern: 'BOOK_WITH_META',
        index: m.index
      });
    }
  }

  // Pattern 3: 独立《书名》
  const reBook = /《([^》\n]{2,60})》/g;
  while ((m = reBook.exec(content)) !== null) {
    const title = cleanBookTitle(m[1]);
    if (title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      const start = Math.max(0, m.index - 30);
      const pre = content.slice(start, m.index);
      let author = '';
      const mPre = /(?:由|在|据)?\s*([·\u4e00-\u9fa5]{2,6})\s*(?:在|的|于|所著)?$/.exec(pre);
      if (mPre) {
        author = cleanAuthorName(mPre[1]);
      }
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        pattern: 'BARE_BOOK',
        index: m.index
      });
    }
  }

  // Pattern 4: 英文引用 "Title" (Author, Year) or by Author
  const reEng = /["“]([^"”\n]{2,60})["”]\s*(?:\(\s*([A-Za-z\s]{2,25})\s*(?:,\s*(\d{4}))?\s*\)|by\s+([A-Za-z\s]{2,25}))/gi;
  while ((m = reEng.exec(content)) !== null) {
    const title = cleanBookTitle(m[1]);
    const author = cleanAuthorName(m[2] || m[4] || '');
    if (title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        year: m[3] || '',
        pattern: 'ENGLISH_QUOTE',
        index: m.index
      });
    }
  }

  // Pattern 5: 英文标准著录 Author, "Title" (Year) / Author, Title (Year) (例如 Kant, Critique of Pure Reason (1781))
  const reEngStd = /([A-Za-z\s]{2,25}),\s*(?:["“]|_|\*)?([A-Za-z\s]{2,60})(?:["”]|_|\*)?\s*\(\s*(\d{4})\s*\)/g;
  while ((m = reEngStd.exec(content)) !== null) {
    const author = cleanAuthorName(m[1]);
    const title = cleanBookTitle(m[2]);
    if (author.length >= 2 && title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        year: m[3] || '',
        pattern: 'ENGLISH_STD',
        index: m.index
      });
    }
  }

  // Pattern 6: As Author argues in "Title" / in Critique of Pure Reason
  const reEngArgues = /(?:As|as|In|in|According to)\s+([A-Za-z\s]{2,25})\s+(?:argues|states|claims|writes)?\s*(?:in)?\s*["“]([^"”\n]{2,60})["”]/g;
  while ((m = reEngArgues.exec(content)) !== null) {
    const author = cleanAuthorName(m[1]);
    const title = cleanBookTitle(m[2]);
    if (author.length >= 2 && title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        pattern: 'ENGLISH_ARGUES',
        index: m.index
      });
    }
  }

  // Pattern 7: 标准学术参考文献 APA 格式 (e.g. Rawls, J. (1971). A theory of justice.)
  const reEngApa = /([A-Z][a-zA-Z]+(?:,\s+[A-Z]\.(?:\s*[A-Z]\.)?)?)\s*\(\s*(\d{4})\s*\)\.\s*([A-Za-z0-9\s:,\-]{2,80}?)(?:\.|$)/g;
  while ((m = reEngApa.exec(content)) !== null) {
    const author = cleanAuthorName(m[1]);
    const title = cleanBookTitle(m[3]);
    if (author.length >= 2 && title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      found.push({
        raw_citation: m[0].trim(),
        author: author,
        title: title,
        year: m[2] || '',
        pattern: 'ENGLISH_APA',
        index: m.index
      });
    }
  }

  return found;
}

const GENERIC_STOPWORDS = new Set([
  '理论', '社会', '资本', '通论', '价值', '哲学', '国家', '历史', '政治', '经济', '文化', '批判',
  'theory', 'society', 'capital', 'value', 'philosophy', 'state', 'history', 'politics', 'economy', 'culture'
]);

function getCanonicalAuthor(c) {
  if (!c) return '';
  const pt = c.primary_thinker || '';
  const match = pt.match(/\(([^)]+)\)/);
  if (match && match[1].trim()) {
    return match[1].trim();
  }
  if (pt) return pt.trim();
  const anchor = c.canon_anchor || {};
  return anchor.author || '';
}

function matchSandboxConceptByTitle(title) {
  if (!title) return null;
  const qTitle = title.toLowerCase().trim();
  // 泛化单字/通用词禁止作为书名做模糊匹配
  if (GENERIC_STOPWORDS.has(qTitle) || qTitle.length < 2) {
    return null;
  }

  // 1. 经典中外名篇规范对齐（高优先级白名单，严格按书名匹配，严禁拿概念名模糊匹配）
  for (const c of sandboxConcepts) {
    const anchor = c.canon_anchor || {};
    const aTitle = (anchor.title || '').toLowerCase();
    if ((qTitle === '资本论' || qTitle === 'capital' || qTitle === 'das kapital') && (c.concept_id === 'VS-SOC-003' || aTitle.includes('资本论') || aTitle.includes('kapital'))) return c;
    if ((qTitle === '国富论' || qTitle === 'wealth of nations') && (c.concept_id === 'VS-ECON-001' || aTitle.includes('wealth of nations') || aTitle.includes('国富论'))) return c;
    if ((qTitle === '纯粹理性批判' || qTitle === 'critique of pure reason') && (c.concept_id === 'VS-PHIL-001' || aTitle.includes('reinen vernunft') || aTitle.includes('纯粹理性批判') || aTitle.includes('pure reason'))) return c;
    if ((qTitle === '正义论' || qTitle === 'theory of justice' || qTitle === 'a theory of justice') && (c.concept_id === 'VS-LAW-004' || aTitle.includes('theory of justice') || aTitle.includes('正义论'))) return c;
    if ((qTitle === '利维坦' || qTitle === 'leviathan') && (c.concept_id === 'VS-POL-001' || aTitle.includes('leviathan'))) return c;
    if ((qTitle === '经济与社会' || qTitle === 'economy and society') && (c.concept_id === 'VS-SOC-001' || aTitle.includes('wirtschaft') || aTitle.includes('经济与社会'))) return c;
    if ((qTitle === '社会分工论' || qTitle === 'the division of labour in society') && (c.concept_id === 'VS-SOC-002' || aTitle.includes('division du travail') || aTitle.includes('社会分工论'))) return c;
    if ((qTitle === '就业、利息和货币通论' || qTitle === 'the general theory of employment, interest and money') && (c.concept_id === 'VS-ECON-002' || aTitle.includes('general theory') || aTitle.includes('通论'))) return c;
    if ((qTitle === '君主论' || qTitle === 'the prince') && (c.concept_id === 'VS-POL-004' || aTitle.includes('principe') || aTitle.includes('君主论'))) return c;
  }

  // 2. 原典权威书目精确/包含比对（严禁拿概念名模糊匹配，严禁短词误伤）
  for (const c of sandboxConcepts) {
    const anchor = c.canon_anchor || {};
    const aTitle = (anchor.title || '').toLowerCase();
    if (!aTitle) continue;

    // 完全一致
    if (aTitle === qTitle) return c;

    // 中文长书名包含（至少 4 个汉字，避免通用短词误触）
    if (/[\u4e00-\u9fa5]/.test(qTitle) && qTitle.length >= 4) {
      if (aTitle.includes(qTitle) || (aTitle.length >= 4 && qTitle.includes(aTitle))) {
        return c;
      }
    }

    // 英文完整书名全词匹配
    if (!/[\u4e00-\u9fa5]/.test(qTitle) && qTitle.length >= 5) {
      const qWords = qTitle.split(/\s+/).filter(w => w.length > 2);
      if (qWords.length >= 2 && aTitle.includes(qTitle)) {
        return c;
      }
    }
  }
  return null;
}

function auditOfflineCitations(text) {
  const cites = extractCitationsFromText(text || '');
  const citations = [];
  let exactCount = 0;
  let supportsCount = 0;
  let qualifiesCount = 0;
  let contradictsCount = 0;
  let suspectCount = 0;
  let unindexedCount = 0;

  for (const item of cites) {
    const matchedConcept = matchSandboxConceptByTitle(item.title);

    if (matchedConcept) {
      const anchor = matchedConcept.canon_anchor || {};
      const trueAuthor = ((anchor.author || '') + ' ' + (matchedConcept.primary_thinker || '')).toLowerCase();

      // 著者对验（拦截张冠李戴）
      if (item.author) {
        const aNorm = item.author.toLowerCase();
        const parts = aNorm.split(/[·•\s]+/);
        const matchesAnyPart = parts.some(p => p.length > 1 && trueAuthor.includes(p));

        if (!matchesAnyPart) {
          suspectCount++;
          const canonAuthor = getCanonicalAuthor(matchedConcept) || anchor.author || matchedConcept.primary_thinker;
          citations.push({
            raw_citation: item.raw_citation,
            extracted_title: item.title,
            extracted_author: item.author,
            verdict: 'ATTRIBUTION_SUSPECT',
            verdict_zh: `🟡 疑似张冠李戴（著作真实，但著录著者不符）：《${anchor.title}》实际著者为『${canonAuthor}』，而非『${item.author}』！`,
            confidence_score: 0.95,
            matched_concept_id: matchedConcept.concept_id,
            canonical_title: anchor.title,
            canonical_author: canonAuthor,
            canon_sha256: anchor.canon_sha256,
            notes: '大模型生成中常见将经典安放至其他学者名下，存在重大引注合规风险。'
          });
          continue;
        }
      }

      // 著者吻合，进一步探查学派辩证张力
      const windowStart = Math.max(0, (item.index || 0) - 100);
      const windowEnd = Math.min((text || '').length, (item.index || 0) + 150);
      const contextSnippet = (text || '').slice(windowStart, windowEnd);

      const canonAuthor = getCanonicalAuthor(matchedConcept) || anchor.author || matchedConcept.primary_thinker;

      let matchedDispute = null;
      const disputes = matchedConcept.dialectical_disputes || [];
      for (const d of disputes) {
        const dKeywords = d.slice(0, 15).split(/[：:‘'“"]/)[0].split(/[\s·]/);
        if (dKeywords.some(kw => kw.length >= 2 && contextSnippet.includes(kw))) {
          matchedDispute = d;
          break;
        }
      }

      if (matchedDispute) {
        qualifiesCount++;
        citations.push({
          raw_citation: item.raw_citation,
          extracted_title: item.title,
          extracted_author: item.author,
          verdict: 'QUALIFIES',
          verdict_zh: '⚖️ 学派辩证张力（正典包含对应限定或交锋论述）',
          confidence_score: 0.92,
          matched_concept_id: matchedConcept.concept_id,
          canonical_title: anchor.title,
          canonical_author: canonAuthor,
          canon_sha256: anchor.canon_sha256,
          chapter_anchor: anchor.chapter_anchor,
          dialectical_dispute: matchedDispute,
          notes: `引述命题在思想史中存在结构性学派交锋：${matchedDispute}`
        });
      } else {
        const excerpt = anchor.verbatim_excerpt || '';
        // 严格字句级引文确证：必须带有双引号包裹且长度>=15字连续匹配，防止命题反转短片段弱匹配误判
        const quoteRegex = /["“'‘]([^"”'’]{15,})["”'’]/g;
        let isVerbatimQuote = false;
        let qm;
        if (excerpt) {
          while ((qm = quoteRegex.exec(contextSnippet)) !== null) {
            if (excerpt.includes(qm[1].trim())) {
              isVerbatimQuote = true;
              break;
            }
          }
        }

        if (isVerbatimQuote) {
          exactCount++;
        } else {
          supportsCount++;
        }

        citations.push({
          raw_citation: item.raw_citation,
          extracted_title: item.title,
          extracted_author: item.author,
          verdict: isVerbatimQuote ? 'EXACT_MATCH' : 'SUPPORTS',
          verdict_zh: isVerbatimQuote ? '🟢 权威原典字句确证（256 位 SHA-256 版本存证）' : '🟢 权威正典著录吻合（书目与著者坐标确证，命题语义待深入研读）',
          confidence_score: isVerbatimQuote ? 0.99 : 0.85,
          matched_concept_id: matchedConcept.concept_id,
          canonical_title: anchor.title,
          canonical_author: canonAuthor,
          canon_year: anchor.year,
          canon_sha256: anchor.canon_sha256,
          chapter_anchor: anchor.chapter_anchor,
          verbatim_excerpt: anchor.verbatim_excerpt,
          notes: isVerbatimQuote ? '原文切片字句高度匹配，出处坐标与 256 位 SHA-256 版本哈希完备。' : '著作与著者著录核对吻合，已定位馆藏权威版本；命题语义核实建议深入研读原典章节。'
        });
      }
    } else {
      unindexedCount++;
      citations.push({
        raw_citation: item.raw_citation,
        extracted_title: item.title,
        extracted_author: item.author,
        verdict: 'UNINDEXED',
        verdict_zh: '⚪ 离线沙盒未收录（本地沙盒未覆盖，无法直接确证，需经权威书目查证）',
        confidence_score: 0.50,
        notes: `未在内置的 50 篇离线正典沙盒中检索到《${item.title}》。该文献可能为其他学科真实著作或外部文献，离线沙盒不作虚构断言。建议连接全库 API 或外部书目数据库（如 CrossRef/OpenAlex）进行二次核验。`
      });
    }
  }

  const total = citations.length;
  if (total === 0) {
    return {
      status: 'ok',
      mode: 'offline_golden_sandbox_50',
      total_citations_extracted: 0,
      exact_matches_count: 0,
      supports_count: 0,
      qualifies_count: 0,
      contradicts_count: 0,
      suspect_count: 0,
      unindexed_count: 0,
      citation_health_score: null,
      verdict: 'NO_CITATIONS_FOUND',
      summary: '未在输入文本中抽取到有效学术文献引用格式。',
      citations: [],
      notice: '离线模式基于 50 篇经典学术正典沙盒初筛。如需对勘 24 学科全量学术正典与章节定位，请配置 VERISCOPE_API_KEY。'
    };
  }

  const groundedTotal = exactCount + supportsCount + qualifiesCount;
  const healthScore = Math.round(((groundedTotal * 100) + (suspectCount * 30)) / total);

  return {
    status: 'ok',
    mode: 'offline_golden_sandbox_50',
    total_citations_extracted: total,
    exact_matches_count: exactCount,
    supports_count: supportsCount,
    qualifies_count: qualifiesCount,
    contradicts_count: contradictsCount,
    suspect_count: suspectCount,
    unindexed_count: unindexedCount,
    citation_health_score: healthScore,
    summary: `共抽检 ${total} 处学术引注：${groundedTotal} 处经正典证实/具备坐标，${suspectCount} 处疑似张冠李戴，${unindexedCount} 处沙盒未收录。`,
    citations: citations,
    notice: '离线模式基于 50 篇经典学术正典沙盒初筛。如需对勘 24 学科全量学术正典与章节定位，请配置 VERISCOPE_API_KEY。'
  };
}

function forwardToGateway(toolName, args) {
  return new Promise((resolve) => {
    try {
      const url = new URL(DEFAULT_GATEWAY_URL);
      // 安全加固: 远端网关强制使用 HTTPS，杜绝明文传输 Bearer 令牌 (仅本地开发允许 http://localhost)
      if (url.protocol !== 'https:' && url.hostname !== 'localhost' && url.hostname !== '127.0.0.1') {
        resolve({ error: 'Insecure gateway rejected: Remote VERISCOPE_GATEWAY_URL must use https:// to protect credentials.' });
        return;
      }

      const postData = JSON.stringify({ tool: toolName, arguments: args });
      const options = {
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? 443 : 80),
        path: url.pathname + url.search,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData),
          'Authorization': `Bearer ${API_KEY}`,
          'User-Agent': 'VeriScope-MCP-Node/1.1.7'
        },
        timeout: 10000
      };
      const client = url.protocol === 'https:' ? https : http;
      const req = client.request(options, (res) => {
        let body = '';
        res.on('data', (chunk) => { body += chunk; });
        res.on('end', () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            resolve({ error: `Invalid JSON from gateway: ${body.slice(0, 200)}` });
          }
        });
      });
      req.on('error', (e) => {
        resolve({ error: `Gateway connection failed: ${e.message}` });
      });
      req.on('timeout', () => {
        req.destroy();
        resolve({ error: 'Gateway request timed out' });
      });
      req.write(postData);
      req.end();
    } catch (err) {
      resolve({ error: `Gateway request setup error: ${err.message}` });
    }
  });
}

async function callTool(name, args) {
  if (API_KEY) {
    if (name === 'veriscope_discover_concepts') {
      const localMatches = discoverLocal(args.query, args.discipline_hint || args.discipline);
      if (localMatches.length > 0) {
        return {
          total_matched: localMatches.length,
          concepts: localMatches,
          matches: localMatches,
          source: 'offline_golden_sandbox_50'
        };
      }
      return await forwardToGateway(name, args);
    }
    if (name === 'veriscope_inspect_topography') {
      const cid = (args.concept_id || '').trim();
      const c = sandboxMap.get(cid) || nameMap.get(cid.toLowerCase());
      if (c) return inspectConcept(c, args.include_disputes !== false);
      return await forwardToGateway(name, args);
    }
    if (name === 'veriscope_locate_evidence') {
      const cid = (args.concept_id || '').trim();
      const c = sandboxMap.get(cid) || nameMap.get(cid.toLowerCase());
      if (c) return locateConcept(c);
      return await forwardToGateway(name, args);
    }
    if (name === 'veriscope_probe_radar' || name === 'veriscope_citation_audit') {
      return await forwardToGateway(name, args);
    }
  }

  // Pure Offline Sandbox Mode
  switch (name) {
    case 'veriscope_discover_concepts':
    case 'veriscope_business_frame':
    case 'veriscope_elevate_concept': {
      const qVal = args.query || args.draft_text || '';
      const matches = discoverLocal(qVal, args.discipline_hint || args.discipline);
      return {
        query: qVal,
        total_matched: matches.length,
        matched_count: matches.length,
        concepts: matches,
        matches: matches,
        sandbox_status: '50 Golden Sandbox concepts loaded (Offline Mode Ready)'
      };
    }
    case 'veriscope_inspect_topography':
    case 'veriscope_redteam_audit':
    case 'veriscope_dialectic_collide': {
      const cid = (args.concept_id || args.query || '').trim();
      const c = sandboxMap.get(cid) || nameMap.get(cid.toLowerCase());
      if (c) return inspectConcept(c, args.include_disputes !== false);
      return {
        error: 'CONCEPT_NOT_FOUND',
        message: `Concept '${args.concept_id}' not found in Golden Sandbox. Configure VERISCOPE_API_KEY for the full 24-discipline conceptual matrix.`,
        available_sandbox_concepts: Array.from(sandboxMap.keys()).slice(0, 10)
      };
    }
    case 'veriscope_locate_evidence':
    case 'veriscope_deslop_and_ground': {
      const cid = (args.concept_id || args.query || '').trim();
      const c = sandboxMap.get(cid) || nameMap.get(cid.toLowerCase());
      if (c) return locateConcept(c);

      return {
        status: 'NOT_FOUND_IN_SANDBOX',
        concept_id: cid,
        canon_anchor: null,
        is_offline_sandbox: true,
        notice: `Concept '${cid}' not found in built-in 50-canon offline sandbox. To query all 24 disciplines, configure VERISCOPE_API_KEY.`
      };
    }
    case 'veriscope_verify_attestation': {
      const trustedPub = VERISCOPE_PUBLIC_KEY_HEX;
      const cid = (args.concept_id || '').trim();
      const querySha = (args.canon_sha256 || '').trim().toLowerCase();
      const att = args.attestation;

      // 路径 B: 提供了数字签名凭证 (Ed25519 Cryptographic Attestation)
      if (att && typeof att === 'object' && (att.signature || att.signed_message || att.payload)) {
        const callerPub = att.public_key ? String(att.public_key).replace(/^0x/, '').trim().toLowerCase() : '';
        // S-4 深度加固: 拒绝任何伪造公钥、异常长度或与信任锚不符的公钥
        if (callerPub && callerPub !== trustedPub.toLowerCase()) {
          return {
            method: 'ed25519_signature',
            verification_level: 'UNTRUSTED_ISSUER',
            is_cryptographically_verified: false,
            verification_status: 'ISSUER_UNTRUSTED',
            algorithm: 'Ed25519',
            public_key: callerPub,
            error: 'Untrusted public key: Caller-supplied key does not match VeriScope Sovereign Trust Anchor.'
          };
        }

        const pub = trustedPub; // 永远强制使用官方根信任锚
        const sig = att.signature || '';
        const msg = att.signed_message || att.payload || '';

        const isSignatureValid = verifyEd25519Signature(pub, sig, msg);
        if (!isSignatureValid) {
          return {
            method: 'ed25519_signature',
            verification_level: 'SIGNATURE_FAILED',
            is_cryptographically_verified: false,
            verification_status: 'SIGNATURE_INVALID',
            algorithm: 'Ed25519',
            public_key: pub,
            error: 'Mathematical signature verification failed.'
          };
        }

        // N-3 闭环: 解构 signed_message 载荷并与用户查询参数严格比对
        // 协议规范:
        // v2 格式: VERISCOPE_ATTESTATION:v2:<key_id>:<concept_id>:<canon_sha256>:<doc_sha256>:<slice16>:<timestamp>
        // v1 格式: VERISCOPE_ATTESTATION:<concept_id>:<canon_sha256>:<nonce_or_slice>:<timestamp>
        let parsedPayload = null;
        if (typeof msg === 'string' && msg.startsWith('VERISCOPE_ATTESTATION:')) {
          const parts = msg.split(':');
          if (parts.length >= 8 && parts[1] === 'v2') {
            parsedPayload = {
              protocol: parts[0],
              version: parts[1],
              key_id: parts[2],
              concept_id: parts[3] || '',
              canon_sha256: (parts[4] || '').toLowerCase(),
              doc_sha256: (parts[5] || '').toLowerCase(),
              slice_or_nonce: parts[6] || '',
              timestamp: parts[7] || ''
            };
          } else if (parts.length >= 5) {
            parsedPayload = {
              protocol: parts[0],
              version: 'v1',
              concept_id: parts[1] || '',
              canon_sha256: (parts[2] || '').toLowerCase(),
              slice_or_nonce: parts[3] || '',
              timestamp: parts[4] || ''
            };
          }
        }

        // 防伪造绕过检查 (Anti-Bypass Guard):
        // 若调用方传入了 concept_id 或 canon_sha256，签名载荷必须是合规的 VERISCOPE_ATTESTATION 凭证
        if (cid || querySha) {
          if (!parsedPayload) {
            return {
              method: 'ed25519_signature',
              verification_level: 'MALFORMED_ATTESTATION',
              is_cryptographically_verified: false,
              verification_status: 'MALFORMED_ATTESTATION',
              error: 'Signed message does not follow canonical VERISCOPE_ATTESTATION protocol format, cannot bind to requested concept_id/canon_sha256.'
            };
          }
          if (cid && cid.toUpperCase() !== parsedPayload.concept_id.toUpperCase()) {
            return {
              method: 'ed25519_signature',
              verification_level: 'PAYLOAD_MISMATCH',
              is_cryptographically_verified: false,
              verification_status: 'PAYLOAD_MISMATCH',
              error: `Signed concept_id '${parsedPayload.concept_id}' does not match query concept_id '${cid}'.`,
              signed_payload: parsedPayload
            };
          }
          if (querySha && querySha.toLowerCase() !== parsedPayload.canon_sha256.toLowerCase()) {
            return {
              method: 'ed25519_signature',
              verification_level: 'PAYLOAD_MISMATCH',
              is_cryptographically_verified: false,
              verification_status: 'PAYLOAD_MISMATCH',
              error: `Signed canon_sha256 '${parsedPayload.canon_sha256}' does not match query canon_sha256 '${querySha}'.`,
              signed_payload: parsedPayload
            };
          }
        }

        return {
          method: 'ed25519_signature',
          verification_level: parsedPayload ? 'SIGNATURE_VERIFIED' : 'ARBITRARY_MESSAGE_SIGNED',
          is_cryptographically_verified: true,
          verification_status: parsedPayload ? 'SIGNATURE_VALID' : 'ARBITRARY_PAYLOAD_VALID',
          algorithm: 'Ed25519',
          public_key: pub,
          signed_payload: parsedPayload || { raw_message: msg, note: 'Valid cryptographic signature on non-attestation message payload.' }
        };
      }

      // 路径 A: 仅提供了概念 ID 与版本散列 (Local Hash Matching)
      if (cid && querySha) {
        const c = sandboxMap.get(cid) || nameMap.get(cid.toLowerCase());
        if (c) {
          const realSha = ((c.canon_anchor && c.canon_anchor.canon_sha256) || '').toLowerCase();
          const isMatched = (querySha === realSha);
          return {
            method: 'local_hash_lookup',
            verification_level: isMatched ? 'HASH_ONLY' : 'TAMPER_DETECTED',
            is_hash_match: isMatched,
            hash_matched: isMatched,
            is_cryptographically_verified: false, // 诚实声明：无数字签名，仅纯哈希比对
            verification_status: isMatched ? 'HASH_MATCHED' : 'TAMPER_DETECTED',
            concept_id: cid,
            matched_edition: c.canon_anchor && c.canon_anchor.title,
            algorithm: 'SHA-256'
          };
        }
        return {
          method: 'local_hash_lookup',
          verification_level: 'CONCEPT_NOT_FOUND',
          is_hash_match: false,
          hash_matched: false,
          is_cryptographically_verified: false,
          verification_status: 'CONCEPT_NOT_FOUND',
          concept_id: cid,
          error: `Concept '${cid}' not found in Golden Sandbox.`
        };
      }

      return {
        error: 'INVALID_ARGUMENTS',
        message: 'Must provide either (concept_id + canon_sha256) for local hash matching or (attestation) for Ed25519 cryptographic signature verification.'
      };
    }
    case 'veriscope_citation_audit': {
      const txt = args.text || args.document_text || args.draft_text || '';
      return auditOfflineCitations(txt);
    }
    case 'veriscope_probe_radar': {
      const stats = {};
      for (const c of sandboxConcepts) {
        const d = c.discipline_code || c.discipline || 'OTHER';
        stats[d] = (stats[d] || 0) + 1;
      }
      return {
        status: 'healthy',
        mode: 'offline_golden_sandbox_50',
        active_disciplines: Object.keys(stats).length,
        sandbox_concept_count: sandboxConcepts.length,
        disciplines_distribution: stats,
        babel_synapses: [
          { source: 'VS-PHIL-001', target: 'VS-PHIL-005', relation: 'epistemological_critique' },
          { source: 'VS-SOC-001', target: 'VS-SOC-003', relation: 'institutional_dialectic' },
          { source: 'VS-COMM-001', target: 'VS-COMM-004', relation: 'public_sphere_transition' },
          { source: 'VS-LAW-001', target: 'VS-LAW-002', relation: 'constitutional_polarity' },
          { source: 'VS-ECON-001', target: 'VS-ECON-004', relation: 'market_order_evolution' }
        ],
        notice: 'Serving from built-in 50-Canon Golden Sandbox. Full 77,984 matrix accessible via VERISCOPE_API_KEY.'
      };
    }
    default:
      return { error: `Unknown tool: ${name}` };
  }
}

function inspectConcept(c, includeDisputes) {
  const res = {
    concept_id: c.concept_id,
    name_zh: c.name_zh,
    name_en: c.name_en,
    discipline: c.discipline,
    primary_thinker: c.primary_thinker,
    historical_period: c.historical_period,
    formal_kernel: c.formal_kernel,
    authoritative_edition: c.canon_anchor ? c.canon_anchor.title : undefined,
    canon_sha256: c.canon_anchor ? c.canon_anchor.canon_sha256 : undefined,
    is_sandbox_concept: true
  };
  if (includeDisputes) {
    res.dialectical_disputes = c.dialectical_disputes || [];
  }
  return res;
}

function locateConcept(c) {
  const anchor = c.canon_anchor || {};
  return {
    status: 'ATTESTED_FULL',
    concept_id: c.concept_id,
    name_zh: c.name_zh,
    discipline: c.discipline,
    primary_thinker: c.primary_thinker,
    canon_anchor: {
      archival_id: anchor.archival_id || 0,
      title: anchor.title || '',
      author: anchor.author || '',
      year: anchor.year || '',
      chapter_anchor: anchor.chapter_anchor || '',
      canon_sha256: anchor.canon_sha256 || '',
      verbatim_excerpt: anchor.verbatim_excerpt || '',
      provenance: 'VeriScope 权威学术原典库 · 规范版本存证'
    },
    cryptographic_receipt: c.cryptographic_receipt || null,
    access_mode: 'GOLDEN_SANDBOX_OFFLINE_VERIFIED'
  };
}

function discoverLocal(query, discipline) {
  if (!query) return [];
  const q = query.toLowerCase().trim();
  const disc = (discipline || '').toLowerCase().trim();
  const effectiveQueries = [q];
  for (const [triggers, canonical] of BUSINESS_SYNONYM_BRIDGE) {
    if (triggers.some(t => q.includes(t.toLowerCase()))) {
      effectiveQueries.push(canonical.toLowerCase());
    }
  }
  const results = [];
  const seenIds = new Set();

  for (const eq of effectiveQueries) {
    for (const c of sandboxConcepts) {
      if (seenIds.has(c.concept_id)) continue;
      if (disc && !c.discipline.toLowerCase().includes(disc) && c.discipline_code.toLowerCase() !== disc) {
        continue;
      }
      const anchor = c.canon_anchor || {};
      const textPool = [
        c.concept_id || '',
        c.name_zh || '',
        c.name_en || '',
        c.primary_thinker || '',
        c.historical_period || '',
        c.core_thesis || '',
        c.formal_kernel || '',
        anchor.author || '',
        anchor.title || ''
      ].join(' ').toLowerCase();

      if (textPool.includes(eq) || eq.split(/\s+/).some(w => w.length > 1 && textPool.includes(w))) {
        seenIds.add(c.concept_id);
        results.push({
          concept_id: c.concept_id,
          name_zh: c.name_zh,
          name_en: c.name_en,
          discipline: c.discipline,
          primary_thinker: c.primary_thinker,
          historical_period: c.historical_period,
          core_thesis: c.core_thesis,
          formal_definition: c.formal_kernel ? c.formal_kernel.slice(0, 160) + '...' : '',
          is_sandbox_ready: true
        });
        if (results.length >= 10) break;
      }
    }
    if (results.length >= 10) break;
  }
  return results;
}

function startServer() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  if (process.argv.includes('--list-tools')) {
    console.log(JSON.stringify(TOOLS, null, 2));
    process.exit(0);
  }

  rl.on('line', async (line) => {
    line = line.trim();
    if (!line) return;
    let req;
    try {
      req = JSON.parse(line);
    } catch (err) {
      process.stdout.write(JSON.stringify({
        jsonrpc: '2.0',
        id: null,
        error: { code: -32700, message: `Parse error: ${err.message}` }
      }) + '\n');
      return;
    }

    const { id, method, params } = req;
    if (method === 'initialize') {
      const res = {
        jsonrpc: '2.0',
        id: id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: {
            name: 'veriscope',
            version: '1.1.6'
          }
        }
      };
      process.stdout.write(JSON.stringify(res) + '\n');
    } else if (method === 'notifications/initialized') {
      // No-op
    } else if (method === 'ping') {
      process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: id, result: {} }) + '\n');
    } else if (method === 'tools/list') {
      process.stdout.write(JSON.stringify({
        jsonrpc: '2.0',
        id: id,
        result: { tools: TOOLS }
      }) + '\n');
    } else if (method === 'tools/call') {
      const toolName = params ? params.name : '';
      const toolArgs = (params && params.arguments) || {};
      const resultData = await callTool(toolName, toolArgs);
      process.stdout.write(JSON.stringify({
        jsonrpc: '2.0',
        id: id,
        result: {
          content: [
            {
              type: 'text',
              text: JSON.stringify(resultData, null, 2)
            }
          ]
        }
      }) + '\n');
    } else {
      process.stdout.write(JSON.stringify({
        jsonrpc: '2.0',
        id: id,
        error: { code: -32601, message: `Method not found: ${method}` }
      }) + '\n');
    }
  });
}

if (require.main === module) {
  startServer();
}

module.exports = {
  verifyEd25519Signature,
  cleanAuthorName,
  cleanBookTitle,
  extractCitationsFromText,
  matchSandboxConceptByTitle,
  auditOfflineCitations,
  callTool,
  TOOLS,
  VERISCOPE_PUBLIC_KEY_HEX
};
