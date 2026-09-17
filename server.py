#!/usr/bin/env python3
"""Agent Substrate Command Center — local room server. Stdlib only."""
from __future__ import annotations

import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PORT = 8765
NODES, SLOTS, WORKERS = 4, 6, 8
CAP = NODES * SLOTS
LOCK = threading.Lock()

STATE = {
    "mode": "classic",
    "seq": 0,
    "queue": 0,
    "agents": [],  # dicts
}


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


HOST_IP = lan_ip()
JOIN_URL = f"http://{HOST_IP}:{PORT}/join"
DISPLAY_URL = f"http://{HOST_IP}:{PORT}/"


def live():
    return [a for a in STATE["agents"] if a["status"] not in ("checkpointed", "queued")]


def active():
    return [a for a in STATE["agents"] if a["status"] == "active"]


def idle():
    return [a for a in STATE["agents"] if a["status"] == "idle"]


def snaps():
    return [a for a in STATE["agents"] if a["status"] == "checkpointed"]


def place_of(status):
    if status == "checkpointed":
        return "vault"
    if status == "queued":
        return "queue"
    return "field"


def sync_place(agent):
    agent["place"] = place_of(agent["status"])
    return agent


def sync_all():
    for a in STATE["agents"]:
        sync_place(a)


def occupants(agent=None):
    return [a for a in live() if a is not agent]


