// test/test_citation_audit.js
// 针对发布版 bin/index.js 的真实模块执行单元测试，严禁自造替身逻辑
const assert = require('assert');
const {
  auditOfflineCitations,
  extractCitationsFromText,
  cleanAuthorName,
  cleanBookTitle,
  matchSandboxConceptByTitle
} = require('../bin/index.js');

console.log('Testing Citation Audit Engine against published bin/index.js module...');

// Test 0: cleanAuthorName preserves internal whitespace (T-1 regression test)
const cleanedRawls = cleanAuthorName('John Rawls');
assert.strictEqual(cleanedRawls, 'John Rawls', `cleanAuthorName must preserve internal spaces, got: ${cleanedRawls}`);
console.log('  [✓] Test 0: cleanAuthorName space-preservation regression test PASS');

// Test 1: Author in book exact match
const t1 = auditOfflineCitations('正如亚当·斯密在《国富论》中指出，每个人都在追求自身的利益...');
assert.strictEqual(t1.total_citations_extracted, 1);
assert.strictEqual(t1.citations[0].verdict, 'SUPPORTS');
assert.strictEqual(t1.citations[0].canonical_author, 'Adam Smith');
console.log('  [✓] Test 1: Author in book exact match PASS');

// Test 2: Attribution suspect mismatch attack (Keynes wrote Wealth of Nations)
const t2 = auditOfflineCitations('正如著名经济学家凯恩斯在《国富论》中所强调...');
assert.strictEqual(t2.total_citations_extracted, 1);
assert.strictEqual(t2.citations[0].verdict, 'ATTRIBUTION_SUSPECT');
assert.strictEqual(t2.suspect_count, 1);
console.log('  [✓] Test 2: Attribution mismatch attack correctly flagged PASS');

// Test 3: Bare book title
const t3 = auditOfflineCitations('在《纯粹理性批判》中，先验感性论探讨了时空形式...');
assert.strictEqual(t3.total_citations_extracted, 1);
assert.strictEqual(t3.citations[0].matched_concept_id, 'VS-PHIL-001');
console.log('  [✓] Test 3: Bare book title match PASS');

// Test 4: Dispute / Qualification detection
const t4 = auditOfflineCitations('在《纯粹理性批判》中探讨物自体，然而黑格尔绝对唯心主义批判物自体为抽象贫乏之物...');
assert.strictEqual(t4.total_citations_extracted, 1);
assert.strictEqual(t4.citations[0].verdict, 'QUALIFIES');
console.log('  [✓] Test 4: Dialectical qualification detection PASS');

// Test 5: Unindexed citation honest labeling (费孝通《乡土中国》, A-1 regression test)
const t5 = auditOfflineCitations('根据费孝通在《乡土中国》中的差序格局理论...');
assert.strictEqual(t5.total_citations_extracted, 1);
assert.strictEqual(t5.citations[0].verdict, 'UNINDEXED');
assert.strictEqual(t5.unindexed_count, 1);
assert.ok(!t5.citations[0].verdict_zh.includes('AI 幻觉'), 'Must not falsely accuse real scholars of AI hallucination');
console.log('  [✓] Test 5: Unindexed real literature honest labeling (UNINDEXED) PASS');

// Test 6: English citation with John Rawls (T-1 & A-3 regression test)
const t6 = auditOfflineCitations('As argued in "A Theory of Justice" by John Rawls, the original position...');
assert.strictEqual(t6.total_citations_extracted, 1);
assert.strictEqual(t6.citations[0].extracted_author, 'John Rawls');
assert.strictEqual(t6.citations[0].canonical_author, 'John Rawls');
assert.strictEqual(t6.citations[0].verdict, 'SUPPORTS');
console.log('  [✓] Test 6: English citation with John Rawls properly verified (SUPPORTS) PASS');

// Test 7: English standard citation (Kant, Critique of Pure Reason (1781))
const t7 = auditOfflineCitations('See Kant, Critique of Pure Reason (1781) for transcendental aesthetics...');
assert.strictEqual(t7.total_citations_extracted, 1);
assert.strictEqual(t7.citations[0].canonical_title, 'Kritik der reinen Vernunft (纯粹理性批判)');
console.log('  [✓] Test 7: English standard citation format PASS');

// Test 8: Western citation prefix stripping (as noted by / according to)
const cleanedKant = cleanAuthorName('As noted by Kant');
assert.strictEqual(cleanedKant, 'Kant', `cleanAuthorName must strip prefix 'As noted by', got: ${cleanedKant}`);
const t8 = auditOfflineCitations('As noted by Kant in "Critique of Pure Reason", space and time are pure forms of intuition...');
assert.strictEqual(t8.total_citations_extracted, 1);
assert.strictEqual(t8.citations[0].extracted_author, 'Kant');
assert.strictEqual(t8.citations[0].verdict, 'SUPPORTS');
console.log('  [✓] Test 8: Western prefix stripping & attribution PASS');

// Test 9: Chinese pronoun reference (他在《...》does not trigger false ATTRIBUTION_SUSPECT)
const t9 = auditOfflineCitations('他在《纯粹理性批判》中探讨了先验感性论与范畴演绎...');
assert.strictEqual(t9.total_citations_extracted, 1);
assert.strictEqual(t9.citations[0].verdict, 'SUPPORTS');
assert.strictEqual(t9.suspect_count, 0, 'Pronoun "他在" must not trigger false ATTRIBUTION_SUSPECT');
console.log('  [✓] Test 9: Chinese pronoun reference handled honestly (SUPPORTS) PASS');

// Test 10: Reverse proposition & Verbatim quote discrimination
const t10_general = auditOfflineCitations('在《纯粹理性批判》中，有人声称物自体不可知并主张怀疑论...');
assert.strictEqual(t10_general.citations[0].verdict, 'SUPPORTS', 'Unquoted proposition must be SUPPORTS (0.85), not EXACT_MATCH (0.99)');
assert.strictEqual(t10_general.citations[0].confidence_score, 0.85);

const c_phil = matchSandboxConceptByTitle('纯粹理性批判');
const excerpt = c_phil.canon_anchor.verbatim_excerpt;
assert.ok(excerpt && excerpt.length >= 15, 'Verbatim excerpt must exist in sandbox');
const verbatimSlice = excerpt.slice(0, 20);
const t10_verbatim = auditOfflineCitations(`在《纯粹理性批判》中，康德写道：“${verbatimSlice}”`);
assert.strictEqual(t10_verbatim.citations[0].verdict, 'EXACT_MATCH', 'Quoted verbatim string >= 15 chars must yield EXACT_MATCH');
assert.strictEqual(t10_verbatim.citations[0].confidence_score, 0.99);
console.log('  [✓] Test 10: Reverse proposition guard & exact quote discrimination PASS');

// Test 11: Fail-open fix (0 citations returns null score and NO_CITATIONS_FOUND)
const t11 = auditOfflineCitations('今天讨论一下现代哲学与科技伦理的发展趋势，这里没有任何书目引用。');
assert.strictEqual(t11.total_citations_extracted, 0);
assert.strictEqual(t11.verdict, 'NO_CITATIONS_FOUND');
assert.strictEqual(t11.citation_health_score, null, 'Score must be null when 0 citations are found');
console.log('  [✓] Test 11: Zero citations fail-open fix (verdict=NO_CITATIONS_FOUND, score=null) PASS');

console.log('All Citation Audit unit tests passed 100% against published module!');
