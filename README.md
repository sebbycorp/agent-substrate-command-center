# Agent Substrate Command Center

Room-scale sales-enablement game. StarCraft-shaped field + briefing HUD + phones as harness agents. No npm. No cluster. Label **SIM**.

A sandbox is an isolated place for an agent to work without a permanent pod. Classic Kubernetes gives each agent its own pod even while idle. Agent Substrate lets many agents share warm workers; idle agents become snapshots (no process). Security, density, and cost are the three proofs. agentgateway is the front door.

## What the room should hear

1. A sandbox is an isolated place for an agent to work — no permanent pod.
2. Classic: Idle agents still own a pod — that's the waste, and it's attackable.
3. Substrate: many agents share warm workers. Idle agents become snapshots — no process.
4. Attack idle: PWNED — the process was still running.
5. Flip: same nodes. Now idle agents sleep as snapshots. Attack again: miss — nothing running to attack.
6. 30× means more agents per worker by sleeping idle ones — not cheaper tokens. agentgateway is the front door.

## Room mode (LAN host)

Same Wi-Fi as the presenter laptop. Python 3 only.

```bash
python3 server.py
```

Opens `0.0.0.0:8765`.

| Surface | URL |
|---|---|
| StarCraft field (projector entrypoint) | `http://<laptop-ip>:8765/` or `/rts` |
| Briefing HUD | `http://<laptop-ip>:8765/hud` |
| Phone handset | `http://<laptop-ip>:8765/join` |

On the field, the minimap rail shows a live QR (qrserver.com) **and** the raw join URL. If guest Wi-Fi has client isolation, phones cannot reach the laptop — use a hotspot.

Each phone **is one agent**. Join with a name to spawn a labeled unit on the field. Wake up / Go to sleep from the handset. Flip, Attack idle, Sleep, Wake from the big screen. One snapshot drives HUD, field, and phones.

Pete live-join is not this file.

## Solo rehearsal (no server)

```bash
open rts.html      # field
open index.html    # briefing HUD
```

Local sim only. No phones, no QR.

## Facilitator click order

1. Room `/` is the field immediately (QR on the rail so phones can join during the talk). Click the adjutant line to reopen the 20-second briefing, or use `/hud` for PaaS stats. Do not say Vertex as the current name. Do not say free.
2. **A Add agents** / **G Send load** until idle is obvious (hit **I Sleep** so idle units go gold). At gold idle: *idle agents still own a pod — that's the waste, and it's attackable.*
3. Wave into the supply ceiling. Adjutant: “You must construct additional pods.”
4. “Scan now” — phones join as classic agents (named triangles).
5. **P Attack idle** — **PWNED**. Handsets read PWNED — you were still running.
6. **F Flip to Substrate**. Same nodes, shared workers, sleeping-agent vault. Phones read snapshot.
7. **P Attack idle** again — miss. Nothing running to attack.
8. **3 Show 30×** if you need the density punch (more agents per worker by sleeping idle ones, not cheaper tokens).

## Claims to keep

- Gemini Enterprise Agent Platform (not “Vertex” as the current name)
- 2M / 4.7M are SDK download proxies, not revenue
- Cast AI 8% / 69% — they sell optimization
- 30× = actors per warm worker via idle suspend, not cheaper tokens
- Sim hourly: ~$0.12 per resident classic pod; after flip, 8 workers × 0.12 + snapshot × ~0.003
- Do not invent Solo APIs, CRDs, or pricing
