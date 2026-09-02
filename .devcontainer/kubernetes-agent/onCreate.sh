#!/usr/bin/env bash
set -euo pipefail

ARCH=$(uname -m)
BIN_ARCH="amd64"
[ "$ARCH" = "aarch64" ] && BIN_ARCH="arm64"

echo "==> Installing kubectl..."
curl -Lo /tmp/kubectl "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/${BIN_ARCH}/kubectl"
sudo install -o root -g root -m 0755 /tmp/kubectl /usr/local/bin/kubectl

echo "==> Installing helm..."
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo "==> Installing kind..."
curl -Lo /tmp/kind "https://kind.sigs.k8s.io/dl/latest/kind-linux-${BIN_ARCH}"
sudo install -o root -g root -m 0755 /tmp/kind /usr/local/bin/kind

echo "==> Creating kind cluster 'cortex-demo'..."
kind create cluster --name cortex-demo --wait 60s

echo "==> Verifying cluster..."
kubectl cluster-info --context kind-cortex-demo

echo "==> Installing cortexapps-cli..."
pip install cortexapps-cli --quiet

echo "==> Done. Run: cortex solutions post-install -s kubernetes-agent"
