#!/usr/bin/env python3
"""Room-server contract tests. Stdlib only. Run: python3 test_server.py"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import server

ROOT = Path(__file__).resolve().parent


class RoomLogicTests(unittest.TestCase):
    def setUp(self):
        with server.LOCK:
            server.host_action("reset")

    def test_join_named_phone_is_field_unit(self):
        agent = server.add_agent("Ada", "phone")
        self.assertEqual(agent["name"], "Ada")
        self.assertEqual(agent["source"], "phone")
        self.assertEqual(agent["status"], "active")
        self.assertEqual(agent["place"], "field")
        self.assertGreaterEqual(agent["node"], 0)
        snap = server.snapshot(server.STATE["mode"])
        self.assertEqual(snap["mode"], "classic")
        self.assertEqual(snap["agents"][0]["place"], "field")
        self.assertIn("metrics", snap)
        self.assertEqual(snap["metrics"]["phones"], 1)

    def test_classic_caps_at_24_and_queues(self):
        for _ in range(25):
            server.add_agent("", "sim")
        self.assertEqual(server.STATE["queue"], 1)
        queued = [a for a in server.STATE["agents"] if a["status"] == "queued"]
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0]["place"], "queue")
        self.assertEqual(queued[0]["node"], -1)

    def test_classic_probe_pwns_idle(self):
        agent = server.add_agent("Ada", "phone")
        server.me_action(agent["id"], "idle")
        self.assertEqual(server.find(agent["id"])["status"], "idle")
        server.host_action("probe")
        hit = server.find(agent["id"])
        self.assertEqual(hit["status"], "compromised")
        self.assertEqual(hit["place"], "field")

    def test_substrate_probe_misses_checkpoint(self):
        agent = server.add_agent("Ada", "phone")
        server.me_action(agent["id"], "idle")
        server.host_action("flip")
        parked = server.find(agent["id"])
        self.assertEqual(server.STATE["mode"], "substrate")
        self.assertEqual(parked["status"], "checkpointed")
        self.assertEqual(parked["place"], "vault")
        server.host_action("probe")
        still = server.find(agent["id"])
        self.assertEqual(still["status"], "checkpointed")
        self.assertEqual(still["place"], "vault")

    def test_flip_after_pwn_becomes_snapshot(self):
        agent = server.add_agent("Ada", "phone")
        server.me_action(agent["id"], "idle")
        server.host_action("probe")
        server.host_action("flip")
        parked = server.find(agent["id"])
        self.assertEqual(parked["status"], "checkpointed")
        self.assertEqual(parked["place"], "vault")

    def test_phone_work_and_idle_follow_mode(self):
        agent = server.add_agent("Ada", "phone")
        server.me_action(agent["id"], "idle")
        self.assertEqual(server.find(agent["id"])["status"], "idle")
        server.me_action(agent["id"], "work")
        self.assertEqual(server.find(agent["id"])["status"], "active")
        server.host_action("flip")
        server.me_action(agent["id"], "idle")
        parked = server.find(agent["id"])
        self.assertEqual(parked["status"], "checkpointed")
        self.assertEqual(parked["place"], "vault")
        server.me_action(agent["id"], "work")
        live = server.find(agent["id"])
        self.assertEqual(live["status"], "active")
        self.assertEqual(live["place"], "field")

    def test_host_recall_and_work_ids(self):
        agent = server.add_agent("Ada", "phone")
        server.host_action("recall", [agent["id"]])
        self.assertEqual(server.find(agent["id"])["status"], "idle")
        server.host_action("work", [agent["id"]])
        self.assertEqual(server.find(agent["id"])["status"], "active")
        server.host_action("flip")
        server.host_action("recall", [agent["id"]])
        self.assertEqual(server.find(agent["id"])["status"], "checkpointed")

    def test_show30_is_actors_per_worker_not_token_price(self):
        server.host_action("flip")
        server.host_action("show30")
        self.assertGreaterEqual(len(server.STATE["agents"]), 240)
        snap = server.snapshot(server.STATE["mode"])
        self.assertEqual(snap["mode"], "substrate")
        self.assertAlmostEqual(snap["metrics"]["density"], 30.0, places=0)
        self.assertEqual(snap["metrics"]["units"], 8)

    def test_snapshot_shape(self):
        server.add_agent("Ada", "phone")
        snap = server.snapshot(server.STATE["mode"])
        for key in ("mode", "agents", "queue", "metrics", "joinUrl", "displayUrl"):
            self.assertIn(key, snap)
        agent = snap["agents"][0]
        for key in ("id", "name", "source", "status", "node", "place"):
            self.assertIn(key, agent)


class RoomHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def setUp(self):
        with server.LOCK:
            server.host_action("reset")

    def _get(self, path):
        with urllib.request.urlopen(self.base + path) as resp:
            return resp.status, resp.read(), resp.headers["Content-Type"]

    def _post(self, path, payload):
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_root_and_rts_serve_starcraft_field(self):
        field = ROOT.joinpath("rts.html").read_bytes()
        for path in ("/", "/rts", "/rts.html"):
            status, body, ctype = self._get(path)
            self.assertEqual(status, 200)
            self.assertIn("text/html", ctype)
            self.assertEqual(body, field)
            self.assertIn(b'id="c"', body)
            self.assertIn(b"joinurl", body)
            self.assertIn(b"qrserver.com", body)

    def test_hud_and_join_routes(self):
        status, body, _ = self._get("/hud")
        self.assertEqual(status, 200)
        self.assertIn(b"SUBSTRATE COMMAND", body)
        status, body, _ = self._get("/join")
        self.assertEqual(status, 200)
        self.assertIn(b"YOU ARE ONE AGENT", body)

    def test_api_join_then_state_and_probe_copy_contract(self):
        status, payload = self._post("/api/join", {"name": "Ada"})
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        agent = payload["agent"]
        self.assertEqual(agent["name"], "Ada")
        self.assertEqual(agent["place"], "field")
        self._post("/api/me", {"id": agent["id"], "action": "idle"})
        self._post("/api/host", {"action": "probe"})
        _, state = self._get_json("/api/state")
        hit = next(a for a in state["agents"] if a["id"] == agent["id"])
        self.assertEqual(hit["status"], "compromised")
        self._post("/api/host", {"action": "flip"})
        _, state = self._get_json("/api/state")
        parked = next(a for a in state["agents"] if a["id"] == agent["id"])
        self.assertEqual(state["mode"], "substrate")
        self.assertEqual(parked["status"], "checkpointed")
        self.assertEqual(parked["place"], "vault")
        self._post("/api/host", {"action": "probe"})
        _, state = self._get_json("/api/state")
        still = next(a for a in state["agents"] if a["id"] == agent["id"])
        self.assertEqual(still["status"], "checkpointed")

    def _get_json(self, path):
        status, body, _ = self._get(path)
        return status, json.loads(body.decode("utf-8"))


class SurfaceContractTests(unittest.TestCase):
    def test_rts_wires_live_state_and_qr(self):
        text = ROOT.joinpath("rts.html").read_text(encoding="utf-8")
        self.assertIn("/api/state", text)
        self.assertIn("/api/host", text)
        self.assertIn("qrserver.com", text)
        self.assertIn("joinurl", text)
        self.assertIn("Pete live-join is not this file", text)
        self.assertNotIn("sc.html", text)

    def test_join_copy_covers_pwn_and_snapshot(self):
        text = ROOT.joinpath("join.html").read_text(encoding="utf-8")
        self.assertIn("You are one agent", text)
        self.assertIn("Your name appears on the big screen", text)
        self.assertIn("You're running on your own pod.", text)
        self.assertIn("You're idle but still running", text)
        self.assertIn("PWNED — you were still running.", text)
        self.assertIn("You're awake on a shared worker.", text)
        self.assertIn("You're a snapshot — nothing running to attack.", text)
        self.assertIn("Wake up", text)
        self.assertIn("Go to sleep", text)
        self.assertIn("/api/state", text)
        self.assertIn("/api/me", text)

    def test_hud_can_follow_room_state(self):
        text = ROOT.joinpath("index.html").read_text(encoding="utf-8")
        self.assertIn("/api/state", text)
        self.assertIn("/api/host", text)
        self.assertIn("Pete live-join is not this file", text)
        self.assertIn('overlay").classList.add("hide")', text)

    def test_rts_room_copy_is_projector_legible(self):
        text = ROOT.joinpath("rts.html").read_text(encoding="utf-8")
        self.assertIn("Run agents on the Kubernetes you already pay for.", text)
        self.assertIn("A sandbox is an isolated place", text)
        self.assertIn("1 agent owns 1 pod even while idle", text)
        self.assertIn("Idle agents still own a pod — that's the waste.", text)
        self.assertIn("PWNED — the process was still running.", text)
        self.assertIn("Same nodes. Now idle agents sleep as snapshots — no process.", text)
        self.assertIn("Miss — nothing running to attack.", text)
        self.assertIn("30× means more agents per worker by sleeping idle ones — not cheaper tokens.", text)
        self.assertIn("This is a SIM for enablement — not a live cluster.", text)
        self.assertIn("CLASSIC · 1 AGENT = 1 POD", text)
        self.assertIn("SUBSTRATE · SHARED WORKERS", text)
        self.assertIn("A Add agents", text)
        self.assertIn("W Wake", text)
        self.assertIn("I Sleep", text)
        self.assertIn("G Send load", text)
        self.assertIn("F Flip to Substrate", text)
        self.assertIn("P Attack idle", text)
        self.assertIn("R Sleep selected", text)
        self.assertIn("3 Show 30×", text)
        self.assertIn("NODE · pods", text)
        self.assertIn("NODE · workers", text)
        self.assertIn("SLEEPING AGENTS", text)
        self.assertIn("You must construct additional pods.", text)
        self.assertIn("front door for agent traffic", text.lower())
        self.assertNotIn("Bedrock", text)
        self.assertNotIn("Cast AI", text)
        self.assertNotIn("TERRAN / CLASSIC K8S", text)
        self.assertNotIn("ZERG / AGENT SUBSTRATE", text)

    def test_hud_keeps_shortened_paas_stats(self):
        text = ROOT.joinpath("index.html").read_text(encoding="utf-8")
        self.assertIn("Bedrock", text)
        self.assertIn("Cast AI", text)
        self.assertIn("Gemini Enterprise Agent Platform", text)
        self.assertIn("formerly Vertex AI", text)
        self.assertIn("Add agents. Sleep them. Attack idle.", text)
        self.assertNotIn("fire Wave 1 and wait for the amber", text)

    def test_readme_has_room_talk_track(self):
        text = ROOT.joinpath("README.md").read_text(encoding="utf-8")
        self.assertIn("What the room should hear", text)
        self.assertIn("Idle agents still own a pod", text)
        self.assertIn("nothing running to attack", text)

    def test_no_duplicate_starcraft_field_file(self):
        self.assertFalse((ROOT / "sc.html").exists())

    def test_browser_scripts_parse(self):
        for name in ("rts.html", "index.html", "join.html"):
            html = ROOT.joinpath(name).read_text(encoding="utf-8")
            scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
            self.assertTrue(scripts, name)
            for i, script in enumerate(scripts):
                with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
                    fh.write(script)
                    path = fh.name
                try:
                    proc = subprocess.run(["node", "--check", path], capture_output=True, text=True)
                    self.assertEqual(proc.returncode, 0, f"{name} script {i}: {proc.stderr}")
                finally:
                    Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
