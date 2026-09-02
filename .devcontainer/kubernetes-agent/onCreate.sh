#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing kind..."
ARCH=$(uname -m)
KIND_ARCH="amd64"
[ "$ARCH" = "aarch64" ] && KIND_ARCH="arm64"
curl -Lo /tmp/kind "https://kind.sigs.k8s.io/dl/latest/kind-linux-${KIND_ARCH}"
sudo install -o root -g root -m 0755 /tmp/kind /usr/local/bin/kind

echo "==> Creating kind cluster 'cortex-demo'..."
kind create cluster --name cortex-demo --wait 60s

echo "==> Verifying cluster..."
kubectl cluster-info --context kind-cortex-demo

echo "==> Installing cortexapps-cli..."
pip install cortexapps-cli --quiet

echo "==> Done. Run: cortex solutions post-install -s kubernetes-agent"
