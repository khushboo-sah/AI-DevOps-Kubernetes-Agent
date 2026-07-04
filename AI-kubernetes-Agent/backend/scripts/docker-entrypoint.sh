#!/bin/sh
set -e

# kind/minikube kubeconfig uses 127.0.0.1 — unreachable from inside Docker.
# kind clusters: backend joins the "kind" Docker network and kubectl uses
# https://<cluster>-control-plane:6443 (see app/kubernetes/kind_docker.py).
# Other local clusters: rewrite API URL to host.docker.internal.
if [ -n "${KUBE_API_REWRITE_HOST:-}" ] && [ -f /root/.kube/config ]; then
  sed \
    -e "s|https://127.0.0.1|https://${KUBE_API_REWRITE_HOST}|g" \
    -e "s|http://127.0.0.1|http://${KUBE_API_REWRITE_HOST}|g" \
    -e "s|https://localhost|https://${KUBE_API_REWRITE_HOST}|g" \
    -e "s|http://localhost|http://${KUBE_API_REWRITE_HOST}|g" \
    /root/.kube/config > /tmp/kubeconfig-docker.yaml
  export KUBECONFIG=/tmp/kubeconfig-docker.yaml
  export KUBECONFIG_PATH=/tmp/kubeconfig-docker.yaml
  echo "Prepared Docker kubeconfig (host fallback: ${KUBE_API_REWRITE_HOST})"
fi

if [ "${KUBE_KIND_DOCKER_NETWORK:-}" = "true" ]; then
  echo "kind Docker network mode enabled (API via <cluster>-control-plane:6443)"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
