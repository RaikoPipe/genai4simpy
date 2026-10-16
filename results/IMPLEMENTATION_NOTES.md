# Proposal implementation — test results (Qwen3.8-27B AWQ-INT4, vLLM + MTP, 1×A40)

Scores: evaluate_v2, M=300, bias vs ground truth of the same block (in-sample).
Full table: `results/compare_runs_all.txt`; deterministic references incl. cross-block: `results/deterministic/`.

| Block | Arm | Completed | Flow time | Time in system | Overlap/case |
|---|---|---|---|---|---|
| A | paper model | +500% | +84% | +83% | 0 |
| A | new, round 1 (LLM code) | +479% | +51% | +32% | 0.92 |
| A | new, round 2 (compiler) | +407% | +106% | +78% | 0.88 |
| A | deterministic discovery (no LLM) | −2% | +10% | −18% | 0 |
| B | paper model | −8% | +37% | +29% | 0 |
| B | new, LLM code | +10% | +10% | +9% | 0.93 |
| B | new, same spec compiled | +8% | +6% | +5% | 1.78 |
| B | deterministic discovery | +1% | +1% | −3% | 1.24 |
| C | paper model | −22% | +31% | +27% | 0 |
| C | new, round 1 (LLM code) | −8% | +36% | +28% | 0.88 |
| C | new, round 1 spec compiled | +0.4% | −7% | −17% | 2.44 |
| C | new, round 2 (compiler, stopped mid-revision) | +83% | +33% | +43% | 1.42 |
| C | deterministic discovery | −4% | −0.3% | −15% | 1.52 |

GT overlap per completed case: A 1.67, B 1.57, C 1.46.

Findings
1. Control-logic discovery (priority at hbw, intra-case concurrency, early exits, burst arrivals) removes the
   flow-time bias when applied as the evidence says (deterministic arm: |bias| ≤ 10 % in-sample on all blocks).
2. LLM-written code loses spec fidelity (C: +36 % LLM code vs −7 % compiled, same spec) → compiler is now default.
3. Remaining LLM error is spec decisions following the context files over the tool evidence
   ("absence = truncation" in A/C context → early exits removed; A two-phase arrivals → +41 % implied releases).
   `check_spec_against_evidence` flags these; the agents keep them because the context is declared authoritative.
4. LLM evaluator leniency: round-1 C evaluator relaxed a metamorphic oracle to declare PASS → verdicts are now deterministic.
