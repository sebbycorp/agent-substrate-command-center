# Agent Substrate Command Center

Big-screen HUD + phone join. No npm. No cluster.

## Room mode (phones)

Same Wi‑Fi as the presenter laptop.

```bash
python3 server.py
```

Open the printed URL on the projector (usually `http://localhost:8765`).  
Phones scan the QR or open `http://<laptop-ip>:8765/join`.

Each phone **is an agent**. Wake / Rest from the handset. Flip and Probe from the big screen. Status updates on the phone.

## Solo mode (no server)

```bash
open index.html
```

Local sim only. No phones.

## Click order

Briefing → Wave 1 → people join → Wave 2 → Probe → Flip → phones change → Probe → Show 30×.
