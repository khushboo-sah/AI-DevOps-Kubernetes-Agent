#!/bin/sh
set -e

# kind/minikube/kubeconfig often use 127.0.0.1 or localhost for the API server.
# Inside Docker, those addresses point at the container — not your Mac/host.
# Rewrite them to host.docker.internal so kubectl in the backend can reach kind.
if [ -n "${KUBE_API_REWRITE_HOST:-}" ] && [ -f /root/.kube/config ]; then
  sed \
    -e "s|https://127.0.0.1|https://${KUBE_API_REWRITE_HOST}|g" \
    -e "s|http://127.0.0.1|http://${KUBE_API_REWRITE_HOST}|g" \
    -e "s|https://localhost|https://${KUBE_API_REWRITE_HOST}|g" \
    -e "s|http://localhost|http://${KUBE_API_REWRITE_HOST}|g" \
    /root/.kube/config > /tmp/kubeconfig-docker.yaml
  export KUBECONFIG=/tmp/kubeconfig-docker.yaml
  export KUBECONFIG_PATH=/tmp/kubeconfig-docker.yaml
  echo "Rewrote kubeconfig API server to ${KUBE_API_REWRITE_HOST} for Docker"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
