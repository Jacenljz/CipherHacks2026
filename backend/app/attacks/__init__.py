"""Live attack feed for the Mirage globe.

In production this is replaced by a tail of a real Cowrie honeypot log; the
simulator here generates statistically realistic events so the globe always has
data to show (and doubles as the demo's offline fallback).
"""

from .simulator import AttackEvent, AttackSimulator

__all__ = ["AttackEvent", "AttackSimulator"]
