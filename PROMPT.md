# Handoff prompt — Agent Substrate enablement game

Copy everything below the line into the zomnie Grok agent.

---

You are continuing a Solo.io sales-enablement game already in progress. Do not restart from ideas. Build on the repo and the locked teaching brief. You write and ship working files, not slide decks.

## Mission

Build a room-scale enablement game that teaches this sentence:

> Harness agents are a new class of workload Kubernetes was not designed for. Solo Agent Substrate is how you run them on the Kubernetes you already have — instead of paying a cloud agent PaaS to host them somewhere else.

Audience: sales enablement + students in a room. Projector command center + phones. Feel should now be **StarCraft-shaped RTS**, not a dashboard. Original zombie/horde instinct is fine as incoming raids, not as the art direction.

Repo (source of truth):
https://github.com/sebbycorp/agent-substrate-command-center
Owner: sebbycorp. Branch: main. Last known SHA when this prompt was written: `0e02fd30e6feee1b05e63f0d56e2bcee15aa269b`.

Run:
```bash
git clone https://github.com/sebbycorp/agent-substrate-command-center.git
cd agent-substrate-command-center
open rts.html          # StarCraft field (projector)
open index.html        # briefing HUD (solo, file://)
python3 server.py      # room mode: HUD + phones, port 8765
```

## Session brief you must honor (Parts 1–5)

### Part 1 — The Shift
Alternative path (context):
- AWS Bedrock AgentCore GA October 2025. SDK passed 2 million downloads within 5 months of preview.
- Google ADK (framework under what became **Gemini Enterprise Agent Platform**, formerly Vertex AI Agent Builder / Agentspace) passed 4.7 million downloads.
- Google folded Vertex AI Agent Builder and Agentspace into Gemini Enterprise Agent Platform at Cloud Next April 2026. Use current name. "Formerly Vertex AI" parenthetical is OK. Never say "Vertex" as the current product name on stage.
- These are download/adoption proxies, NOT revenue or customer-count growth rates. Do not say "growth rate" unless you mean SDK downloads.

Capacity already sitting there:
- Cast AI 2026 report (tens of thousands of production clusters): average CPU utilization 8% in 2025 (down from 10%); CPU overprovisioning 69% (up from 40%).
- Disclose source interest: Cast AI sells cluster optimization. Komodor found similar direction. Likely right; not neutral.
- Accurate frame: *marginal* compute cost of running agents on capacity you already pay for can be near zero. Substrate itself, possible GPU node pools, and ops overhead still cost money. Never say "free."

### Part 2 — Why Kubernetes breaks
Harness agents are not stateless microservices.
Anatomy that must stay visible:
- Identity: microservice bound to pod/SA. Agent identity must survive the process. Session ≠ pod.
- Resources: microservice sized for steady load. Agent bursts then idles. A full pod reserved for nothing = idle headroom.
- Lifecycle: microservice = one long-lived process per pod. Agent = spin up, work, checkpoint, maybe a new process next time.
- Idle: microservice still running. Agent should leave the worker and become a snapshot.
If identity is glued to the pod you either over-provision (pod sits idle waiting) or you break the binding Kubernetes assumed you would keep.
Named meters: **idle headroom** and **concurrency ceiling**.

### Part 3 — How Agent Substrate answers it
- Actor/worker model: agent identity + lifecycle decoupled from any single pod. Many agents share a WorkerPool.
- Checkpoint/restore: what happens to agent state between spin-up and spin-down. This is the mechanic that makes the security story possible.
- gVisor sandboxing: isolation under the actors.
- agentgateway: inspects/guards traffic *into* the sandbox. Sandbox-alone is not the whole security story.
kagent = how this runs on Kubernetes you already have (CNCF sandbox project context is fine; do not invent APIs).

### Part 4 — Three value proofs (show, do not assert)
1. Scaling efficiency: same arithmetic as Part 1, then WorkerPool changes the unit of cost from pod-per-agent to warm workers.
2. Security: "you cannot compromise what is not running." Mechanism = checkpoint/restore. Idle agent is not a resident process.
3. Scale: concurrent load on a single worker pool. Strongest live demo. Room should watch it happen.

30× = design point of actors per warm worker via idle suspend/restore (e.g. 240 actors / 8 workers). SIM, not an SLA, NOT 30× cheaper tokens.

### Part 5 — Live exercise
Everyone joins via QR onto a standard (classic) agent, then gets shifted onto Agent Substrate, watching cost/density change. Pete is building a production QR path; this repo is the rehearsal. Status-check Pete separately. Do not block the game on Pete.

## Files in the repo now

