#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing kind..."
curl -Lo /usr/local/bin/kind \
  https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x /usr/local/bin/kind

echo "==> Creating kind cluster 'cortex-demo'..."
kind create cluster --name cortex-demo --wait 60s

echo "==> Verifying cluster..."
kubectl cluster-info --context kind-cortex-demo

echo "==> Installing cortexapps-cli..."
pip install cortexapps-cli --quiet

echo "==> Done. Run: cortex solutions post-install -s kubernetes-agent"
