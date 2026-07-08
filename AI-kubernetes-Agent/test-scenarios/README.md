# Kubernetes Failure Test Scenarios

Use these manifests to validate end-to-end troubleshooting with the AI Kubernetes Agent.

## Prerequisites

- A Kubernetes cluster (minikube, kind, Docker Desktop, or cloud)
- `kubectl` configured and the context selected in the dashboard
- Backend running with access to the same kubeconfig

## Quick start

```bash
kubectl create namespace agent-test
```

Apply one scenario at a time, run **Investigate Cluster** in the dashboard, then clean up before the next scenario.

```bash
kubectl delete namespace agent-test
```

---

## Scenario 1 — CrashLoopBackOff (missing environment variable)

**Apply:**

```bash
kubectl apply -f test-scenarios/01-crashloop-missing-env.yaml
```

**Expected diagnosis:**

- Root cause: missing environment variable / startup failure
- Suggested fix: add the missing env var via ConfigMap/Secret and restart

**Cleanup:**

```bash
kubectl delete -f test-scenarios/01-crashloop-missing-env.yaml
```

---

## Scenario 2 — ImagePullBackOff (wrong image tag)

**Apply:**

```bash
kubectl apply -f test-scenarios/02-imagepull-wrong-tag.yaml
```

**Expected diagnosis:**

- Root cause: invalid image or tag
- Suggested fix: update deployment image to a valid tag

**Cleanup:**

```bash
kubectl delete -f test-scenarios/02-imagepull-wrong-tag.yaml
```

---

## Scenario 3 — OOMKilled (low memory limits)

**Apply:**

```bash
kubectl apply -f test-scenarios/03-oom-low-memory.yaml
```

Wait 30–60 seconds for the pod to restart and hit the memory limit.

**Expected diagnosis:**

- Root cause: container exceeded memory limit
- Suggested fix: increase memory requests/limits

**Cleanup:**

```bash
kubectl delete -f test-scenarios/03-oom-low-memory.yaml
```

---

## Scenario 4 — Service selector mismatch

**Apply:**

```bash
kubectl apply -f test-scenarios/04-service-selector-mismatch.yaml
```

**Expected diagnosis:**

- Root cause: service selector does not match pod labels
- Suggested fix: align service selector with pod labels

**Cleanup:**

```bash
kubectl delete -f test-scenarios/04-service-selector-mismatch.yaml
```

---

## Tips

- Select the correct cluster context in the dashboard before investigating.
- If email verification blocks login, complete OTP verification first.
- For Docker, mount your kubeconfig:

  ```yaml
  volumes:
    - ${HOME}/.kube:/root/.kube:ro
  ```

- If no failures are detected after applying a scenario, wait for pods to enter a failing state (`kubectl get pods -n agent-test -w`).
