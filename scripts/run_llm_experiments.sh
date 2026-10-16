#!/bin/bash
# Run the pipeline on blocks in parallel against the vLLM server in logs/vllm_endpoint.env.
# Usage: scripts/run_llm_experiments.sh [llm|compiler] [blocks...]
#        RESUME_A=<run-name> ... resumes that block's run directory instead of starting a new one.
MODE=${1:-llm}; shift
BLOCKS=${@:-A B C}
cd "$(dirname "$0")/.."
mkdir -p logs/runs
for b in $BLOCKS; do
  var=RESUME_$b; extra=""; [ -n "${!var}" ] && extra="--resume-run ${!var}"
  CODEGEN_MODE=$MODE nohup .venv/bin/python experiment.py \
      -d data/fischertechnik_lab_$b/block-$b.csv -n 1 \
      --context-file data/fischertechnik_lab_$b/user_context.md $extra \
      > logs/runs/${MODE}_${b}_$(date +%H%M%S).log 2>&1 &
  echo "block $b ($MODE): pid $! $extra"
done