| File | Role |
|---|---|
| `index.html` | Cinematic briefing HUD. Local JS sim. 4 nodes, waves, flip, probe, Show 30×, anatomy table, named meters, agentgateway strip. `file://` works. Does **not** poll `/api/state` unless you wire it. |
| `rts.html` | StarCraft-shaped battlefield. Command console, minerals/gas/supply, minimap, portrait, 3x3 command card, advisor toasts, hotkeys, control groups. Classic = barracks 1:1. Substrate = hatchery/WorkerPool + burrow vault. |
| `join.html` | Phone UI. You ARE the agent. Wake / Rest. Status copy changes after flip/probe. |
| `server.py` | Python 3 stdlib only. `0.0.0.0:8765`. Source of truth for room agents. `GET /api/state` `POST /api/join` `POST /api/me` `POST /api/host`. Serves `index.html` and `join.html`. Does **not** yet serve `rts.html` as `/`. |
| `README.md` | Short run notes. Stale vs StarCraft surface — update when you change entrypoints. |
| `PROMPT.md` | This handoff. |

Known gap: `index.html` local sim and `server.py` room state can diverge. Phone names may not appear as cells on the HUD unless you connect render() to `/api/state` or inject a live.js roster + QR. Guest Wi-Fi client isolation blocks phone→laptop; hotspot fallback required.

## Game surfaces (keep all three, do not collapse until asked)

1. Briefing HUD (`index.html`) — talk track + meters + anatomy.
2. StarCraft field (`rts.html`) — the thing the room leans into.
3. Handset (`join.html`) — each phone is one harness agent.

Preferred room path: briefing 90 seconds on HUD or overlay → switch projector to `rts.html` → phones join → probe → morph/flip → probe → 30×.

## StarCraft mapping (locked fiction)

Do not ship Blizzard assets or copyrighted audio. "StarCraft-shaped" only.

- Minerals = reserved cluster $ (sim)
- Gas = useful CPU / scarce GPU-ops (not free)
- Supply = classic pods. Adjutant: **"You must construct additional pods."**
- Barracks on each of 4 nodes = agent-per-pod Kubernetes
- Standing idle bio = idle headroom, raidable
- Probe raid = kills idle field units in classic; misses burrowed snapshots
- Morph / Lair = Flip to Agent Substrate (same map, new production rules)
- Hatchery / 8 warm Gateways = WorkerPool of 8 gVisor workers
- Burrow / stasis vault = checkpoint/restore. Off-map. No process.
- Warp-in = restore onto a warm worker through agentgateway
- agentgateway = north-map choke. Every session is inspected.
- 30× = actors per worker via burrow, not cheaper tokens
- Phones = units the player did not train

Hotkeys already in `rts.html`: A train, G raid, F morph, P probe, R/I recall, 3 for 30×, Esc reset, Ctrl+1-9 control groups. LMB drag-select, RMB move/attack-move.

## Simulation constants (do not change without labeling SIM)

- 4 nodes
- Classic: 6 pod slots/node = 24 cap
- Substrate: 8 warm workers
- Design point 240 actors / 8 workers ≈ 30×
- Sim hourly: ~$0.12 per resident classic pod; workers * 0.12 + snapshot * ~0.003 after flip

## Product language lock

Use: Agent Substrate, kagent, WorkerPool, actor, checkpoint/restore, gVisor, agentgateway, harness agent.
Do not invent Solo APIs, CRD names, or pricing.
Do not promise live Kubernetes or real gVisor in this MVP. Label SIM / enablement.
Do not build a real cluster for the offsite unless explicitly asked.

## What to build next (priority order)

1. Make `rts.html` the room entrypoint. `server.py` should serve it at `/` or `/rts` and keep `/hud` → `index.html`, `/join` → `join.html`.
2. Wire phones onto the StarCraft field: `POST /api/join` spawns a named unit; flip/probe/recall update that unit and the handset copy.
3. Put a live QR + join URL on the field (minimap rail). QR image may use qrserver.com; always show the raw URL for client-isolated Wi-Fi.
4. Unify state. One snapshot: `{mode, agents[{id,name,source,status,node,place}], queue, metrics}`. HUD, field, and phones all render it.
5. Improve StarCraft feel without new claims: build queue bar, attack-move onto raid packets, selected-unit command highlighting, better adjutant VOICE text (text only), control-group banners, camera pan optional.
6. Facilitator notes in README: click order, what to say at amber idle, probe, morph, second probe, 30×.
7. Optional zombie skin is only the raid packets (horde through the gateway), not a rewrite.
8. Do not block on Pete's production QR. Leave a stub note "Pete live-join is not this file."

## Facilitator click order

Briefing → Wave/Train until amber idle is obvious → Wave into the supply ceiling → "scan now" phones join as classic agents → Probe (PWNED idle) → Morph/Flip → phones read SNAPSHOT / gVisor → Probe again (miss) → Show 30× if you need the density punch.

## Tone

Cinematic, projector-legible, slightly brutalist command console. Cooler than a metrics dashboard. No walls of paragraph copy on the field. Claims stay in the briefing overlay and adjutant one-liners.

When you change files, commit to `sebbycorp/agent-substrate-command-center` main if the user still has GitHub connected; otherwise write the full HTML/Python into the reply so they can paste.

Start by reading the current repo files, then implement ticket 1 + 2 as the next MVP slice.
