# Agent Substrate Command Center

Playable sales-enablement MVP. Single HTML file. No build step. No cluster.

## Open

```bash
git clone https://github.com/sebbycorp/agent-substrate-command-center.git
open index.html
```

Or:

```bash
python3 -m http.server 8080
```

Full-screen the briefing overlay first. Click **Enter command center**.

## Facilitator path (8 min)

1. Briefing: PaaS path + idle capacity + anatomy table.
2. Wave 1 — let pods go amber.
3. Wave 2 / 3 — concurrency ceiling (queue).
4. Attack probe — idle processes get hit.
5. Flip to Substrate — same 4 nodes, 8 warm workers.
6. Room joins or Wave 3 — pool absorbs load.
7. Show 30× — 240 actors / 8 workers. Say the assumption out loud.
8. Probe again — snapshots have no process. agentgateway drops the probe.

## What 30× means here

Actors hosted per warm worker by suspending idle actors (RAM + filesystem checkpoint) to object storage. Not 30× cheaper tokens. Design point from the public kagent Substrate writeup.

## Not in this MVP

Pete QR live-join. Room joins is a stub.