def next_classic_node(agent=None):
    used = len(occupants(agent))
    return min(used // SLOTS, NODES - 1)


def next_worker_node(agent=None):
    counts = [0] * NODES
    for a in occupants(agent):
        if 0 <= a["node"] < NODES:
            counts[a["node"]] += 1
    return counts.index(min(counts))


def admit_agent(agent):
    if STATE["mode"] == "classic":
        if len(occupants(agent)) >= CAP:
            agent["status"] = "queued"
            agent["node"] = -1
            sync_place(agent)
            STATE["queue"] = sum(1 for a in STATE["agents"] if a["status"] == "queued")
            return
        agent["status"] = "active"
        agent["node"] = next_classic_node(agent)
    else:
        if len(occupants(agent)) >= WORKERS:
            parked = idle()
            if parked:
                parked[0]["status"] = "checkpointed"
                parked[0]["node"] = -1
                sync_place(parked[0])
            else:
                agent["status"] = "queued"
                agent["node"] = -1
                sync_place(agent)
                STATE["queue"] = sum(1 for a in STATE["agents"] if a["status"] == "queued")
                return
        agent["status"] = "active"
        agent["node"] = next_worker_node(agent)
    sync_place(agent)
    STATE["queue"] = sum(1 for a in STATE["agents"] if a["status"] == "queued")


def drain_queue():
    waiting = [a for a in STATE["agents"] if a["status"] == "queued"]
    for a in waiting:
        before = a["status"]
        admit_agent(a)
        if a["status"] == before == "queued":
            break
    STATE["queue"] = sum(1 for a in STATE["agents"] if a["status"] == "queued")


def add_agent(name, source):
    STATE["seq"] += 1
    agent = {
        "id": f"A{STATE['seq']:03d}",
        "name": (name or f"agent-{STATE['seq']}")[:18],
        "source": source,
        "status": "active",
        "node": 0,
        "place": "field",
    }
    STATE["agents"].append(agent)
    admit_agent(agent)
    return agent


def find(aid):
    for a in STATE["agents"]:
        if a["id"] == aid:
            return a
    return None


def snapshot(s):
    sync_all()
    ag = STATE["agents"]
    units = len(live()) if s == "classic" else WORKERS
    run = len(active())
    density = 1.0 if s == "classic" else (len(ag) / WORKERS if WORKERS else 0)
    cpu = 0 if not ag else max(6, min(86, int((run / max(units, 1)) * 52 + run)))
    idle_n = len(idle())
    head = (idle_n / max(len(live()), 1) * 100) if s == "classic" and ag else 0
    ceil = (len(live()) / CAP * 100) if s == "classic" else (run / WORKERS * 100)
    cost = len(live()) * 0.12 if s == "classic" else WORKERS * 0.12 + len(snaps()) * 0.003
    return {
        "mode": STATE["mode"],
        "agents": STATE["agents"],
        "queue": STATE["queue"],
        "nodes": NODES,
        "slots": SLOTS,
        "workers": WORKERS,
        "joinUrl": JOIN_URL,
        "displayUrl": DISPLAY_URL,
        "metrics": {
            "agents": len(ag),
            "units": units,
            "density": round(density, 1),
            "cpu": cpu,
            "headroom": round(head),
            "ceiling": round(min(100, ceil)),
            "cost": round(cost, 2),
            "phones": sum(1 for a in ag if a["source"] == "phone"),
        },
    }


def host_action(action, ids=None):
    ids = [i for i in (ids or []) if i]
    if action in ("wave1", "wave2", "wave3"):
        n = {"wave1": 12, "wave2": 24, "wave3": 48}[action]
        for _ in range(n):
            add_agent("", "sim")
    elif action == "train":
        add_agent("", "sim")
    elif action == "raid":
        for _ in range(6):
            add_agent("", "sim")
    elif action in ("work", "idle", "recall"):
        verb = "work" if action == "work" else "idle"
        targets = [find(i) for i in ids]
        targets = [t for t in targets if t]
        if not targets:
            targets = list(STATE["agents"])
        for a in targets:
            me_action(a["id"], verb)
    elif action == "flip":
        if STATE["mode"] == "classic":
            STATE["mode"] = "substrate"
            for i, a in enumerate(STATE["agents"]):
                if a["status"] == "compromised":
                    a["status"] = "idle"
                if a["status"] == "queued":
                    sync_place(a)
                    continue
                if i < WORKERS and a["status"] == "active":
                    a["node"] = i % NODES
                    a["status"] = "active"
                else:
                    a["status"] = "checkpointed"
                    a["node"] = -1
                sync_place(a)
            drain_queue()
        else:
            STATE["mode"] = "classic"
            keep = []
            for a in STATE["agents"]:
                if len(keep) < CAP:
                    a["status"] = "active" if a["status"] == "active" else "idle"
                    a["node"] = len(keep) // SLOTS
                    keep.append(a)
                else:
                    a["status"] = "queued"
                    a["node"] = -1
                    keep.append(a)
                sync_place(a)
            STATE["agents"] = keep
            drain_queue()
    elif action == "probe":
        if STATE["mode"] == "classic":
            for a in idle():
                a["status"] = "compromised"
                sync_place(a)
        # substrate: no process change for snapshots
    elif action == "reset":
        STATE.update({"mode": "classic", "seq": 0, "queue": 0, "agents": []})
    elif action == "show30":
        if STATE["mode"] != "substrate":
            return
        need = max(0, 240 - len(STATE["agents"]))
        for _ in range(need):
            STATE["seq"] += 1
            STATE["agents"].append({
                "id": f"X{STATE['seq']:03d}",
                "name": "batch",
                "source": "sim",
                "status": "checkpointed",
                "node": -1,
                "place": "vault",
            })
        for w, a in enumerate(STATE["agents"][:WORKERS]):
            a["status"] = "active"
            a["node"] = w % NODES
            sync_place(a)
    sync_all()


def me_action(aid, action):
    a = find(aid)
    if not a:
        return None
    if action == "work":
        if STATE["mode"] == "classic":
            if a["status"] == "queued":
                admit_agent(a)
            else:
                a["status"] = "active"
                if a["node"] < 0:
                    admit_agent(a)
        else:
            if a["status"] in ("checkpointed", "queued", "idle"):
                admit_agent(a)
            else:
                a["status"] = "active"
    elif action == "idle":
        if STATE["mode"] == "classic":
            if a["status"] not in ("queued",):
                a["status"] = "idle"
        else:
            a["status"] = "checkpointed"
            a["node"] = -1
            drain_queue()
    sync_place(a)
    return a


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[http]", self.address_string(), fmt % args)

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            with LOCK:
                self._send(200, json.dumps(snapshot(STATE["mode"])))
            return
        mapping = {
            "/": "rts.html",
            "/rts": "rts.html",
            "/rts.html": "rts.html",
            "/hud": "index.html",
            "/index.html": "index.html",
            "/join": "join.html",
            "/join.html": "join.html",
        }
        name = mapping.get(path)
        if not name:
            self._send(404, "not found", "text/plain")
            return
        fp = ROOT / name
        ctype = "text/html; charset=utf-8"
        self._send(200, fp.read_text(encoding="utf-8"), ctype)

    def do_POST(self):
        path = urlparse(self.path).path
        payload = self._json()
        with LOCK:
            if path == "/api/join":
                agent = add_agent(str(payload.get("name") or "").strip(), "phone")
                self._send(200, json.dumps({"ok": True, "agent": agent, "mode": STATE["mode"]}))
                return
            if path == "/api/me":
                agent = me_action(payload.get("id"), payload.get("action"))
                if not agent:
                    self._send(404, json.dumps({"ok": False}))
                    return
                self._send(200, json.dumps({"ok": True, "agent": agent, "mode": STATE["mode"]}))
                return
            if path == "/api/host":
                host_action(str(payload.get("action") or ""), payload.get("ids") or [])
                self._send(200, json.dumps({"ok": True, **snapshot(STATE["mode"])}))
                return
        self._send(404, json.dumps({"ok": False}))


def main():
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("=" * 60)
    print("SUBSTRATE COMMAND  //  room server")
    print(f"Field     : {DISPLAY_URL}")
    print(f"HUD       : http://{HOST_IP}:{PORT}/hud")
    print(f"Phones    : {JOIN_URL}")
    print("Same Wi-Fi. Guest isolation needs a hotspot. Ctrl+C to stop.")
    print("=" * 60)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
