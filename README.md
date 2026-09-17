# Agent Substrate Command Center

Sales-enablement MVP: a browser simulation that teaches why harness agents are a different Kubernetes workload, and what Agent Substrate changes.

This is a **simulation**, not a live cluster. Open `index.html` in any modern browser. No build step. No Kubernetes required.

## Run it

```bash
open index.html
```

Or from the repo root:

```bash
python3 -m http.server 8080
```

Then open http://localhost:8080

## What the room should feel

**Phase 1 — Classic Kubernetes (agent-per-pod)**

1. Click **Start wave**. Incoming sessions each claim a pod.
2. Watch utilization stay low while reserved capacity and cost climb. Agents burst, then sit idle — but the pod is still there.
3. Hit the concurrency ceiling. New sessions queue.
4. Click **Attack probe**. Idle resident processes are the attack surface.

**Phase 2 — Flip to Agent Substrate**

1. Click **Flip to Substrate**. Same nodes. Same wave. Different runtime.
2. Warm `WorkerPool` pods host actors. Idle actors checkpoint (RAM + filesystem) to object storage. Workers free up.
3. Density climbs because actors are multiplexed onto a small warm pool.
4. Click **Attack probe** again. You cannot compromise a process that is not running. A live actor still sits in a gVisor sandbox; traffic is meant to flow through agentgateway.

## Claims the HUD is allowed to make

| Claim | How the game states it |
| --- | --- |
| ~30× density | On-screen assumption: *actors hosted per worker via idle suspend/restore, not 30× cheaper tokens*. Source: kagent blog design point. |
| Idle K8s waste | Simulated 8–12% CPU while pods stay reserved. Cast AI 2026 report cited in the briefing panel with vendor-interest disclosure. |
| PaaS alternative | Bedrock AgentCore and Gemini Enterprise Agent Platform named as the path companies take when they do not want to run agents on existing clusters. |
| Security | “You cannot compromise what is not running” maps to checkpointed actors. Running actors are gVisor-isolated. |

## Session map (10 minutes)

1. Brief the shift (2 min): harness agent vs stateless microservice.
2. Play Phase 1 without talking over it (3 min).
3. Flip and replay the same load (3 min).
4. Debrief the three proofs: density, security, concurrent load on one pool (2 min).

QR / live join of the room onto a real `SandboxAgent` is **not** in this MVP. Next slice.

## Product names used

- Agent Substrate — Kubernetes-native actor runtime (WorkerPool, ActorTemplate, checkpoint/restore, gVisor or microVM)
- kagent — control plane (`SandboxAgent`, `AgentHarness`)
- agentgateway — traffic, identity, policy, cost attribution
- Do **not** say “Vertex AI” as the current Google product name. Use Gemini Enterprise Agent Platform.

## Next slices

- Facilitator presenter mode (big-screen typography, hide coach notes)
- QR join so each attendee is an actor that migrates onto the pool
- Optional live cost-model numbers from a real WorkerPool
