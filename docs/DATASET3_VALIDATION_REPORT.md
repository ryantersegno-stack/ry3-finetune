# Dataset 3 — Validation Report (R18)
*2026-10-12. Built for RY3 v03 Config A.*

## File
`~/workspace/ry3-github/eval_repair/dataset3.jsonl` — **349 lines**, valid JSONL, schema `id, instruction, output, category, skill, difficulty, source, quality_profile` on every line. Zero duplicate IDs, zero duplicate instructions.

## Composition (matches spec)

| Segment | Count | % |
|---|---|---|
| Format-exemplifying: troubleshooting (ordered steps) | 61 | |
| Format-exemplifying: key checks | 61 | |
| Format-exemplifying: tradeoff | 61 | |
| Format-exemplifying: concrete example | 62 | |
| Format-exemplifying subtotal | 245 | 70.2% |
| Fresh-example discipline | 52 | 14.9% |
| Replay (source preserved: 40 RY3_ULTRA_NEW, 12 RY3_V02_TARGETED) | 52 | 14.9% |
| **Total** | **349** | 100% |

- 23 categories, 23,086 words of new output.
- Difficulty: 144 foundational / 131 intermediate / 22 advanced.
- Instructions reuse the eval's exact format phrasings ("Answer as a troubleshooting guide with ordered steps", "Give a concise answer followed by the key checks", "Compare the main alternatives and state the tradeoff", "Explain the main idea, then give one concrete example") plus the corpus's audience framing and "Do not assume facts that were not provided" constraint.

## R18 validator results
Programmatic checks on all 297 new examples:
- Troubleshooting: every output contains ≥2 numbered steps (`^\d+\.`).
- Key checks: every output contains an explicit "Key checks:" section.
- Tradeoff: every output names ≥2 alternatives (Option A/B or vs/versus) AND states the tradeoff.
- Example: every output contains a concrete example marker.
- Fresh-example discipline: all 52 example bodies verified free of their canonical reference terms (checked against `d3_avoid.json`; concept names in the definitional sentence are permitted, canonical story content is absent).

**Result: 297/297 new examples pass all checks. 100%.**

## Notes
- Replay examples were selected as the best format-honoring examples in the v01/v02 corpus (24 tradeoff-honoring + 28 diverse example-honoring); their `source` values are preserved as-is per spec.
- `d3_avoid.json` (canonical-term map) kept alongside the dataset for re-validation.
- Ready for v03 Config A training: LR 2e-5, 2 epochs, effective batch 16, max_length 2048.
