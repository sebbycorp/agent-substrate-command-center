# Handoff prompt for zomnie agent

Copy everything below the line into the next Grok bot and keep building.

---

You are continuing work on a sales-enablement game for Solo.io Agent Substrate. Do not start over. Read this entire brief before touching files.

## Who this is for

Presenter laptop + projector + optional phones on the same Wi-Fi. Audience is sales enablement, not game designers. The game must teach a session, not win Steam.

## Session goal (do not dilute)

Teach the room that **harness agents are a new class of workload that Kubernetes was not designed for**, and that **Solo Agent Substrate is how you run them on the Kubernetes platform you already have** — instead of paying a cloud agent PaaS to host them somewhere else.

## Locked product claims (never invent numbers or names)

- AWS Bedrock AgentCore went GA October 2025. SDK passed **2 million downloads** within 5 months of preview. These are **download/adoption proxies**, not revenue or customer-count growth. Do not say "growth rate" unless it is clearly SDK adoption.
- Google ADK passed **4.7 million downloads**. Product name on stage: **Gemini Enterprise Agent Platform** (formerly Vertex AI Agent Builder / Agentspace, folded at Cloud Next April 2026). Do **not** say "Vertex" as the current name.
- Cast AI 2026 report: average CPU utilization **8%** in 2025 (down from 10%); CPU overprovisioning **69%** (up from 40%). Disclose vendor interest: Cast AI sells optimization. Komodor saw the same direction. Framing: **marginal compute on capacity you already buy ≈ 0**. Substrate, GPUs, and ops still cost.
- **30×** means **actors per warm worker via idle suspend / checkpoint**, e.g. 240 actors / 8 workers. It does **not** mean cheaper tokens, an SLA, or a benchmark you measured.
- Security line: **"you can't compromise what's not running."** Mechanism: checkpoint/restore. Idle agent is a snapshot (RAM + filesystem), not a resident process. Isolation under it: **gVisor**.
- Runtime pieces: **actor/worker model** (identity + lifecycle detached from a single pod; many agents share a worker pool), **checkpoint/restore**, **gVisor sandboxing**, **agentgateway** as the policy/traffic choke (not the sandbox itself).
- kagent = CNCF Sandbox project for agents on Kubernetes. Agent Substrate is how kagent runs harness agents on the cluster you already pay for.
- Simulation only. Never claim this is a live Kubernetes cluster.

## Session anatomy the game must carry

Part 1 — The Shift: PaaS path vs idle capacity already sitting in the cluster.
Part 2 — Why K8s breaks: harness agents are not microservices. Identity / resources / lifecycle / idle were all bound to the pod. Over-provision or break the binding K8s assumed.
Part 3 — Agent Substrate answers: actor/worker, checkpoint/restore, gVisor.
Part 4 — Three value proofs (must be shown, not asserted):
1. Scaling efficiency — same arithmetic, then worker-pool changes the bill.
2. Security — idle is not a process.
3. Scale — concurrent load on one worker pool.
Part 5 — Live exercise: everyone joins via QR onto a standard agent, then gets shifted onto Agent Substrate. Pete owns production QR; this repo is the rehearsal.

Facilitator click order:
Briefing → Wave 1 (amber idle waste) → Wave 2 (ceiling) → people join on phones → Probe (pwn idle pods) → Flip Substrate → phones become snapshots/actors → Probe again (nothing to hit) → Show 30×.

## Repo (source of truth)

https://github.com/sebbycorp/agent-substrate-command-center

Files on main as of 2026-09-17:

| File | What it is | Status |
|---|---|---|
| `index.html` | Cinematic command-center HUD. Dark ops, gateway aperture, racks, meters, briefing overlay, Wave/Flip/Probe/30×. Works `file://`. | Solo sim. **Not wired** to `/api/state`. No QR. |
| `join.html` | Phone UI. You ARE the agent. Jack in / Wake / Rest. Polls `/api/state`. | Works when `server.py` is up. |
| `rts.html` | StarCraft-ish canvas field. Drag-select, RMB move, train, raid, flip, vault. | Local only. **Not bound** to phone state. |
| `server.py` | Python 3 stdlib. `0.0.0.0:8765`. GET `/` `/join` `/api/state`. POST `/api/join` `/api/me` `/api/host`. | Does **not** serve `/rts`. Does **not** inject live JS into the HUD. |
| `README.md` | Run notes. | Stale vs StarCraft surface. |

No npm. No K8s. No build step.

## Run

Solo HUD: `open index.html`
Solo field: `open rts.html`
Room: `python3 server.py` then projector `http://localhost:8765` and phones `http://<lan-ip>:8765/join`

Venue gotcha: guest Wi-Fi client isolation blocks phone→laptop. Use staff SSID or a hotspot.

## Shared protocol (keep this, do not invent a second one)

```
GET  /api/state  → {mode, agents[{id,name,source,status,node}], queue, joinUrl, metrics}
POST /api/join   {name} → {ok, agent, mode}
POST /api/me     {id, action: "work"|"idle"}
POST /api/host   {action: "wave1"|"wave2"|"wave3"|"flip"|"probe"|"reset"|"show30"}
```

Agent status: `active` | `idle` | `checkpointed` | `compromised` | `queued`
Classic cap: 4 nodes × 6 pods = 24.
Substrate: 8 warm gVisor workers. Extra agents checkpoint.

## StarCraft language (visual grammar, not Blizzard assets)

| SC | This mission | Line to say |
|---|---|---|
| Minerals / supply | Reserved $ / pod slots | Capacity you already bought |
| "Additional pylons" | "You must construct additional pods." | Concurrency ceiling |
| Barracks 1:1 | Classic agent-per-pod | Identity glued to the building |
| Idle bio on creep | Amber units standing on a node | Idle headroom — billed, raidable |
| Runby / snipe | Probe | Resident process is the surface |
| Morph Lair / warp-in | Flip Substrate | Same map, new production rules |
| Burrow / stasis | Checkpoint vault | No process on the field |
| Gateway | agentgateway choke | Traffic still inspected |
| Pop cheat | 30× | 240 actors / 8 workers via suspend |

Wanted HUD: top resource/supply bar, bottom portrait + command card + minimap, adjutant toasts, drag-select, RMB attack-move, hotkeys (T train, W a-move, I hold, R burrow, F morph, P probe, Ctrl+1-4 groups).

## What to build next (in this order)

1. Wire `index.html` to `/api/state` when served by `server.py`. Show QR + join URL. Host buttons POST `/api/host`. Keep `file://` fallback.
2. Serve `rts.html` at `/rts`. Same API. Phone joins appear as named units on the field.
3. Finish the StarCraft command console on `rts.html` (portrait, command card, minimap, adjutant, control groups) without stealing Blizzard art.
4. Probe must visibly snipe **idle field units only** in classic; Substrate vaulted units are off-map and survive.
5. After Flip, phone copy must change: classic idle = "still resident"; substrate checkpoint = "no process."
6. Keep briefing overlay with locked Part 1 names/numbers.
7. Do not require a real cluster. Do not add npm unless asked.
8. Update README with HUD vs RTS vs room instructions.

## Out of scope unless asked

Pete's production QR path. Real kagent / Agent Substrate / Agent Gateway wiring. Token-cost claims. New product names.

## Tone

Cinematic, enablement-sharp, a little dangerous. Cooler than a dashboard. Still a teaching tool first.
