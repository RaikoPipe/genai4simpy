#!/bin/bash
# vLLM server for the GenAI4SimPy test environment (Qwen3.8-27B).
# Picks BF16 when the GPU has >= 70 GB, otherwise the AWQ-INT4 checkpoint.
# gpu02/gpu03 must not be used; the A30 nodes (24 GB) cannot host a 27B model.
#SBATCH -J g4s-vllm
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --ntasks-per-node 1
#SBATCH --cpus-per-task 16
#SBATCH --mem 64G
#SBATCH --gres=gpu:1
#SBATCH --exclude=gpu02,gpu03,gpu06,gpu07,gpu08,gpu09
#SBATCH --time 24:00:00
#SBATCH -o /beegfs2/scratch/rreider/genai4simpy/logs/vllm-%j.out
#SBATCH -e /beegfs2/scratch/rreider/genai4simpy/logs/vllm-%j.err

LLM_PORT=${LLM_PORT:-41437}
IMG=/beegfs2/scratch/rreider/vllm/vllm-img
SCRATCH=/beegfs2/scratch/rreider
ENDPOINT_FILE=/beegfs2/scratch/rreider/genai4simpy/logs/vllm_endpoint.env

. /beegfs1/urz/utils/slurmProlog.sh
unset GOMP_CPU_AFFINITY OMP_PROC_BIND OMP_PLACES   # prolog pins to cores 0-15, which may not be in our cpuset
if [[ -n "${MODULESHOME:-}" && -r "${MODULESHOME}/init/bash" ]]; then source "${MODULESHOME}/init/bash";
elif [[ -r /etc/profile.d/modules.sh ]]; then source /etc/profile.d/modules.sh; fi
module load charliecloud

VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
if [ "$VRAM_MB" -ge 70000 ]; then
    LLM_MODEL="Qwen/Qwen3.8-27b"; LLM_NAME="qwen3.8-27b"; MAXLEN=131072
else
    LLM_MODEL="cyankiwi/Qwen3.8-27B-AWQ-INT4"; LLM_NAME="qwen3.8-27b-int4"; MAXLEN=131072
fi
echo "GPU VRAM ${VRAM_MB} MiB -> ${LLM_MODEL}"
# Multi-token-prediction speculative decoding (Qwen3.8 ships an MTP head); SPEC=none disables it.
SPEC=${SPEC:-'{"method": "mtp", "num_speculative_tokens": 3}'}
SPEC_ARGS=(); [ "$SPEC" != "none" ] && SPEC_ARGS=(--speculative-config "$SPEC")

ch-run --bind ${SCRATCH}:/mnt \
    --set-env=LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat:/mnt/vllm/nvml \
    --set-env=HF_HOME=/mnt/vllm/hf --set-env=HF_HUB_OFFLINE=1 \
    --set-env=HOME=/mnt/vllm/chome --set-env=XDG_CACHE_HOME=/mnt/vllm/chome/.cache \
    --set-env=FLASHINFER_WORKSPACE_DIR=/mnt/vllm/chome/.cache/flashinfer \
    --set-env=FLASHINFER_DISABLE_VERSION_CHECK=1 \
    --set-env=VLLM_CACHE_ROOT=/mnt/vllm/chome/.cache/vllm \
    --set-env=TORCHINDUCTOR_CACHE_DIR=/mnt/vllm/chome/.cache/inductor \
    --set-env=TRITON_CACHE_DIR=/mnt/vllm/chome/.cache/triton \
    --set-env=OMP_NUM_THREADS=8 \
    --unset-env=GOMP_CPU_AFFINITY --unset-env=OMP_PROC_BIND --unset-env=OMP_PLACES \
    "$IMG" -- vllm serve "$LLM_MODEL" \
    --served-model-name "$LLM_NAME" \
    --host 0.0.0.0 --port ${LLM_PORT} \
    --gpu-memory-utilization 0.92 \
    --max-model-len ${MAXLEN} \
    --max-num-seqs 16 \
    --language-model-only \
    --reasoning-parser qwen3 \
    --tool-call-parser qwen3_coder \
    --enable-auto-tool-choice \
    --enable-prefix-caching \
    --safetensors-load-strategy=prefetch "${SPEC_ARGS[@]}" &
LLM_PID=$!

for i in {1..720}; do
    kill -0 $LLM_PID 2>/dev/null || { echo "vLLM died early"; exit 1; }
    if curl -s http://localhost:${LLM_PORT}/health >/dev/null 2>&1; then
        echo "LLM ready on $(hostname):${LLM_PORT} (${LLM_NAME})"
        printf 'VLLM_BASE_URL=http://%s:%s/v1\nVLLM_MODEL=%s\nVLLM_MODEL_REPO=%s\nVLLM_JOB=%s\n' \
            "$(hostname)" "$LLM_PORT" "$LLM_NAME" "$LLM_MODEL" "$SLURM_JOB_ID" > "$ENDPOINT_FILE"
        break
    fi
    sleep 5
done
wait $LLM_PID
echo "vLLM exited with $?"
rm -f "$ENDPOINT_FILE"
. /beegfs1/urz/utils/slurmEpilog.sh
