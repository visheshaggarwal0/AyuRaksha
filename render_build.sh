#!/usr/bin/env bash
# AyuRaksha Render Deployment Build Script
# Optimized for free-tier memory constraints (512MB RAM)
set -e

echo "=== [1/3] Upgrading pip ==="
python -m pip install --upgrade pip

echo "=== [2/3] Installing lightweight CPU-only PyTorch ==="
# Crucial: Installing standard torch downloads an 800MB+ CUDA wheel that crashes Render's 512MB build container.
# The CPU wheel is ~150MB and runs sentence-transformers embeddings cleanly.
python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

echo "=== [3/3] Installing AyuRaksha backend dependencies ==="
python -m pip install --no-cache-dir -r backend/requirements.txt

echo "=== Validating environment & pre-warming embedding cache ==="
python -c "import sentence_transformers; print('✓ Sentence-transformers loaded successfully in CPU mode')"

echo "=== Build Complete ==="
