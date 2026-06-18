"""Chaff FastAPI backend.

Exposes:
  * GET  /api/health           — liveness probe
  * GET  /api/vault            — vault metadata
  * POST /api/vault/crack      — decrypt one guess (authentic Honey Encryption)
  * POST /api/vault/flood      — a burst of decoy cards (simulated brute force)
  * GET  /api/stats            — attack leaderboards
  * GET  /api/attacks/recent   — recent attack backlog
  * GET  /api/honeypot         — decoy server location
  * WS   /ws/attacks           — live stream of attack events + stats
If a built frontend exists at ../frontend/dist it is served at /.
"""

from __future__ import annotations

import asyncio
import os
import random
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import vault
from .attacks import AttackSimulator
from .attacks.cowrie import CowrieTailer
from .attacks.data import HONEYPOT

simulator = AttackSimulator()


class ConnectionManager:
    """Tracks live WebSocket clients and fans out broadcasts."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)

    async def broadcast(self, message: dict) -> None:
        for ws in list(self._connections):
            try:
                await ws.send_json(message)
            except Exception:  # noqa: BLE001 - drop any client that errors out
                self.disconnect(ws)


manager = ConnectionManager()


def _stats() -> dict:
    """Combine attack leaderboards with the running decoy-served counter."""
    return {**simulator.stats(), "decoys_served": vault.decoys_served()}


def _make_source():
    """Use a real Cowrie log if CHAFF_COWRIE_LOG points at one, else the
    built-in simulator (returns None)."""
    log = os.environ.get("CHAFF_COWRIE_LOG")
    if log and Path(log).exists():
        return CowrieTailer(log)
    return None


async def _attack_loop() -> None:
    """Stream attack events (real Cowrie log if configured, else the simulator)
    plus periodic leaderboard updates."""
    tailer = _make_source()
    ticks = 0
    try:
        while True:
            if tailer is not None:
                events = [simulator.ingest(fields) for fields in tailer.poll()]
            else:
                events = [simulator.random_event()]
            for event in events:
                await manager.broadcast({"type": "attack", "event": event.to_dict()})
                ticks += 1
                if ticks % 5 == 0:
                    await manager.broadcast({"type": "stats", "stats": _stats()})
            if not events:
                await manager.broadcast({"type": "stats", "stats": _stats()})
            await asyncio.sleep(1.0 if tailer is not None else random.uniform(0.35, 1.1))
    except asyncio.CancelledError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_attack_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Chaff", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CrackRequest(BaseModel):
    password: str


class FloodRequest(BaseModel):
    count: int = Field(default=25, ge=1, le=200)


class ChallengeRequest(BaseModel):
    n: int = Field(default=6, ge=2, le=12)


class GuessRequest(BaseModel):
    id: str
    index: int


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/honeypot")
def get_honeypot() -> dict:
    return HONEYPOT


@app.get("/api/vault")
def get_vault() -> dict:
    return vault.metadata()


@app.post("/api/vault/crack")
def post_crack(req: CrackRequest) -> dict:
    return vault.crack(req.password)


@app.post("/api/vault/flood")
def post_flood(req: FloodRequest) -> dict:
    return {"results": vault.flood(req.count)}


@app.post("/api/vault/challenge")
def post_challenge(req: ChallengeRequest) -> dict:
    return vault.challenge(req.n)


@app.post("/api/vault/challenge/guess")
def post_challenge_guess(req: GuessRequest) -> dict:
    return vault.guess_challenge(req.id, req.index)


@app.get("/api/stats")
def get_stats() -> dict:
    return _stats()


@app.get("/api/attacks/recent")
def get_recent() -> dict:
    return {"events": simulator.recent()}


@app.websocket("/ws/attacks")
async def ws_attacks(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        await ws.send_json(
            {
                "type": "init",
                "honeypot": HONEYPOT,
                "events": simulator.recent(),
                "stats": _stats(),
            }
        )
        while True:
            # We don't expect client messages; this keeps the socket open and
            # surfaces disconnects.
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:  # noqa: BLE001
        manager.disconnect(ws)


# Serve the built frontend if it exists (single-process production deploy).
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="frontend")
