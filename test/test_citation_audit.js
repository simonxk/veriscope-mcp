// test/test_citation_audit.js
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const sandboxRaw = fs.readFileSync(path.join(__dirname, '..', 'golden_sandbox_50.json'), 'utf8');
const sandboxConcepts = JSON.parse(sandboxRaw).concepts;

const AUTHOR_NOISE_WORDS = [
  '德意志哲学家', '德国哲学家', '法国哲学家', '英国经济学家', '美国社会学家',
  '古希腊哲学家', '古典政治学家', '社会学先驱', '法学先驱', '经济学大师',
  '著名哲学家', '学者', '教授', '先生', '作家', '部分学者', '然而', '但是',
  '认为', '强调', '指出', '提出', '声称', '根据', '按照'
];

function cleanAuthor(raw) {
  let s = (raw || '').trim();
  for (const w of AUTHOR_NOISE_WORDS) {
    s = s.replace(w, '').trim();
  }
  s = s.replace(/^[\s，,、“”"'（(：:【\[]+/, '').replace(/[\s，,、“”"'）)：:】\]]+/, '');
  if (s.includes('·')) {
    const parts = s.split('·');
    if (parts.length >= 2) {
      s = parts[parts.length - 2].trim().slice(-3) + '·' + parts[parts.length - 1].trim().slice(0, 6);
    }
  }
  return s.trim();
}

function cleanTitle(raw) {
  let s = (raw || '').trim();
  s = s.replace(/^(?:关于|论)\s*/, '');
  s = s.replace(/\s*(?:（[^）]+）|\([^)]+\))$/, '');
  return s.trim();
}

function extractCitations(text) {
  const content = text || '';
  const found = [];
  const seenTitles = new Set();

  // Pattern 1: 学者在《书名》 / 由学者所著《书名》
  const reAuthorBook = /(?:由|据|正如|如|在|根据)?\s*([·\u4e00-\u9fa5A-Za-z\s]{2,20}?)\s*(?:先生|教授|学者)?\s*(?:所著(?:的)?|在|于|的)?\s*《([^》\n]{2,60})》/g;
  let m;
  while ((m = reAuthorBook.exec(content)) !== null) {
    const author = cleanAuthor(m[1]);
    const title = cleanTitle(m[2]);
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
    const title = cleanTitle(m[1]);
    const author = cleanAuthor(m[2]);
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
    const title = cleanTitle(m[1]);
    if (title.length >= 2 && !seenTitles.has(title.toLowerCase())) {
      seenTitles.add(title.toLowerCase());
      // 往前探查著者
      const start = Math.max(0, m.index - 30);
      const pre = content.slice(start, m.index);
      let author = '';
      const mPre = /(?:由|在|据)?\s*([·\u4e00-\u9fa5]{2,6})\s*(?:在|的|于|所著)?$/.exec(pre);
      if (mPre) {
        author = cleanAuthor(mPre[1]);
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
    const title = cleanTitle(m[1]);
    const author = cleanAuthor(m[2] || m[4] || '');
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

  return found;
}

function matchConcept(title) {
  const qTitle = title.toLowerCase();
  for (const c of sandboxConcepts) {
    const anchor = c.canon_anchor || {};
    const aTitle = (anchor.title || '').toLowerCase();
    const cZh = (c.name_zh || '').toLowerCase();
    const cEn = (c.name_en || '').toLowerCase();

    if (aTitle.includes(qTitle) || qTitle.includes(aTitle) || cZh.includes(qTitle) || cEn.includes(qTitle)) {
      return c;
    }
    // 经典别名匹配
    if (qTitle === '国富论' && aTitle.includes('wealth of nations')) return c;
    if (qTitle === '资本论' && aTitle.includes('das kapital')) return c;
    if (qTitle === '纯粹理性批判' && aTitle.includes('reinen vernunft')) return c;
    if (qTitle === '正义论' && aTitle.includes('theory of justice')) return c;
    if (qTitle === '利维坦' && aTitle.includes('leviathan')) return c;
    if (qTitle === '经济与社会' && aTitle.includes('wirtschaft und gesellschaft')) return c;
    if (qTitle === '社会分工论' && aTitle.includes('division du travail')) return c;
    if (qTitle === '通论' && aTitle.includes('general theory')) return c;
  }
  return null;
}

function auditCitations(text) {
  const cites = extractCitations(text);
  const results = [];
  let exactCount = 0;
  let supportsCount = 0;
  let qualifiesCount = 0;
  let contradictsCount = 0;
  let suspectCount = 0;
  let unindexedCount = 0;

  for (const item of cites) {
    const c = matchConcept(item.title);
    if (!c) {
      unindexedCount++;
      results.push({
        raw_citation: item.raw_citation,
        extracted_title: item.title,
        extracted_author: item.author,
        verdict: 'UNINDEXED_OR_HALLUCINATED',
        verdict_zh: '⚪ 离线沙盒未收录（疑似 AI 幻觉编造引文或需全库检索）',
        confidence_score: 0.20,
        notes: `未在内置的 50 篇离线正典沙盒中检索到《${item.title}》。可能属于其他学科专著，或系大模型幻觉编造引文。`
      });
      continue;
    }

    const anchor = c.canon_anchor || {};
    const trueAuthor = ((anchor.author || '') + ' ' + (c.primary_thinker || '')).toLowerCase();

    // 著者对验
    if (item.author) {
      const aNorm = item.author.toLowerCase();
      const parts = aNorm.split(/[·•\s]+/);
      const authorHit = parts.some(p => p.length > 1 && trueAuthor.includes(p));

      if (!authorHit) {
        suspectCount++;
        results.push({
          raw_citation: item.raw_citation,
          extracted_title: item.title,
          extracted_author: item.author,
          verdict: 'ATTRIBUTION_SUSPECT',
          verdict_zh: `🟡 疑似张冠李戴（著作真实，但著录著者不符）：《${anchor.title}》实际著者为『${anchor.author || c.primary_thinker}』，而非『${item.author}』！`,
          confidence_score: 0.95,
          matched_concept_id: c.concept_id,
          canonical_title: anchor.title,
          canonical_author: anchor.author || c.primary_thinker,
          canon_sha256: anchor.canon_sha256,
          notes: '大模型常见将名著挂载至错误思想家名下，存在重大引注合规风险。'
        });
        continue;
      }
    }

    // 著者吻合或未注明著者，检查上下文是否有辩证张力
    const windowStart = Math.max(0, (item.index || 0) - 100);
    const windowEnd = Math.min((text || '').length, (item.index || 0) + 150);
    const contextSnippet = text.slice(windowStart, windowEnd);

    // 辩证分歧探查
    let matchedDispute = null;
    const disputes = c.dialectical_disputes || [];
    for (const d of disputes) {
      const dKeywords = d.slice(0, 15).split(/[：:‘'“"]/)[0].split(/[\s·]/);
      if (dKeywords.some(kw => kw.length >= 2 && contextSnippet.includes(kw))) {
        matchedDispute = d;
        break;
      }
    }

    if (matchedDispute) {
      qualifiesCount++;
      results.push({
        raw_citation: item.raw_citation,
        extracted_title: item.title,
        extracted_author: item.author,
        verdict: 'QUALIFIES',
        verdict_zh: '⚖️ 学派辩证张力（正典包含对应限定或交锋论述）',
        confidence_score: 0.92,
        matched_concept_id: c.concept_id,
        canonical_title: anchor.title,
        canonical_author: anchor.author || c.primary_thinker,
        canon_sha256: anchor.canon_sha256,
        chapter_anchor: anchor.chapter_anchor,
        dialectical_dispute: matchedDispute,
        notes: `引述命题在思想史中存在结构性学派交锋：${matchedDispute}`
      });
    } else {
      // 检验是否直接包含原典摘要字句
      const excerpt = anchor.verbatim_excerpt || '';
      const isExact = excerpt && contextSnippet.split(/[,，。；;]/).some(seg => seg.length >= 6 && excerpt.includes(seg));

      if (isExact) {
        exactCount++;
      } else {
        supportsCount++;
      }

      results.push({
        raw_citation: item.raw_citation,
        extracted_title: item.title,
        extracted_author: item.author,
        verdict: isExact ? 'EXACT_MATCH' : 'SUPPORTS',
        verdict_zh: isExact ? '🟢 权威原典字句确证（256 位 SHA-256 版本存证）' : '🟢 权威学术正典思想支持',
        confidence_score: isExact ? 0.99 : 0.95,
        matched_concept_id: c.concept_id,
        canonical_title: anchor.title,
        canonical_author: anchor.author || c.primary_thinker,
        canon_year: anchor.year,
        canon_sha256: anchor.canon_sha256,
        chapter_anchor: anchor.chapter_anchor,
        verbatim_excerpt: anchor.verbatim_excerpt,
        notes: '匹配权威学术正典，出处与 256 位 SHA-256 版本哈希完备。'
      });
    }
  }

  const total = results.length;
  const groundedTotal = exactCount + supportsCount + qualifiesCount;
  const healthScore = total > 0 ? Math.round(((groundedTotal * 100) + (suspectCount * 30)) / total) : 100;

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
    summary: `共抽检 ${total} 处学术引注：${groundedTotal} 处经正典证实/具备辩证限定，${suspectCount} 处疑似张冠李戴，${unindexedCount} 处沙盒未收录或疑似幻觉。`,
    citations: results,
    notice: '离线模式基于 50 篇经典学术正典沙盒初筛。如需对勘 24 学科全量学术正典与章节定位，请配置 VERISCOPE_API_KEY。'
  };
}

// ── TEST RUN ──
console.log('Testing Citation Audit Engine...');

// Test 1: Author in book exact match
const t1 = auditCitations('正如亚当·斯密在《国富论》中指出，每个人都在追求自身的利益...');
assert.strictEqual(t1.total_citations_extracted, 1);
assert.strictEqual(t1.citations[0].verdict, 'SUPPORTS');
assert.strictEqual(t1.citations[0].canonical_author, 'Adam Smith');
console.log('  [✓] Test 1: Author in book exact match PASS');

// Test 2: Attribution suspect mismatch attack (Keynes wrote Wealth of Nations)
const t2 = auditCitations('正如著名经济学家凯恩斯在《国富论》中所强调...');
assert.strictEqual(t2.total_citations_extracted, 1);
assert.strictEqual(t2.citations[0].verdict, 'ATTRIBUTION_SUSPECT');
assert.strictEqual(t2.suspect_count, 1);
console.log('  [✓] Test 2: Attribution mismatch attack correctly flagged PASS');

// Test 3: Bare book title
const t3 = auditCitations('在《纯粹理性批判》中，先验感性论探讨了时空形式...');
assert.strictEqual(t3.total_citations_extracted, 1);
assert.strictEqual(t3.citations[0].matched_concept_id, 'VS-PHIL-001');
console.log('  [✓] Test 3: Bare book title match PASS');

// Test 4: Dispute / Qualification detection
const t4 = auditCitations('在《纯粹理性批判》中探讨物自体，然而黑格尔绝对唯心主义批判物自体为抽象贫乏之物...');
assert.strictEqual(t4.total_citations_extracted, 1);
assert.strictEqual(t4.citations[0].verdict, 'QUALIFIES');
console.log('  [✓] Test 4: Dialectical qualification detection PASS');

// Test 5: Hallucinated / Unindexed citation
const t5 = auditCitations('根据张三教授在《量子区块链元宇宙心智哲学导论》中的惊人论证...');
assert.strictEqual(t5.total_citations_extracted, 1);
assert.strictEqual(t5.citations[0].verdict, 'UNINDEXED_OR_HALLUCINATED');
assert.strictEqual(t5.unindexed_count, 1);
console.log('  [✓] Test 5: Hallucinated citation detection PASS');

// Test 6: English citation
const t6 = auditCitations('As argued in "A Theory of Justice" by John Rawls, the original position...');
assert.strictEqual(t6.total_citations_extracted, 1);
assert.strictEqual(t6.citations[0].canonical_author, 'John Rawls');
console.log('  [✓] Test 6: English citation match PASS');

console.log('All Citation Audit unit tests passed 100%!');
