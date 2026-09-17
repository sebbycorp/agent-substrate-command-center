# Agent Substrate Command Center

Room-scale sales-enablement game. StarCraft-shaped field + briefing HUD + phones as harness agents. No npm. No cluster. Label **SIM**.

Learning goal is not only “under attack.” The sandbox is an isolated place for harness agents to work without permanent pods. Agent Substrate is how you run many agents on Kubernetes you already pay for (actor off the pod, warm workers, checkpoint when idle) instead of a cloud agent PaaS. Security (“you cannot compromise what is not running”) is one of three proofs, with density and cost.

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

Each phone **is an agent**. Jack in with a name to spawn a labeled unit on the field. Wake / Rest from the handset. Flip, Probe, Idle, Recall, Work from the big screen. One snapshot drives HUD, field, and phones.

Pete live-join is not this file.

## Solo rehearsal (no server)

```bash
open rts.html      # field
open index.html    # briefing HUD
```

Local sim only. No phones, no QR.

## Facilitator click order

1. Briefing on `/` overlay or `/hud` (~90s). Alternative path + idle capacity + anatomy. Do not say Vertex as the current name. Do not say free.
2. Switch projector to the field if you briefed on `/hud`.
3. **A Train** / **G Raid** until amber idle is obvious (hit **I Idle** so standing bio is gold).
4. Wave into the supply ceiling. Adjutant: “You must construct additional pods.”
5. “Scan now” — phones join as classic agents (named triangles).
6. **P Probe** — idle processes are **PWNED**. Handsets read PWNED.
7. **F Morph** to Agent Substrate. Same map, WorkerPool + burrow vault. Phones read SNAPSHOT / gVisor.
8. **P Probe** again — misses. Snapshots have no process.
9. **3** Show 30× if you need the density punch (240 actors / 8 workers via burrow, not cheaper tokens).

## Claims to keep

- Gemini Enterprise Agent Platform (not “Vertex” as the current name)
- 2M / 4.7M are SDK download proxies, not revenue
- Cast AI 8% / 69% — they sell optimization
- 30× = actors per warm worker via idle suspend, not cheaper tokens
- Sim hourly: ~$0.12 per resident classic pod; after flip, 8 workers × 0.12 + snapshot × ~0.003
- Do not invent Solo APIs, CRDs, or pricing
