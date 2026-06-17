# Mirage — A Live Cyber-Deception Battlestation

> **CipherHacks 2026** · Theme: Cyber Security · Build window: 36–48h
> Working name: **Mirage** (alternatives: *FoolsGold*, *Looking Glass*)

## One-liner
We don't just watch hackers attack us — we **drown them in believable lies**. Mirage is a live world-map of real attackers hitting our honeypot, where everything they steal is **Honey-Encrypted fake data** they can never tell apart from the real thing.

## The hook (the problem)
Every server on the public internet is under constant **automated attack** — credential brute-force, scanning, botnets — starting within *minutes* of going online. Defenders usually just block attackers. Mirage flips it: instead of saying "no," we say "yes" — and hand them an ocean of perfectly plausible fake secrets. **Brute-force becomes useless, because the attacker can never tell a real hit from a fake.**

## What we're building
Two halves that reinforce each other:

1. **The Globe (the spectacle).** A real-time 3D globe showing *actual* attackers from around the world hitting our honeypot live — their location, the passwords they try, the commands they run.
2. **The Mirage (the brains).** The "vault" they're trying to crack is protected by **Honey Encryption**. Every wrong key decrypts to a *different, completely believable* fake (e.g. a valid-looking credit card that even passes the Luhn checksum). The attacker drowns in plausible fakes and cannot identify the real data — if there is any.

This is **active cyber-deception**, a real and respected branch of security.

## The demo (the 2 minutes that win)
1. Big screen: a 3D globe, arcs of real attacks pouring in live from across the planet. *"Everything you see is happening right now, to a server we put online days ago. We did nothing to invite them."*
2. A live counter ticking up; a leaderboard of the most common passwords attackers try (`admin/admin`, `root/123456`).
3. Zoom into one attacker — show the real credentials they tried and the commands they ran.
4. **The money shot:** *"When they finally break in and steal our database…"* → the loot is Honey-Encrypted → every decryption yields a different believable fake. *"They stole 10,000 credit cards. All fake. And they will never know which — if any — is real."*
5. **Hand it to the audience:** *"You try."* A peer brute-forces the vault → the screen floods with believable fake cards. (People vote for what they touched.)

## Why this wins (scoring: 60% judges + 40% peers)
- **Peer vote (40%) — instant, visceral, interactive.** A live world-map of real hackers + "come crack it yourself" is graspable in 5 seconds and hands-on. Peers reward spectacle they can touch, and this delivers.
- **Judge vote (60%) — real depth + novelty.** Honey Encryption is genuine cryptography research (Juels & Ristenpart, 2014); cyber-deception is a serious defense discipline; the attack data is *real*. Technically sophisticated judges (undergrad + PhD) will respect it.
- **Original.** It's a fusion nobody else will build — the globe gives Mirage its "wow," and Honey Encryption gives the attack-map real novelty. Each half fixes the other's weakness.
- **On-theme.** It's literally about encryption and deception — perfect for *CipherHacks*.

## How it works (high level — no code)
```
Real attackers (worldwide) ─► Honeypot on a public VPS ─► attack logs
        └─► add geolocation ─► stream live ─► the Globe

The honeypot's "vault" ─► protected by Honey Encryption ─►
        any password (right or wrong) decrypts to a believable fake
```
- **Honeypot:** a decoy server exposed on the public internet that records every attacker's IP, credentials, and actions.
- **Globe:** a 3D world map that animates each attack in real time.
- **Honey Encryption:** the core trick — a special encoder guarantees every decryption key produces a valid-looking result, so brute-force yields only plausible fakes.

## Tech stack
- **Honeypot:** Cowrie (SSH/Telnet) on a cheap public VPS — deployed *days early* to collect real attack data.
- **Backend:** Python (FastAPI) — parse logs, add geolocation (MaxMind GeoLite2), stream to the frontend over WebSocket.
- **Frontend:** React + react-globe.gl (three.js) — the live globe, counters, leaderboards, and the interactive "Vault" panel.
- **Honey Encryption:** Python module (start with the credit-card domain; realistic passwords as a stretch).
- **Deploy:** frontend on Vercel; backend + honeypot on the VPS.

## 48-hour plan
| Phase | Focus |
|---|---|
| Before the event | Deploy the honeypot on a VPS so real attack data accumulates |
| 0–4h | Lock scope, scaffold repo, define the data format + demo storyboard |
| 4–12h | Honeypot log → geolocation → live stream ‖ Globe renders live points/arcs |
| 12–24h | Honey Encryption module + interactive "crack the vault" panel; first end-to-end demo |
| 24–36h | Polish visuals (globe, leaderboards, vault), connect honeypot ↔ vault, deploy |
| 36–44h | Stretch: AI explains attacker intent / session replay; otherwise harden + rehearse |
| 44–48h | Rehearse the demo 3×, build a 1-page slide, prep Q&A |

## Suggested roles
- **Infra / Data:** VPS + honeypot + log parsing + geolocation + live stream
- **Frontend:** the globe, counters, leaderboards, vault UI
- **Crypto:** Honey Encryption + Distribution-Transforming Encoder + the interactive brute-force demo

*(Scale up/down by team size; integrate on day 2.)*

## Risks & mitigations
- **Will real attackers actually show up?** Yes — overwhelmingly. Any exposed SSH/Telnet server gets brute-forced within minutes and thousands of times a day. *Mitigation:* deploy days early; keep a replay of captured data as a live fallback.
- **The "fake data" payoff must be reliable, not left to a random bot.** *Mitigation:* the honeypot serves the Honey-Encrypted "loot" by design, and the peer-interactive "you crack it" moment demonstrates the payoff on demand.
- **Two subsystems to integrate.** *Mitigation:* build the globe/honeypot and the Honey Encryption tracks independently; connect them at the "vault" boundary on day 2.
- **Safety / legal.** We only passively receive unsolicited attacks (legal); we never strike back. The honeypot runs on an isolated, firewalled VPS so it can't be used as a pivot.

## Alternative considered: "Cloak"
An adversarial-patch *invisibility cloak* — a printed pattern that makes a person vanish from an AI security camera (YOLO) live on webcam. Higher peak "wow," but a **high-variance live demo**: sensitive to lighting / print / angle, needs a GPU to train, and if it flickers or fails in front of the room, *both* the judge and peer scores collapse. We lean **Mirage** because it has a much higher floor (guaranteed real data, scripted + interactive payoff), is more original, and fits the *CipherHacks* theme better. Cloak stays as a backup if we have a strong ML member, a GPU, and time to harden it.

## Idea pool (for reference)
- **GhostText** — hide ciphertext inside natural, AI-written text (LLM steganography).
- **TrojanSign** — a small sticker that flips a traffic-sign classifier (STOP → Speed-80).
- **AirGap** — exfiltrate data from an offline computer (screen brightness / acoustics).
- **TrafficGhost** — fingerprint what a person is watching over encrypted traffic.
- **DolphinCmd** — inaudible voice commands to a phone / assistant.
- **Deniable** — deniable encryption: a decoy password reveals fake data; the real data's existence can't be proven.
